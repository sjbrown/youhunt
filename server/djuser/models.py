from random import randint

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from api.models import *

class PlayerConnector(models.Model):
    user = models.OneToOneField(User)
    player_id = models.CharField(default='', max_length=256)

    @property
    def player(self):
        try:
            return Player.objects.get(pk=self.player_id)
        except (ValueError, DoesNotExist):
            return None

def on_create(**kwargs):
    if kwargs.get('created') != True:
        return
    newu = kwargs.get('instance')
    newp = Player(unique_name=newu.username)
    newp.make_token() # this does the save()
    newpc = PlayerConnector(user=newu, player_id=newp.id)
    newpc.save()

post_save.connect(on_create, User)
