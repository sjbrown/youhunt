#! /usr/bin/env python2.7

import json
import random
import datetime
import functools

from django.db import models
from django.utils import timezone
from django_extensions.db.fields import CreationDateTimeField
from django.db.models.signals import post_init, pre_save

from api.lazyjason import LazyJason, post_init_for_lazies, pre_save_for_lazies

def younger_than_one_day_ago(model_obj):
    #age = datetime.datetime.now(timezone.utc) - model_obj._created
    age = datetime.datetime.now() - model_obj._created
    return age < datetime.timedelta(days=1)

class NotAllowed(Exception):
    def __nonzero__(self):
        return False

def allower(fn):
    """
    Allower functions either raise NotAllowed or don't.  If they don't
    raise a NotAllowed exception, they will forcibly return True
    """
    RAISE = object() # Sentinel value
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        fail = kwargs.pop('on_fail', RAISE)
        try:
            result = fn(*args, **kwargs)
        except NotAllowed as e:
            if fail != RAISE:
                print e
                fn.__allower_result = e
                return fail
            else:
                raise
        else:
            if result is not None:
                raise Exception("Improper use of @allower")
            return True
    return wrapper

class Game(models.Model, LazyJason):
    name = models.CharField(max_length=1024)
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = dict(
        creator = None,
        started = False,
        invites = [],
    )

    def __unicode__(self):
        return self.name

    def new_charactor(self, player):
        c = Charactor(game=self, player=player)
        c.save()

    def to_dict(self):
        return super(Game, self).to_dict('name')

    def game_over(self):
        #TODO: clean up all cruft like old missions, etc
        #      ideally only Event objects will remain
        pass

    # API ----------------------------------------------

    @classmethod
    def create_new_game(cls, name, creator):
        cls.create_new_game_allowed(name, creator)

        newgame = cls(name=name)
        newgame.lazy_set(creator=creator.id)
        newgame.save()
        newgame.new_charactor(creator)
        return newgame

    @classmethod
    def create_new_game_allowed(cls, name, creator):
        #TODO: find the player that requested it, see if he has one pending

        # you can have duplicate names, so long as any dups have already
        # started.
        results = cls.objects.filter(name=name)
        for r in results:
            if not r.started:
                raise NotAllowed('create_new_game not allowed - another game with the same name is waiting to start')

    def start(self, requestor):
        self.start_allowed(requestor)

        self.lazy_set(started=True)
        for c in self.charactor_set.all():
            c.on_game_start(self)
        self.save()

    @allower
    def start_allowed(self, requestor):
        g_chars = self.charactor_set.all()
        if len(g_chars) < 6:
            raise NotAllowed('start not allowed - need more charactors')
        p_chars = requestor.charactor_set.all()
        if not set(p_chars).intersection(g_chars):
            raise NotAllowed('start not allowed - you are not in this game')

    def invite(self, requestor, invite_json):
        self.invite_allowed(requestor, invite_json)
        #TODO: maybe use F() here?
        self.lazy_set(invites=self.invites+[invite_json])
        self.save()

    @allower
    def invite_allowed(self, requestor, invite_json):
        try:
            json.loads(invite_json)
        except:
            raise NotAllowed('invite not allowed - invalid JSON')


class Player(models.Model, LazyJason):
    unique_name = models.CharField(max_length=1024)
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = dict(
        last_auth_token=None,
        last_auth_token_time=None,
    )

    def __unicode__(self):
        return self.unique_name


class MissionStunt(models.Model, LazyJason):
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = {'text':''}

    def __unicode__(self):
        return self.text


# -----------------------------------------------------------------------------
# Game - dependent models

class Event(models.Model, LazyJason):
    _created = CreationDateTimeField()
    game = models.ForeignKey(Game)
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = {'name':'generic event'}


