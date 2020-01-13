from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError

from .models import (Answer, Question, Student, User, Subject, StudentAnswer)

class StudentSignUpForm(UserCreationForm):
    #interests = forms.ModelMultipleChoiceField(
    #    queryset=Subject.objects.all(),
    #    widget=forms.CheckboxSelectMultiple,
    #    required=True
    #)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.save()
        student = Student.objects.create(user=user)
        #student.interests.add(*self.cleaned_data.get('interests'))
        return user

class TeacherSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        if commit:
            user.save()
        return user


#forms dla Studenta
class StudentInterestsForm(forms.ModelForm):
    """docstring forStudentInterestForm."""

    class Meta:
        model = Student
        fields = ('interests',)
        widget = {
        'interests':forms.CheckboxSelectMultiple
        }


class TakeQuizForm(forms.ModelForm):
    """docstring for TakeQuizForm."""
    answer = forms.ModelChoiceField(
    queryset = Answer.objects.none(),
    widget = forms.RadioSelect(),
    required = True,
    empty_label = None
    )

    class Meta:
        model = StudentAnswer
        fields = ('answer', )

    def __init__(self, *arg, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.answers.order_by('text')
