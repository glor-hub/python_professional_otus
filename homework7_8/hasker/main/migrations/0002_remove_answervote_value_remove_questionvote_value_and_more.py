# Generated by Django 4.1.1 on 2022-09-26 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answervote',
            name='value',
        ),
        migrations.RemoveField(
            model_name='questionvote',
            name='value',
        ),
        migrations.AddField(
            model_name='answervote',
            name='add_dislike',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='answervote',
            name='add_like',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='answervote',
            name='status',
            field=models.CharField(choices=[('L', 'Like'), ('D', 'Dislike'), ('N', 'None')], default='N', max_length=1),
        ),
        migrations.AddField(
            model_name='question',
            name='votes_dislike',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='question',
            name='votes_like',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='question',
            name='votes_total',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='questionvote',
            name='add_dislike',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='questionvote',
            name='add_like',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='questionvote',
            name='status',
            field=models.CharField(choices=[('L', 'Like'), ('D', 'Dislike'), ('N', 'None')], default='N', max_length=1),
        ),
    ]