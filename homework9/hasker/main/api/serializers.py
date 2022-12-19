from rest_framework import serializers
from main.models import Answer,Question


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question