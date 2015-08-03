from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^s/(?P<player_id>[^/]+)/auth/(?P<token>[^/]+)/?$',
    views.authorize, name='auth'),
    url(r'^s/(?P<player_id>[^/]+)/?$',
    views.player, name='player'),

    url(r'^s/charactor/(?P<charactor_id>[^/]+)/?$',
    views.charactor, name='charactor'),
]

