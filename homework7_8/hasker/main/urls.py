from django.urls import path

from .views import index, QuestionCreateView

app_name = 'main'

urlpatterns = [
    path('', index, name='index'),
    path('ask/', QuestionCreateView.as_view(), name='ask'),
    # path('question/new/', main.index, name='question_new'),
    # path('question/hot', main.index, name='question_hot'),
    # path('question/detail/<slug:question_slug>', main.index, name='question_detail'),
    # path('search/', main.index, name='search'),
    # path('tag/<slug:tag_slug>', main.index, name='tag'),
]
