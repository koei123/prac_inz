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

from .models import User, Quiz, Student, TakenQuiz, Question, Answer, Subject


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
        messages.success(self, request, 'pomyślnie zaktualizowano zainteresowania!')
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
        student_interests = student.interests.values_list('pk', flat=True)
        taken_quizzes = student.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.filter(subject__in=student_interests) \
            .exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset

@method_decorator([login_required, student_required], name='dispatch')
class QuizResultsView(View):
    """docstring for QuizResultsView."""
    template_name = 'quiz_result.html'

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
    fields = ('name', 'subject', )
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
