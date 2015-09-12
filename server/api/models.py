#! /usr/bin/env python2.7

import json
import random
import datetime
import functools

from django.db import models
from django.utils import timezone
from django_extensions.db.fields import CreationDateTimeField
from django.db.models.signals import post_init, pre_save, post_save

from api.lazyjason import LazyJason, post_init_for_lazies, pre_save_for_lazies, post_save_for_lazies

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
            print 'Not Allowed: ', e
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
        newgame.creator = str(creator.id)
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

        self.started = True
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

    def authorize_new_session(self, token):
        if self.last_auth_token == None:
            return False
        if str(token) == str(self.last_auth_token):
            return True
        else:
            return False

    def make_token(self):
        # TODO: make this smarter
        self.last_auth_token = str(random.randint(10000,99999))
        self.last_auth_token_time = datetime.datetime.now()


class MissionStunt(models.Model, LazyJason):
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = {'text':''}

    def __unicode__(self):
        if hasattr(self, 'text'):
            return self.text
        return 'NEW MISSION STUNT'


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
        c_name = 'C-?',
        coin = 0,
        activity = 'choosing_mission',
        potential_missions = [],
        notifications = [],
        current_prey_submissions = [],
        current_judge_submissions = [],
    )

    def __unicode__(self):
        return self.name

    @property
    def name(self):
        if hasattr(self, 'c_name'):
            return self.c_name
        return 'C-' + self.player.unique_name

    @property
    def submission(self):
        result = [
            s for s in self.game.submission_set.all()
            if (s.dismissed == False and s.stakeholders['hunter'] == self)
        ]
        if result:
            return result[0]
        return None

    @property
    def current_award(self):
        # TODO: make award smarter to incentivize hunting rare prizes
        return 200

    @property
    def current_bounties(self):
        bounties = Bounty.objects.filter(target=self.id)
        bounties = [b for b in bounties if not b.claimed]
        return bounties

    def on_game_start(self, game):
        self.coin = 100
        if self.c_name == self._lazy_defaults['c_name']:
            self.c_name = 'C-'+ self.player.unique_name
        self.get_potential_missions(self_save=False)
        self.save()

    def add_coin(self, amount):
        self.coin = self.coin + amount
        self.save()

    def remove_coin(self, amount):
        self.coin = self.coin - amount
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
            m = Mission(game = self.game)
            m.lazy_set(
                stunt = str(stunt.id),
                hunter = str(self.id),
                prey = str(prey.id),
                award = self.current_award,
            )
            m.save()
            missions.append(m)
        self.potential_missions = [str(x.id) for x in missions]
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

    def human_readable_mission(self):
        mission = self.mission_Mission__object
        return mission.human_readable()


    def notify_as_prey(self, submission):
        self.lazy_set(current_prey_submissions=
            self.current_prey_submissions + [str(submission.id)]
        )
        self.save()

    def notify_prey_finished(self, submission):
        self.current_prey_submissions.remove(str(submission.id))
        self.save()

    def notify_as_judge(self, submission):
        self.lazy_set(current_judge_submissions=
            self.current_judge_submissions + [str(submission.id)]
        )
        self.save()

    def notify_judge_finished(self, submission):
        self.current_judge_submissions.remove(str(submission.id))
        self.save()

    def notify_bounty_claimed(self):
        msg = 'One or more of the bounties you are hunting was claimed'
        print self, msg
        # TODO

    def notify_bounty_new(self, bounty):
        msg = 'A bounty was added to your mission'
        print self, msg
        # TODO

    def submission_finished(self, submission):
        self.activity = 'submission_finished'
        if submission.judgement == True:
            self.coin = self.coin + submission.hunter_pay
        self.save()

    def submission_dismissed(self, submission):
        if submission.judgement == True:
            self.activity = 'choosing_mission'
        if submission.judgement == False:
            self.activity = 'hunting'
        self.save()


    # API ----------------------------------------------

    def accept_mission(self, requestor, mission):
        print 'mission', mission
        print 'p ms', self.get_potential_missions(self_save=False)
        self.accept_allowed(requestor, mission)
        mission.accept()

        self.activity = 'hunting'
        self.mission = str(mission.id)
        self.potential_missions = []
        self.save()

    @allower
    def accept_allowed(self, requestor, mission):
        if requestor != self.player:
            raise NotAllowed('accept not allowed - player does not own char')
        if self.activity != 'choosing_mission':
            raise NotAllowed('accept not allowed - not choosing_mission')
        if mission not in self.get_potential_missions(self_save=False):
            raise NotAllowed('accept not_allowed - mission is not a potential')

    def submit_mission(self, requestor, photo_url):
        self.submit_allowed(requestor, photo_url)

        s = Submission(game = self.game)
        s.mission = str(self.mission)
        s.photo_url = photo_url
        s.start()

        self.activity = 'awaiting_judgement'
        self.save()

    @allower
    def submit_allowed(self, requestor, photo_url):
        if requestor != self.player:
            raise NotAllowed('submit not allowed - player does not own char')
        print 'ssact', self.activity
        if self.activity != 'hunting':
            raise NotAllowed('submit not allowed - not hunting')



