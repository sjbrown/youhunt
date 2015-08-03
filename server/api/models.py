import json
from django.db import models
from django.db.models.signals import post_init, pre_save

from api.lazyjason import LazyJason, post_init_for_lazies, pre_save_for_lazies

class NotAllowed(Exception): pass

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

    @classmethod
    def create_new_game(cls, name, creator):
        cls.create_new_game_allowed(name, creator)

        newgame = cls(name=name)
        newgame.lazy_set(creator=creator.id)
        newgame.save()
        newgame.new_charactor(creator)
        return newgame

    def create_new_game_allowed(cls, name, creator):
        #TODO: find the player that requested it, see if he has one pending

        # you can have duplicate names, so long as any dups have already
        # started.
        results = cls.objects.filter(name=name)
        for r in results:
            if not r.started:
                raise NotAllowed('create_new_game not allowed - another game with the same name is waiting to start')

    def new_charactor(self, player):
        c = Charactor(game=self, player=player)
        c.save()

    def start(self, requestor):
        self.start_allowed(requestor)

        self.lazy_set(started=True)
        for c in self.charactor_set.all():
            c.on_game_start(self)

    def start_allowed(self, requestor):
        if len(self.invites) < 6:
            raise NotAllowed('start not allowed - need more invites')
        g_chars = self.charactor_set.all()
        if len(g_chars) < 6:
            raise NotAllowed('start not allowed - need more charactors')
        p_chars = requestor.charactor_set.all()
        if set(p_chars).intersection(g_chars):
            raise NotAllowed('start not allowed - you are not in this game')

    def to_dict(self):
        return super(Game, self).to_dict('name')


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
    time_created = models.DateTimeField()
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
        potential_prey = [],
    )

    def __unicode__(self):
        return 'C-' + self.player.unique_name

    def on_game_start(self, game):
        self.lazy_set(coin=100)
        self.lazy_set(potential_prey = self.choose_potential_prey())
        self.save()

    def choose_potential_prey(self):
        # TODO: make this smarter
        allcs = set(self.game.charactor_set.all())
        allcs.remove(self)
        print 'prey from', allcs
        return [allcs.pop().id, allcs.pop().id]


class Mission(models.Model, LazyJason):
    game = models.ForeignKey(Game)
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = {'stunt':None, 'hunter':None, 'prey':None}


class Bounty(models.Model, LazyJason):
    game = models.ForeignKey(Game)
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = {'coin':0, 'poster':None, 'target':None}


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
