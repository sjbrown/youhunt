# client.views

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import RequestContext, loader

from api.models import *

def index(request):
    g = get_object_or_404(Game, pk=1)
    return render(request, 'client/index.html', {
        'g': g,
    })

def authorize(request, player_id, token):
    p = get_object_or_404(Player, pk=player_id)
    if str(p.last_auth_token) != token:
        request.session['player_id'] = None
        return HttpResponse('Wrong auth')
    else:
        request.session['player_id'] = p.id
        return HttpResponse('Logged in')

def player(request, player_id):
    session_pid = request.session.get('player_id')
    if request.session.get('player_id') != int(player_id):
        return HttpResponse('Wrong auth')
    p = get_object_or_404(Player, pk=session_pid)
    return render(request, 'client/player.html', {
        'p': p,
        'template_choosing_mission': 'client/choosing_mission.html',
    })

def charactor(request, charactor_id):
    session_pid = request.session.get('player_id')
    p = get_object_or_404(Player, pk=session_pid)
    results = [c for c in p.charactor_set.all()
               if c.id == int(charactor_id)]
    if not results:
        raise Http404("Charactor not found in Player %s's list" % session_pid)
    c = results[0]
    return render(request, 'client/charactor.html', {
        'c': c,
        'template_choosing_mission': 'client/choosing_mission.html',
    })