class Mission(models.Model, LazyJason):
    _created = CreationDateTimeField()
    game = models.ForeignKey(Game)
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = dict(
        stunt = None,
        hunter = None,
        prey = None,
        award = 0,
        active = False,
    )

    def __unicode__(self):
        return "%s->%s (%s)" % (self.hunter, self.prey, self.stunt)

    def human_readable(self):
        prey_obj = Charactor.objects.get(id=self.prey)
        stunt_obj = MissionStunt.objects.get(id=self.stunt)
        return "%s %s" % (prey_obj.name, stunt_obj.text)

    def award_amounts(self):
        prey = self.prey_Charactor__object
        additional = sum(b.coin for b in prey.current_bounties)
        return (self.award, additional)

    def accept(self):
        self.active = True
        self.save()

    def complete(self):
        self.active = False
        self.save()


class Bounty(models.Model, LazyJason):
    game = models.ForeignKey(Game)
    target = models.ForeignKey(Charactor)
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = dict(
        claimed = False,
        coin = 0,
        poster = None,
    )

    @classmethod
    def get_bounty_hunters(cls, target):
        bounty_hunters = set()
        for m in [x for x in Mission.objects.all() if x.active]:
            if m.prey_Charactor__object == target:
                bounty_hunters.add(m.hunter_Charactor__object)
        return bounty_hunters

    @classmethod
    def notify_claimed(cls, claimed_bounties):
        assert len(set(b.target for b in claimed_bounties)) == 1
        target = claimed_bounties[0].target
        for hunter in cls.get_bounty_hunters(target):
            hunter.notify_bounty_claimed()

    def notify_new(self):
        for hunter in self.get_bounty_hunters(self.target):
            hunter.notify_bounty_new(self)

    def __unicode__(self):
        return "%s->%s (%s)" % (self.poster, self.target, self.coin)

    def claim(self):
        self.claimed = True
        self.save()


    # API ----------------------------------------------

    @classmethod
    def new_bounty(cls, requestor, poster, target, amount):
        cls.new_bounty_allowed(requestor, poster, target, amount)
        b = cls(game=poster.game, target=target)
        b.poster = poster
        b.coin = amount
        b.save()
        poster.remove_coin(amount)
        return b

    @classmethod
    @allower
    def new_bounty_allowed(cls, requestor, poster, target, amount):
        if requestor != poster.player:
            raise NotAllowed('not allowed - player does not own char')
        if poster.coin < amount:
            raise NotAllowed('not allowed - char does not have the coin')

        s = poster.submission
        peeps = s.stakeholders

        if (not s or s.judgement is None):
            raise NotAllowed('not allowed - no submission ready')
        if (poster not in
            [peeps['hunter'], peeps['prey']]):
            raise NotAllowed('not allowed - must be hunter or prey')
        if (s.judgement == True
            and poster == peeps['hunter']):
            raise NotAllowed('not allowed - hunter was favoured')
        if (s.judgement == False
            and poster == peeps['prey']):
            raise NotAllowed('not allowed - prey was favoured')
        if (target not in
            [peeps['hunter'], peeps['prey'], s.winning_judge_Charactor__object]
           ):
            raise NotAllowed('not allowed - not one of the potential targets')



class Award(models.Model, LazyJason):
    game = models.ForeignKey(Game)
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = {'coin':0, 'target':None}