class Charactor(models.Model, LazyJason):
    game = models.ForeignKey(Game)
    player = models.ForeignKey(Player)
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = dict(
        coin = 0,
        activity = 'choosing_mission',
        potential_missions = [],
    )

    def __unicode__(self):
        return self.name

    @property
    def name(self):
        return 'C-' + self.player.unique_name

    def on_game_start(self, game):
        self.lazy_set(coin=100)
        self.get_potential_missions(self_save=False)
        self.save()

    def get_potential_missions(self, self_save=True):
        if hasattr(self, 'potential_missions'):
            missions = self.potential_missions_Mission__objects
            print missions
            if missions and all(younger_than_one_day_ago(x) for x in missions):
                return missions
            # Old ones will garbage-collect on game_over

        missions = []
        stunt = self.choose_stunt()
        for prey in self.choose_potential_prey():
            award, bounties = self.current_award_and_bounties()
            m = Mission(game = self.game)
            m.lazy_set(
                stunt = str(stunt.id),
                hunter = str(self.id),
                prey = str(prey.id),
                award = award,
                bounties = [str(x.id) for x in bounties],
            )
            m.save()
            missions.append(m)
        self.lazy_set(potential_missions = [str(x.id) for x in missions])
        if self_save:
            self.save()

        return missions

    def choose_potential_prey(self):
        # TODO: make this smarter
        allcs = set(self.game.charactor_set.all())
        allcs.remove(self)
        return [allcs.pop(), allcs.pop()]

    def choose_stunt(self):
        # TODO: make this smarter
        return random.choice(MissionStunt.objects.all())

    def get_mission_obj(self):
        try:
            mission_id = self.mission
        except:
            return None
        mission = Mission.objects.get(id=mission_id)
        return mission.human_readable()

    def current_award_and_bounties(self):
        bounties = Bounty.objects.filter(target=self.id)
        # TODO: make award smarter to incentivize hunting rare prizes
        return 200, bounties

    # API ----------------------------------------------

    def accept_mission(self, requestor, accept_json):
        jdata = json.loads(accept_json)
        self.accept_allowed(requestor, jdata)

        m_id = jdata.get('mission')

        self.lazy_set(activity='hunting', mission=str(m_id),
                      potential_missions=[])
        self.save()

    @allower
    def accept_allowed(self, requestor, jdata):
        if requestor != self.player:
            raise NotAllowed('accept not allowed - player does not own char')
        if self.activity != 'choosing_mission':
            raise NotAllowed('accept not allowed - not choosing_mission')

        m_id = jdata.get('mission')
        try:
            m = Mission.objects.get(id=m_id)
        except:
            raise NotAllowed('accept not_allowed - mission has expired')
        if m not in self.get_potential_missions():
            raise NotAllowed('accept not_allowed - mission is not a potential')


class Mission(models.Model, LazyJason):
    _created = CreationDateTimeField()
    game = models.ForeignKey(Game)
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = dict(
        stunt = None,
        hunter = None,
        prey = None,
        award = 0,
        bounties = [],
    )

    def __unicode__(self):
        return "%s->%s (%s)" % (self.hunter, self.prey, self.stunt)

    def human_readable(self):
        prey_obj = Charactor.objects.get(id=self.prey)
        stunt_obj = MissionStunt.objects.get(id=self.stunt)
        return "%s %s" % (prey_obj.name, stunt_obj.text)

    def award_amounts(self):
        bounties = self.bounties_Bounty__objects
        additional = sum(b.coin for b in bounties)
        return (200, additional)



class Bounty(models.Model, LazyJason):
    game = models.ForeignKey(Game)
    target = models.ForeignKey(Charactor)
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = {'coin':0, 'poster':None}


class Award(models.Model, LazyJason):
    game = models.ForeignKey(Game)
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = {'coin':0, 'target':None}


class Submission(models.Model, LazyJason):
    # This is the pic
    game = models.ForeignKey(Game)
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = {
        'mission':None, 'pic_url':'', 'tips':{},
        'judges':[], 'winning_judge':None, 'judgement':None,
    }


for val in locals().values():
    if hasattr(val, '__bases__'):
        bases = val.__bases__
        if models.Model in bases and LazyJason in bases:
            post_init.connect(post_init_for_lazies, val)
            pre_save.connect(pre_save_for_lazies, val)
