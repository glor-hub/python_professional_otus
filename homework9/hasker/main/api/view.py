# from rest_framework import viewsets
from main.models import Answer, Question
from .serializers import AnswerSerializer, QuestionSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

class AnswerMixin(object):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

class AnswerList(AnswerMixin, ListCreateAPIView):
    pass


class AnswerDetail(AnswerMixin, RetrieveUpdateDestroyAPIView):
    pass

class QuestionMixin(object):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class QuestionList(QuestionMixin, ListCreateAPIView):
    pass


class QuestionDetail(QuestionMixin, RetrieveUpdateDestroyAPIView):
    pass

# class QuestionViewSet(viewsets.ModelViewSet):
#     queryset = Question.objects.all()
#     serializer_class = QuestionSerializer
#
# class AnswerViewSet(viewsets.ModelViewSet):
#     queryset = Answer.objects.all()
#     serializer_class = AnswerSerializer