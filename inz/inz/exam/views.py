from django.utils import timezone
import time
import pytz
from django.contrib.admin.widgets import AdminDateWidget
from datetime import datetime, timedelta
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count, Sum
from django.urls import reverse, reverse_lazy
from django.forms import inlineformset_factory
from django.utils.decorators import method_decorator
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (DetailView, DeleteView, CreateView, ListView, UpdateView)
from django.views import View
from django.views.generic import TemplateView

from .decorators import student_required, teacher_required
from .forms import (TeacherSignUpForm, StudentSignUpForm, StudentInterestsForm
, TakeQuizForm, QuestionForm, BaseAnswerInLineFormSet)

from .models import User, Quiz, Student, TakenQuiz, Question, Answer, Subject, Post

class test(CreateView):
    model = Quiz
    fields = ('name', 'date_access', )
    template_name = 'test.html'

    def get_form(self):
        form = super().get_form()
        form.fields['date_access'].widget =  forms.DateTimeInput(attrs={'type': 'AdminDateWidget'})
        return form




class SignUpView(TemplateView):
    template_name = 'registration/signup.html'

class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('quiz_list')

class TeacherSignUpView(CreateView):
    model = User
    form_class = TeacherSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('quiz_change_list')


def home(request):
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return redirect('quiz_change_list')
        else:
            return redirect('quiz_list')
    count = User.objects.count()
    return render(request, 'home.html',{
    'count':count,
    })

#views dla studenta
@method_decorator([login_required, student_required], name='dispatch')
class StudentInterestsView(UpdateView):
    """docstring for StudentInterestsView."""
    model = Student
    form_class = StudentInterestsForm
    template_name = 'interests_form.html'
    success_url = reverse_lazy('quiz_list')

    def get_object(self):
        return self.request.user.student

    def form_valid(self, form):
        messages.success(self.request, 'pomyślnie zaktualizowano zainteresowania!')
        return super().form_valid(form)

@method_decorator([login_required, student_required], name='dispatch')
class StudentQuizListView(ListView):
    """docstring for QuizListView."""
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'quiz_list.html'



    def get_queryset(self):
        student = self.request.user.student
        now = timezone.now()
        student_interests = student.interests.values_list('pk', flat=True)
        taken_quizzes = student.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.filter(subject__in=student_interests) \
            .exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0) \
            .filter(date_access__lt=now, date_access_end__gt=now)
        return queryset

@method_decorator([login_required, student_required], name='dispatch')
class StudentQuizResultsView(View):
    """docstring for QuizResultsView."""
    template_name = 'quiz_result_student.html'

    def get(self, request, *args, **kwargs):
        quiz = Quiz.objects.get(id = kwargs['pk'])
        taken_quiz = TakenQuiz.objects.filter(student = request.user.student, quiz = quiz)
        if not taken_quiz:
            return redirect('quiz_list')
        questions = Question.objects.filter(quiz = quiz)

        return render(request, self.template_name, {'questions':questions,
        'quiz':quiz, 'percentage': taken_quiz[0].percentage})

@method_decorator([login_required, student_required], name='dispatch')
class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.student.taken_quizzes \
            .select_related('quiz', 'quiz__subject') \
            .order_by('quiz__name')
        return queryset

@login_required
@student_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    student = request.user.student

    if student.quizzes.filter(pk=pk).exists():
        return render(request, 'taken_quiz.html')


    total_questions = quiz.questions.count()
    unanswered_questions = student.get_unanswered_question(quiz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()


    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                student_answer = form.save(commit=False)
                student_answer.student = student
                student_answer.save()

                if student.get_unanswered_question(quiz).exists():
                    return redirect('take_quiz', pk)
                else:
                    correct_answers = student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
                    percentage = round((correct_answers / (total_questions)) *100.0, 2)
                    TakenQuiz.objects.create(student=student, quiz=quiz, score=correct_answers, percentage=percentage)
                    student.save()
                    if percentage < 50.0:
                        messages.warning(request, 'Powodzenia następnym razem!, twój wynik egzaminu: %s był %s.' % (quiz.name, percentage))
                    else:
                        messages.success(request, 'Gratulacje!, Zdałeś egzamin: %s. Twój wynik to %s.' % (quiz.name, percentage))
                    return redirect('quiz_list')
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'take_quiz_form.html', {
    'quiz': quiz,
    'question': question,
    'form': form,
    'progress': progress,
    'answered_questions': total_questions - total_unanswered_questions,
    'total_questions': total_questions
    })



#views dla nauczyciela
@method_decorator([login_required, teacher_required], name='dispatch')
class TeacherQuizListView(ListView):
    """docstring for TeacherQuizListView."""
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'quiz_change_list.html'

    def get_queryset(self):
        queryset = self.request.user.quizzes \
            .select_related('subject') \
            .annotate(questions_count=Count('questions', distinct=True)) \
            .annotate(taken_count=Count('taken_quizzes', distinct=True))
        return queryset

