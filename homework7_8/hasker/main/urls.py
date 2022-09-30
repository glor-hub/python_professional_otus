from django.urls import path

from .views import QuestionCreateView, NewQuestionListView, HotQuestionListView, QuestionListView

app_name = 'main'

urlpatterns = [
    path('', NewQuestionListView.as_view(), name='index'),
    path('question/hot', HotQuestionListView.as_view(), name='question_list_hot'),
    # path('', index, name='index'),
    path('ask/', QuestionCreateView.as_view(), name='question_create'),
    # # path('question/new/', main.index, name='question_new'),
    # # path('question/hot', main.index, name='question_hot'),
    # path('question/detail/<slug:question_slug>', main.index, name='question_detail'),
    # # path('search/', main.index, name='search'),
    # # path('tag/<slug:tag_slug>', main.index, name='tag'),
]
