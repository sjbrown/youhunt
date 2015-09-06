from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^new_game/(?P<name>[^/]+)/?$',
        views.new_game , name='new game'),
    url(r'^game/(?P<game_id>[^/]+)/?$',
        views.game , name='game'),
    url(r'^game/(?P<game_id>[^/]+)/start/?$',
        views.game_start , name='game start'),
    url(r'^game/(?P<game_id>[^/]+)/invite/?$',
        views.game_invite, name='game invite'),

    url(r'^player/(?P<player_id>[^/]+)/?$',
        views.player, name='player'),

    url(r'^charactor/(?P<charactor_id>[^/]+)/?$',
        views.charactor, name='charactor'),
    url(r'^charactor/(?P<charactor_id>[^/]+)/accept/?$',
        views.charactor_accept, name='charactor accept'),
    url(r'^charactor/(?P<charactor_id>[^/]+)/submit/?$',
        views.charactor_submit, name='charactor submit'),

    url(r'^submission/(?P<submission_id>[^/]+)/judgement/?$',
        views.submission_judgement, name='submission judgement'),

]

