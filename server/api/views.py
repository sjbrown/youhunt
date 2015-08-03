# api.views

import json
from cgi import escape as html_esc
from functools import partial

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST

from .forms import InviteForm

class Http400(APIException):
    status_code = HTTP_400_BAD_REQUEST

from api.models import *

def index(request):
    from api.urls import urlpatterns
    s = '<h1>API Listing</h1>\n'
    s += '\n'.join(['<li>%s</li>' % html_esc(str(x)) for x in urlpatterns])
    #TODO: SECURITY: get rid of this session part
    s += '\n<hr>Your session: "%s"' % request.session.items()
    return HttpResponse(s)

def new_game(request, name):
    p = Player.objects.get(pk=request.session.get('player_id'))
    try:
        g = Game.create_new_game(name=name, creator=p)
    except NotAllowed as e:
        raise Http400(detail=e.message)
    return JsonResponse(dict(game_id=g.id, status='happy jazz'))

def game(request, game_id):
    try:
        g = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        raise Http404('Could not find game')
    j = g.to_dict()
    return JsonResponse(j)

def game_start(request, game_id):
    p = Player.objects.get(pk=request.session.get('player_id'))
    g = get_object_or_404(Game, pk=int(game_id))
    try:
        g.start(requestor=p)
    except NotAllowed as e:
        raise Http400(detail=e.message)
    j = g.to_dict()
    return JsonResponse(j)

def game_invite(request, game_id):
    print 'got POST', request.POST
    p = Player.objects.get(pk=request.session.get('player_id'))
    g = get_object_or_404(Game, pk=int(game_id))
    form = InviteForm(request.POST)
    if not form.is_valid():
        raise Http400(detail="Invalid invite")
    try:
        g.invite(requestor=p, invite_json=form.cleaned_data['invite_json'])
    except NotAllowed as e:
        raise Http400(detail=e.message)
    j = g.to_dict()
    return JsonResponse(j)


def player(request, player_id):
    return HttpResponse('player ID %s' % player_id)

def charactor(request, charactor_id):
    return HttpResponse('charactor ID %s' % charactor_id)
