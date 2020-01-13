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
    path('teachers/', views.TeacherQuizListView.as_view(), name='quiz_change_list'),
    path('accounts/login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('accounts/',include('django.contrib.auth.urls')),
    path('accounts/signup/',views.SignUpView.as_view(), name='signup'),
    #path('secret/',views.secret_page, name='secret'),
    #path('admin/', admin.site.urls),
    #path('accounts/signup/', classroom.SignUpView.as_view(), name='signup'),
    path('accounts/signup/student/', views.StudentSignUpView.as_view(), name='student_signup'),
    path('accounts/signup/teacher/', views.TeacherSignUpView.as_view(), name='teacher_signup'),
    ]
