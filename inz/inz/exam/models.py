from django.utils import timezone
import pytz
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe


class User(AbstractUser):
    #wybór użytkownika (uczen/nauczyciel)
    is_student = models.BooleanField(default = False)
    is_teacher = models.BooleanField(default = False)


class Subject(models.Model):
    #temat testu
    name = models.CharField(max_length=30)
    color = models.CharField(max_length=7, default='#7bff00')

    def __str__(self):
        return self.name

    def get_html_badge(self):
        name = escape(self.name)
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (color, name)
        return mark_safe(html)

class Quiz(models.Model):
    TIMES_CHOICES = (
    (15, '15 minut'),
    (30, '30 minut'),
    (60, '1 godzina'),
    )
    #poszczególny test dla konkretnego użytkownika

    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'quizzes')
    name = models.CharField('Nazwa', max_length=100)
    date_access = models.DateTimeField('Data dostępu (RRRR-MM-DD HH:MM:SS)',default= timezone.now)
    date_access_end = models.DateTimeField('Data zakończenia (RRRR-MM-DD HH:MM:SS)',default= timezone.now() + timezone.timedelta(days=7))
    time_access = models.IntegerField('Dostępny przez', choices=TIMES_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name = 'quizzes', verbose_name='Przedmiot')

    def __str__(self):
        return self.name

class Question(models.Model):
    #tworzenie pytan
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name = 'questions')
    text = models.CharField(max_length = 100)

    def __str__(self):
        return self.text

class Answer(models.Model):
    #odpowiedzi
    question = models.ForeignKey(Question, on_delete = models.CASCADE, related_name = 'answers')
    text = models.CharField(max_length = 100)
    #zaznaczenie poprawnej odpowiedzi
    is_correct = models.BooleanField(default =False)

    def __str__(self):
        return self.text



class Student(models.Model):
    #uczen
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True)
    quizzes = models.ManyToManyField(Quiz,through='TakenQuiz')
    interests = models.ManyToManyField(Subject, related_name = 'interested_students')

    #wynik użytkownika
    score = models.IntegerField(default=0)

    #funkcja pobierajace nieodpowiedziane pytania z bazy danych
    def get_unanswered_question(self, quiz):
        answered_questions = self.quiz_answers \
            .filter(answer__question__quiz=quiz) \
            .values_list('answer__question__pk', flat=True)
        questions = quiz.questions.exclude(pk__in=answered_questions).order_by('text')
        return questions

    def __str__(self):
        return self.user.username



class TakenQuiz(models.Model):
    #rozwiazane quizy
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='taken_quizzes')
    score = models.IntegerField()
    percentage = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

class StudentAnswer(models.Model):
    #odpowiedzi studenta
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_answers')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='plus')
