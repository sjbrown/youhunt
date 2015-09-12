from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^s/(?P<player_id>[^/]+)/auth/(?P<token>[^/]+)/?$',
    views.authorize, name='auth'),
    url(r'^s/(?P<player_id>[^/]+)/?$',
    views.player, name='player'),

    url(r'^s/charactor/(?P<charactor_id>[^/]+)/?$',
    views.charactor, name='charactor'),

    url(r'^s/charactor/(?P<charactor_id>[^/]+)/submission/(?P<submission_id>[^/]+)/?$',
    views.charactor_submission, name='charactor_submission'),

    url('', include('django.contrib.auth.urls')),

]

