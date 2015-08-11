# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20150801_1100'),
    ]

    operations = [
        migrations.AddField(
            model_name='bounty',
            name='target',
            field=models.ForeignKey(default=None, to='api.Charactor'),
            preserve_default=False,
        ),
    ]
