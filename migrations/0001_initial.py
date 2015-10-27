# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Barcode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name=b'Barcode name')),
                ('sequence', models.CharField(max_length=64, verbose_name=b'Barcode sequence')),
            ],
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(verbose_name=b'Config Creation Datetime')),
                ('read1_cycles', models.IntegerField(verbose_name=b'Config Read1 Cycles')),
                ('read2_cycles', models.IntegerField(verbose_name=b'Config Read2 Cycles')),
                ('barcode_cycles', models.IntegerField(verbose_name=b'Config Barcode Cycles')),
                ('flowcell_id', models.CharField(max_length=64, verbose_name=b'Config Flowcell ID')),
                ('approved_date', models.DateTimeField(verbose_name=b'Config Approved By Datetime')),
                ('approved_by', models.ForeignKey(related_name='approved_by_user', verbose_name=b'Config User Approved By', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(related_name='created_by_user', verbose_name=b'Config User Created By', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Lane',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.SmallIntegerField(verbose_name=b'Lane Number')),
                ('config', models.ForeignKey(verbose_name=b'Lane Config', to='seqConfig.Config')),
            ],
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bionumbus_id', models.CharField(max_length=16, verbose_name=b'Library Bionimbus ID')),
                ('cluster_station_concentration', models.FloatField(verbose_name=b'Library Cluster Station Concentration')),
                ('barcode', models.ForeignKey(verbose_name=b'Library Barcode', to='seqConfig.Barcode')),
                ('lane', models.ManyToManyField(to='seqConfig.Lane', verbose_name=b'Library Lane')),
                ('submitter', models.ForeignKey(verbose_name=b'Library User Submitter', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RunType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=8, verbose_name=b'RunType Name')),
                ('description', models.TextField(verbose_name=b'RunType Description')),
            ],
        ),
        migrations.CreateModel(
            name='SequencingMachine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=16, verbose_name=b'SequencingMachine Name')),
                ('description', models.TextField(verbose_name=b'RunType Description')),
            ],
        ),
        migrations.AddField(
            model_name='config',
            name='machine',
            field=models.ForeignKey(verbose_name=b'Config Machine', to='seqConfig.SequencingMachine'),
        ),
        migrations.AddField(
            model_name='config',
            name='runtype',
            field=models.ForeignKey(verbose_name=b'Config RunType', to='seqConfig.RunType'),
        ),
    ]
