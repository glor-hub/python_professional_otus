# Generated by Django 3.2.13 on 2022-10-04 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_question_tags_string_alter_question_tags_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='slug',
            field=models.SlugField(max_length=256, unique=True),
        ),
    ]
