# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_attrs', models.CharField(max_length=102400)),
            ],
        ),
        migrations.CreateModel(
            name='Bounty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_attrs', models.CharField(max_length=102400)),
            ],
        ),
        migrations.CreateModel(
            name='Charactor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_attrs', models.CharField(max_length=102400)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_created', models.DateTimeField()),
                ('db_attrs', models.CharField(max_length=102400)),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
                ('db_attrs', models.CharField(max_length=102400)),
            ],
        ),
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_attrs', models.CharField(max_length=102400)),
                ('game', models.ForeignKey(to='api.Game')),
            ],
        ),
        migrations.CreateModel(
            name='MissionStunt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_attrs', models.CharField(max_length=102400)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unique_name', models.CharField(max_length=1024)),
                ('db_attrs', models.CharField(max_length=102400)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_attrs', models.CharField(max_length=102400)),
                ('game', models.ForeignKey(to='api.Game')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='game',
            field=models.ForeignKey(to='api.Game'),
        ),
        migrations.AddField(
            model_name='charactor',
            name='game',
            field=models.ForeignKey(to='api.Game'),
        ),
        migrations.AddField(
            model_name='charactor',
            name='player',
            field=models.ForeignKey(to='api.Player'),
        ),
        migrations.AddField(
            model_name='bounty',
            name='game',
            field=models.ForeignKey(to='api.Game'),
        ),
        migrations.AddField(
            model_name='award',
            name='game',
            field=models.ForeignKey(to='api.Game'),
        ),
    ]
