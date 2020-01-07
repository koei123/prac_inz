#from django.shortcuts import render, redirect
#from django.contrib.auth.models import User
#from django.contrib.auth.forms import UserCreationForm
#from django.contrib.auth.decorators import login_required

from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views.generic import CreateView
from .forms import TeacherSignUpForm
from .forms import StudentSignUpForm
from .models import User
from django.views.generic import TemplateView

def home(request):
    count = User.objects.count()
    return render(request,'home.html',{
    'count':count,
    })
#
#
#def signup(request):
#    if request.method == ('POST'):
#        form = UserCreationForm(request.POST)
#        if form.is_valid():
#            form.save()
#            return redirect('home')
#    else:
#        form = UserCreationForm()
#    return render(request,'registration/signup.html',{
#        'form':form
#    })
#
#@login_required
#def secret_page(request):
#    return render(request,'secret_page.html')
#





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
        return redirect('home')

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
        return redirect('home')
