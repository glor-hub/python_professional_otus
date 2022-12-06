from django.urls import path

from .views import QuestionCreateView, NewQuestionListView, HotQuestionListView, QuestionDetailView, QuestionView, \
    QuestionSearchListView

app_name = 'main'

urlpatterns = [
    path('', NewQuestionListView.as_view(), name='index'),
    path('question/hot', HotQuestionListView.as_view(), name='question_list_hot'),
    path('ask/', QuestionCreateView.as_view(), name='question_create'),
    path('question/<slug:question_slug>', QuestionView.as_view(), name='question_detail'),
    path('search/', QuestionSearchListView.as_view(),name='question_search_list_view'),
]
