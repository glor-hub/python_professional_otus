from rest_framework import serializers
from main.models import Answer,Question


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields='__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields='__all__'
