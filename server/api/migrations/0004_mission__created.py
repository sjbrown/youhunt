# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_bounty_target'),
    ]

    operations = [
        migrations.AddField(
            model_name='mission',
            name='_created',
            field=django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True),
        ),
    ]
