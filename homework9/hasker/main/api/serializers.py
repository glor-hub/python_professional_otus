from rest_framework import serializers
from main.models import Answer,Question


class AnswerSerializer(serializers.ModelSerializer):

    user=serializers.CharField(source='user.username')
    question = serializers.CharField(source='question.title')

    class Meta:
        model = Answer
        # fields=[
        #     'body',
        #     'create_at',
        #     'votes_total',
        # 'rating',
        # 'votes_like',
        # 'votes_dislike',
        # 'is_favorite',
        # 'user',
        # 'question']
        fields='__all__'

class QuestionSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username')

    class Meta:
        model = Question
        fields='__all__'