@method_decorator([login_required, teacher_required], name='dispatch')
class QuizCreateView(CreateView):
    """docstring for QuizCreateView."""
    model = Quiz
    fields = ('name', 'subject', 'date_access', 'date_access_end'  )
    template_name = 'quiz_add_form.html'


    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.person = self.request.user
        quiz.save()
        messages.success(self.request, 'pomyślnie stworzono egzamin! dodaj pytania')
        return redirect('quiz_change', quiz.pk)

@method_decorator([login_required, teacher_required], name='dispatch')
class QuizUpdateView(UpdateView):
    model = Quiz
    fields = ('name', 'subject', )
    context_object_name = 'quiz'
    template_name = 'quiz_change_form.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()

    def get_success_url(self):
        return reverse('quiz_change', kwargs = {'pk': self.object.pk})

class QuizSubjectCreateView(CreateView):
    model = Subject
    fields = ('name', )
    template_name = 'quiz_add_subject.html'

    def form_valid(self, form):
        subject = form.save()
        messages.success(self.request, 'pomyślnie stworzono temat')
        return redirect('quiz_change_list')

@login_required
@teacher_required
def question_add(request,pk):
    quiz = get_object_or_404(Quiz, pk=pk, person=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'możesz dodać odpowiedzi/opcje do pytania')
            return redirect('question_change', quiz.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'question_add_form.html', {
                                                'quiz': quiz,
                                                'form': form })


@login_required
@teacher_required

def question_change(request, quiz_pk, question_pk):

    quiz = get_object_or_404(Quiz, pk=quiz_pk, person = request.user)
    question = get_object_or_404(Question, pk= question_pk, quiz=quiz)

    AnswerFormSet = inlineformset_factory(
        Question,  # rodzic model
        Answer,  # podstawowy model
        formset=BaseAnswerInLineFormSet,
        fields=('text', 'is_correct'),
        min_num=2,
        validate_min=True,
        max_num=10,
        validate_max=True
    )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, 'Pytanie i odpowiedz zapisano pomyślnie')
            return redirect('quiz_change', quiz.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

    return render(request, 'question_change_form.html', {
                                                        'quiz': quiz,
                                                        'question': question,
                                                        'form': form,
                                                        'formset': formset,
    })


@method_decorator([login_required, teacher_required], name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'question_delete.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['quiz'] = question.quiz
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'usunięto pytanie %s pomyślnie' % question.text)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(quiz__person=self.request.user)

    def get_success_url(self):
        question = self.get_object()
        return reverse('quiz_change', kwargs={'pk': question.quiz.id})

@method_decorator([login_required, teacher_required], name='dispatch')
class QuizResultsView(DetailView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'quiz_result_teacher.html'

    def get_context_data(self, **kwargs):
        quiz = self.get_object()
        taken_quizzes = quiz.taken_quizzes.select_related('student__user').order_by('-date')
        total_taken_quizzes = taken_quizzes.count()
        quiz_score = quiz.taken_quizzes.aggregate(average_score=Avg('score'))
        extra_context = {
            'taken_quizzes': taken_quizzes,
            'total_taken_quizzes': total_taken_quizzes,
            'quiz_score': quiz_score
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()



@method_decorator([login_required, teacher_required], name='dispatch')
class QuizDeleteView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'quiz_delete.html'
    success_url = reverse_lazy('quiz_change_list')

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(request, 'Egzamin %s został usunięty pomyślnie' % quiz.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


@method_decorator([login_required, teacher_required], name='dispatch')
class PostCreateView(CreateView):
    model = Post
    fields = ('title', 'category', 'content', )
    template_name = 'post_add_form.html'


    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        messages.success(self.request, 'pomyślnie stworzono post!')
        return redirect('post_list')

@method_decorator([login_required, teacher_required], name='dispatch')
class TeacherPostListView(ListView):
    """docstring for TeacherQuizListView."""
    model = Post
    ordering = ('title', )
    context_object_name = 'blog_posts'
    template_name = 'teacher_post.html'

    def get_queryset(self):
        queryset = self.request.user.blog_posts \
            .select_related('category')
        return queryset



@method_decorator([login_required, student_required], name='dispatch')
class StudentPostListView(ListView):
    model = Post
    ordering = ('title', )
    context_object_name = 'blog_posts'
    template_name = 'student_post_list.html'

    def get_queryset(self):
        student = self.request.user.student
        student_interests = student.interests.values_list('pk', flat=True)
        queryset = Post.objects.filter(category__in=student_interests)
        return queryset


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'post_detail.html'
