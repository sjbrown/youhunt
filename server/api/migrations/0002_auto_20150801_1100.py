# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='award',
            name='db_attrs',
            field=models.CharField(default=b'{}', max_length=102400),
        ),
        migrations.AlterField(
            model_name='bounty',
            name='db_attrs',
            field=models.CharField(default=b'{}', max_length=102400),
        ),
        migrations.AlterField(
            model_name='charactor',
            name='db_attrs',
            field=models.CharField(default=b'{}', max_length=102400),
        ),
        migrations.AlterField(
            model_name='event',
            name='db_attrs',
            field=models.CharField(default=b'{}', max_length=102400),
        ),
        migrations.AlterField(
            model_name='game',
            name='db_attrs',
            field=models.CharField(default=b'{}', max_length=102400),
        ),
        migrations.AlterField(
            model_name='mission',
            name='db_attrs',
            field=models.CharField(default=b'{}', max_length=102400),
        ),
        migrations.AlterField(
            model_name='missionstunt',
            name='db_attrs',
            field=models.CharField(default=b'{}', max_length=102400),
        ),
        migrations.AlterField(
            model_name='player',
            name='db_attrs',
            field=models.CharField(default=b'{}', max_length=102400),
        ),
        migrations.AlterField(
            model_name='submission',
            name='db_attrs',
            field=models.CharField(default=b'{}', max_length=102400),
        ),
    ]
