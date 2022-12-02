from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

import accounts.views as accounts

app_name = 'accounts'

urlpatterns = [
    path('signup/', accounts.AccountCreateView.as_view(), name='signup'),
    path('profile/<int:pk>/', accounts.AccountUpdateView.as_view(), name='profile'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
