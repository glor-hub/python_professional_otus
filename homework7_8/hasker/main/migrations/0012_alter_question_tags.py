# Generated by Django 3.2.13 on 2022-10-06 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_rename_is_correct_answer_is_favorite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='tags',
            field=models.ManyToManyField(related_name='tags', to='main.Tag'),
        ),
    ]