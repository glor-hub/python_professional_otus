from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

import siteauth.views as siteauth

app_name = 'siteauth'

urlpatterns = [
    path('signup/', siteauth.SiteUserCreateView.as_view(), name='signup'),
    path('settings/<int:pk>/', siteauth.SiteUserUpdateView.as_view(), name='settings'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
