# api.views

import json
import inspect
from cgi import escape as html_esc
from functools import partial, wraps

from django import forms
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST

from .forms import InviteForm, AcceptMissionForm, SubmitMissionForm

class Http400(APIException):
    status_code = HTTP_400_BAD_REQUEST

from api.models import *

def kwargs_from_json(jdata):
    try:
        print 'Trying to loads the jdata', jdata
        json_data = json.loads(jdata)
    except Exception as e:
        print 'JSON PARSE FAIL', e
        raise forms.ValidationError("Invalid JSON data in %s" % jdata)
    assert type(json_data) == dict
    return json_data

def standard_charactor_view(fn):
    @wraps(fn)
    def wrapper(request, charactor_id):
        print request.POST
        json_key = [k for k in request.POST.keys()
                    if k.endswith('_json')][0]
        p = from_session(request)
        c = get_object_or_404(Charactor, pk=int(charactor_id))
        kwargs = kwargs_from_json(request.POST[json_key])
        print 'kwargs', kwargs
        ret_dict = fn(request, p, c, **kwargs)
        return JsonResponse(ret_dict)
    return wrapper

def from_session(request, arg_name='player_id', *args, **kwargs):
    return Player.objects.get(pk=request.session.get('player_id'))

def from_path(request, arg_name, *args, **kwargs):
    if type(arg_name) == int:
        return args[arg_name]
    return kwargs[arg_name]

def from_json(request, arg_name, *args, **kwargs):
    print request.POST
    json_keys = [k for k in request.POST.keys()
                 if k.endswith('_json')]
    assert len(json_keys) == 1
    json_key = json_keys[0]
    jdict = kwargs_from_json(request.POST[json_key])
    return jdict[arg_name]

def index(request):
    from api.urls import urlpatterns
    s = '<h1>API Listing</h1>\n'
    s += '\n'.join(['<li>%s</li>' % html_esc(str(x)) for x in urlpatterns])
    #TODO: SECURITY: get rid of this session part
    s += '\n<hr>Your session: "%s"' % request.session.items()
    return HttpResponse(s)

def player(request, player_id):
    return HttpResponse('player ID %s' % player_id)

def charactor(request, charactor_id):
    return HttpResponse('charactor ID %s' % charactor_id)

def game(request, game_id):
    try:
        g = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        raise Http404('Could not find game')
    j = g.to_dict()
    return JsonResponse(j)

def new_game(request, name):
    p = from_session(request)
    try:
        g = Game.create_new_game(name=name, creator=p)
    except NotAllowed as e:
        raise Http400(detail=e.message)
    return JsonResponse(dict(game_id=g.id, status='happy jazz'))

def game_start(request, game_id):
    p = from_session(request)
    g = get_object_or_404(Game, pk=int(game_id))
    try:
        g.start(requestor=p)
    except NotAllowed as e:
        raise Http400(detail=e.message)
    j = g.to_dict()
    return JsonResponse(j)

def game_invite(request, game_id):
    p = from_session(request)
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


@standard_charactor_view
def charactor_accept(request, p, c, mission_id=None):
    c.accept_mission(p, mission_id)
    return {'success':True}

@standard_charactor_view
def charactor_submit(request, p, c, photo_url=None):
    c.submit_mission(p, photo_url)
    return {'success':True, 'submission':c.submission}

class Make(object):
    class_mapper = dict(
        game = Game,
        player = Player,
        charactor = Charactor,
        mission = Mission,
        submission = Submission,
    )

    @staticmethod
    def a_bool(from_fn, field_name=None):
        def bool_wrapper(request, argname, *fn_args, **fn_kwargs):
            if field_name is not None:
                argname = field_name
            val = from_fn(request, argname, *fn_args, **fn_kwargs)
            val = bool(val)
            return val
        return bool_wrapper

    @classmethod
    def an_obj(cls, from_fn, field_name=None):
        def an_obj_wrapper(request, argname, *fn_args, **fn_kwargs):
            if field_name is not None:
                argname = field_name
            else:
                argname += '_id'
            print 'Making ', argname
            id_val = from_fn(request, argname, *fn_args, **fn_kwargs)
            if argname.endswith('_id'):
                cls_name = argname[:-3]
            else:
                cls_name = argname
            obj_class = cls.class_mapper[cls_name]
            obj = get_object_or_404(obj_class, pk=int(id_val))
            return obj
        return an_obj_wrapper

    @staticmethod
    def args(fn):
        argspec = inspect.getargspec(fn)
        # argspec should be request, and then kwargs
        assert len(argspec.args) - 1 == len(argspec.defaults)
        fn_kwargs_names = argspec.args[1:]

        @wraps(fn)
        def wrapper(request, *w_args, **w_kwargs):
            #print 'fn-args', w_args
            #print 'w_kwargs', w_kwargs
            fn_kwargs = {}
            for i, argname in enumerate(fn_kwargs_names):
                val_maker = argspec.defaults[i]
                print argname, val_maker
                fn_kwargs[argname] = val_maker(request, argname,
                                               *w_args, **w_kwargs)

            ret_dict = fn(request, **fn_kwargs)
            return JsonResponse(ret_dict)
        return wrapper

@Make.args
def submission_judgement(
    request,
    p = from_session,
    charactor = Make.an_obj(from_json),
    submission = Make.an_obj(from_path),
    judgement = Make.a_bool(from_json),
):
    print 'p', p
    print 'c', charactor
    print 's', submission
    print 'judgement', judgement
    print request.POST
    submission.judge(p, charactor, judgement)
    return {'success':True, 'submission':submission.id}


