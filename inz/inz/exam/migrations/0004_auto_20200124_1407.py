# Generated by Django 3.0.1 on 2020-01-24 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0003_quiz_date_access'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='date_access',
        ),
        migrations.AddField(
            model_name='quiz',
            name='cos',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
