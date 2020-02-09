# Generated by Django 3.0.1 on 2020-02-09 19:09

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0012_auto_20200204_1222'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='second_chance',
        ),
        migrations.RemoveField(
            model_name='quiz',
            name='time_access',
        ),
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_posts', to='exam.Subject', verbose_name='Kategoria'),
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(verbose_name='Treść'),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=200, unique=True, verbose_name='Temat'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='date_access_end',
            field=models.DateTimeField(default=datetime.datetime(2020, 2, 16, 19, 9, 3, 682328, tzinfo=utc), verbose_name='Data zakończenia (RRRR-MM-DD HH:MM:SS)'),
        ),
    ]
