from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Sum
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, ListView, UpdateView
from django.views import View
from django.views.generic import TemplateView

from .decorators import student_required
from .forms import TeacherSignUpForm, StudentSignUpForm, StudentInterestsForm, TakeQuizForm
from .models import User, Quiz, Student, TakenQuiz, Question


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
class QuizListView(ListView):
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
