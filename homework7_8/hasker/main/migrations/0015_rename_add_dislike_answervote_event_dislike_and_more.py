# Generated by Django 4.1.1 on 2022-10-07 01:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_alter_answer_body'),
    ]

    operations = [
        migrations.RenameField(
            model_name='answervote',
            old_name='add_dislike',
            new_name='event_dislike',
        ),
        migrations.RenameField(
            model_name='answervote',
            old_name='add_like',
            new_name='event_like',
        ),
        migrations.RenameField(
            model_name='questionvote',
            old_name='add_dislike',
            new_name='event_dislike',
        ),
        migrations.RenameField(
            model_name='questionvote',
            old_name='add_like',
            new_name='event_like',
        ),
    ]