# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seqConfig', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='library',
            options={'verbose_name_plural': 'Libraries'},
        ),
        migrations.RenameField(
            model_name='library',
            old_name='bionumbus_id',
            new_name='bionimbus_id',
        ),
    ]
