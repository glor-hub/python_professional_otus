from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

import siteauth.views as siteauth

app_name = 'siteauth'

urlpatterns = [
    path('register/',  siteauth.SiteUserCreateView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]