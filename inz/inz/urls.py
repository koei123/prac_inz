"""inz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views

from inz.exam import views


urlpatterns = [
    path('',views.home, name='home'),
    path('students/', views.StudentQuizListView.as_view(), name='quiz_list'),
    path('students/interests/', views.StudentInterestsView.as_view(), name='student_interests'),
    path('students/quiz/<int:pk>/studentresults/', views.StudentQuizResultsView.as_view(), name='student_quiz_results'),
    path('students/taken/', views.TakenQuizListView.as_view(), name='taken_quiz_list'),
    path('students/quiz/<int:pk>/', views.take_quiz, name='take_quiz'),
    path('teachers/', views.TeacherQuizListView.as_view(), name='quiz_change_list'),
    path('teachers/quiz/add/', views.QuizCreateView.as_view(), name='quiz_add'),
    path('teachers/quiz/add_subject/', views.QuizSubjectCreateView.as_view(), name='quiz_add_subject'),
    path('teachers/quiz/<int:pk>/', views.QuizUpdateView.as_view(), name='quiz_change'),
    path('teachers/quiz/<int:pk>/delete/', views.QuizDeleteView.as_view(), name='quiz_delete'),
    path('teachers/quiz/<int:pk>/results/', views.QuizResultsView.as_view(), name='quiz_results'),
    path('teachers/quiz/<int:pk>/question/add/', views.question_add, name='question_add'),
    path('teachers/quiz/<int:quiz_pk>/question/<int:question_pk>/', views.question_change, name='question_change'),
    path('teachers/quiz/<int:quiz_pk>/question/<int:question_pk>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),
    path('accounts/login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('accounts/',include('django.contrib.auth.urls')),
    path('accounts/signup/',views.SignUpView.as_view(), name='signup'),
    #path('secret/',views.secret_page, name='secret'),
    #path('admin/', admin.site.urls),
    #path('accounts/signup/', classroom.SignUpView.as_view(), name='signup'),
    path('accounts/signup/student/', views.StudentSignUpView.as_view(), name='student_signup'),
    path('accounts/signup/teacher/', views.TeacherSignUpView.as_view(), name='teacher_signup'),
    ]