class Submission(models.Model, LazyJason):
    # This is the pic
    game = models.ForeignKey(Game)
    db_attrs = models.CharField(default='{}', max_length=100*1024)
    _lazy_defaults = dict(
        mission = None,
        photo_url = '',
        tips = {'yes':0, 'no':0},
        judges = [],
        winning_judge = None,
        judgement = None,
        dismissed = False,
        eligible_bounties = [],
    )
    base_pay = {'yes': 0, 'no': 25}

    def __unicode__(self):
        return "%s %s (Mission %s)" % (self.id, self.judgement, self.mission)

    @property
    def stakeholders(self):
        s = {}
        m = self.mission_Mission__object
        s['prey'] = m.prey_Charactor__object
        s['hunter'] = m.hunter_Charactor__object
        for i, judge in enumerate(self.judges_Charactor__objects):
            s['j' + str(i)] = judge
        return s

    def role_of_charactor(self, c):
        if c == self.stakeholders['hunter']:
            return 'hunter'
        if c == self.stakeholders['prey']:
            return 'prey'
        if c in self.stakeholders.values():
            return 'judge'
        return 'spectator'

    @property
    def pay_yes(self):
        return self.base_pay['yes'] + self.tips['yes']

    @property
    def pay_no(self):
        return self.base_pay['no'] + self.tips['no']

    @property
    def hunter_pay(self):
        return self._hunter_pay

    def start(self):
        bounties = self.stakeholders['prey'].current_bounties
        self.eligible_bounties = [str(b.id) for b in bounties]
        self.choose_judges()
        self.save()
        self.notify_players_start()

    def finish(self, winning_judge_obj, judgement):
        self.winning_judge = str(winning_judge_obj.id)
        self.judgement = judgement
        self.save()

        if judgement == True:
            winning_judge_obj.add_coin(self.pay_yes)
            self.mission_Mission__object.complete()
            claimed_bounties = []
            for b in self.eligible_bounties_Bounty__objects:
                if not b.claimed:
                    b.claim()
                    claimed_bounties.append(b)
            Bounty.notify_claimed(claimed_bounties)
            self._hunter_pay = (self.mission_Mission__object.award
                                + sum([b.coin for b in claimed_bounties]))
        else:
            winning_judge_obj.add_coin(self.pay_no)

        self.stakeholders['hunter'].submission_finished(self)
        self.notify_players_finish()

    def choose_judges(self):
        # TODO: make this smarter
        allcs = set(self.game.charactor_set.all())
        m = self.mission_Mission__object
        allcs.remove(m.hunter_Charactor__object)
        allcs.remove(m.prey_Charactor__object)
        self.judges = [allcs.pop(), allcs.pop()]

    def notify_players_start(self):
        self.stakeholders['prey'].notify_as_prey(self)
        for judge in self.judges_Charactor__objects:
            judge.notify_as_judge(self)

    def notify_players_finish(self):
        self.stakeholders['prey'].notify_prey_finished(self)
        for judge in self.judges_Charactor__objects:
            judge.notify_judge_finished(self)

    def notify_players_tip_change(self):
        for c in self.stakeholders.values():
            c.notify_tip_change(self)

    # API ----------------------------------------------

    def judge(self, requestor, charactor, judgement):
        self.judge_allowed(requestor, charactor)
        self.finish(charactor, judgement)

    @allower
    def judge_allowed(self, requestor, charactor):
        if requestor != charactor.player:
            raise NotAllowed('not allowed - player does not own char')
        if charactor not in self.judges_Charactor__objects:
            raise NotAllowed('not allowed - char is not a judge')

    def dismiss(self, requestor, charactor):
        self.dismiss_allowed(requestor, charactor)
        self.dismissed = True
        self.save()
        charactor.submission_dismissed(self)

    @allower
    def dismiss_allowed(self, requestor, charactor):
        if requestor != charactor.player:
            raise NotAllowed('not allowed - player does not own char')
        if self.judgement is None:
            raise NotAllowed('not allowed - submission has not been judged')
        if charactor != self.stakeholders['hunter']:
            raise NotAllowed('not allowed - hunter only may dismiss')



for val in locals().values():
    if hasattr(val, '__bases__'):
        bases = val.__bases__
        if models.Model in bases and LazyJason in bases:
            post_init.connect(post_init_for_lazies, val)
            pre_save.connect(pre_save_for_lazies, val)
            post_save.connect(post_save_for_lazies, val)



def scenario_1(delete=False):
    def O(cls, d1, d2):
        o = cls(**d1)
        for key,val in d2.items():
            if hasattr(val, 'id'):
                val = val.id
            setattr(o, key, val)
        o.save()
        return o

    def D(cls, d1, d2):
        o = cls.objects.get(**d1)
        o.delete()

    if delete:
        O = D

    p1 = O(Player, dict(unique_name='s1-Shandy'), dict(last_auth_token = '123'))
    p2 = O(Player, dict(unique_name='s1-Luna'), dict(last_auth_token = '123'))
    g = O(Game, dict(name='Sc1'), dict(creator=p1))
    c1 = O(Charactor, dict(game=g, player=p1), dict(
            c_name='C-Shandy', coin=100))
    c2 = O(Charactor, dict(game=g, player=p1), dict(
            c_name='C-Jared', coin=100))
    c3 = O(Charactor, dict(game=g, player=p1), dict(
            c_name='C-Alex', coin=100))
    c4 = O(Charactor, dict(game=g, player=p2), dict(
            c_name='C-Luna', coin=100))
    c5 = O(Charactor, dict(game=g, player=p2), dict(
            c_name='C-Kim', coin=100))
    c6 = O(Charactor, dict(game=g, player=p2), dict(
            c_name='C-Kristy', coin=100))

    g.start(p1)

    m = c1.get_potential_missions(self_save=False)[0]
    c1.accept_mission(p1, m)
    prey = m.prey_Charactor__object

    print c1, 'is now hunting', prey
    print 'activity', c1.activity

    c1.submit_mission(p1, 'http://i.imgur.com/L8GlJ3A.gif')

