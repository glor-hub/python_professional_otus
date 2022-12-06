from django.conf.urls import url

from main.api import views as main_views

urlpatterns = [
    url(
        path('main/', main_views.MainCreateReadView.as_view(),
        name='main'
    ),
    url(
        regex=r'^flavors/(?P<uuid>[-\w]+)/$',
        view=flavor_views.FlavorReadUpdateDeleteView.as_view(),
        name='flavors'
    ),
    # {% url 'api:users' %}
    url(
        regex=r'^users/$',
        view=user_views.UserCreateReadView.as_view(),
        name='users'
    ),
    # {% url 'api:users' user.uuid %}
    url(
        regex=r'^users/(?P<uuid>[-\w]+)/$',
        view=user_views.UserReadUpdateDeleteView.as_view(),
        name='users'
    ),
]
