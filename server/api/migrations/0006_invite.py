# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import api.lazyjason
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20150907_0732'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('db_attrs', models.CharField(default=b'{}', max_length=102400)),
                ('game', models.ForeignKey(to='api.Game')),
            ],
            bases=(models.Model, api.lazyjason.LazyJason),
        ),
    ]
