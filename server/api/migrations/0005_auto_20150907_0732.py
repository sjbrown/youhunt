# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_mission__created'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='time_created',
        ),
        migrations.AddField(
            model_name='event',
            name='_created',
            field=django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True),
        ),
    ]
