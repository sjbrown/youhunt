from django.contrib import admin

from .models import *

admin.site.register(Player)
admin.site.register(MissionStunt)
admin.site.register(Mission)
admin.site.register(Bounty)

class CharactorInline(admin.TabularInline):
    model = Charactor
    extra = 0

class GameAdmin(admin.ModelAdmin):
    inlines = [CharactorInline]
    search_fields = ['name']

admin.site.register(Game, GameAdmin)
