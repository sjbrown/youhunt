from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^new_game/(?P<name>[^/]+)/?$',
        views.new_game , name='new game'),
    url(r'^game/(?P<game_id>[^/]+)/?$',
        views.game , name='game'),
    url(r'^game/(?P<game_id>[^/]+)/start?$',
        views.game_start , name='game start'),

    url(r'^player/(?P<player_id>[^/]+)/?$',
        views.player, name='player'),

    url(r'^charactor/(?P<charactor_id>[^/]+)/?$',
        views.charactor, name='charactor'),
]

