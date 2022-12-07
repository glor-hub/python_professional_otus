from django.conf.urls import url
from rest_framework import routers
from core.views import AnswerViewSet, QuestionViewSet

app_name = 'main-api'

router = routers.DefaultRouter()
router.register(r'answers', AnswerViewSet)
router.register(r'questions', QuestionViewSet)

urlpatterns = router.urls
