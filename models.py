from django.db import models
from django.contrib.auth.models import User
import django.utils.timezone


class Run(models.Model):
    class RunStatus:
        SEQUENCING = 0
        PROCESSING = 1
        FINISHED = 2

    name = models.CharField(max_length=128, verbose_name='')
    status_choices = (
        (RunStatus.SEQUENCING, 'Sequencing'),
        (RunStatus.PROCESSING, 'Processing'),
        (RunStatus.FINISHED, 'Finished')
    )
    status = models.SmallIntegerField(choices=status_choices,
                                      verbose_name='Run Status')


class Barcode(models.Model):
    name = models.CharField(max_length=64, verbose_name='Barcode name')
    sequence = models.CharField(max_length=64, verbose_name='Barcode sequence')

    def __str__(self):
        return '{}:{}'.format(self.name, self.sequence)


class RunType(models.Model):
    name = models.CharField(max_length=32, verbose_name='RunType Name')
    description = models.TextField(verbose_name='RunType Description')

    def __str__(self):
        return self.name


class Config(models.Model):
    creation_date = models.DateTimeField(verbose_name='Config Creation Datetime',
                                         default=django.utils.timezone.now)
    runtype = models.ForeignKey(RunType, verbose_name='Config RunType')
    read1_cycles = models.IntegerField(verbose_name='Config Read1 Cycles')
    read2_cycles = models.IntegerField(verbose_name='Config Read2 Cycles',
                                       blank=True, null=True)
    barcode_cycles = models.IntegerField(verbose_name='Config Barcode Cycles',
                                         blank=True, null=True)
    run_name = models.CharField(max_length=64, verbose_name='Illumina Run Name',
                                blank=True, null=True)
    created_by = models.ForeignKey(User, verbose_name='Config User Created By',
                                   related_name='created_by_user')
    approved_by = models.ForeignKey(User, verbose_name='Config User Approved By',
                                    related_name='approved_by_user', blank=True,
                                    null=True, default=None)
    approved_date = models.DateTimeField(verbose_name='Config Approved By Datetime',
                                         blank=True, null=True, default=None)
    run = models.ForeignKey('Run', null=True, blank=True, default=None,
                            verbose_name='Config Run')

    def __str__(self):
        return '{}'.format(self.pk)


class Lane(models.Model):
    number = models.SmallIntegerField(verbose_name='Lane Number')
    config = models.ForeignKey(Config, verbose_name='Config id')

    def __str__(self):
        return '{}'.format(self.number)


class Submitter(models.Model):
    name = models.CharField(max_length=32, verbose_name='Submitter')

    def __str__(self):
        return self.name


class Library(models.Model):
    lane = models.ForeignKey(Lane, verbose_name='Library Lane')
    bionimbus_id = models.CharField(max_length=16, verbose_name='Library Bionimbus ID')
    submitter = models.ForeignKey(Submitter, verbose_name='Library User Submitter')
    barcode = models.ForeignKey(Barcode, verbose_name='Library Barcode')
    cluster_station_concentration = models.FloatField(
        verbose_name='Library Cluster Station Concentration')

    def __str__(self):
        return self.bionimbus_id

    class Meta:
        verbose_name_plural = 'Libraries'


class LaneCount(models.Model):
    name = models.CharField(max_length=128, verbose_name='Lane Count Name')
    count = models.SmallIntegerField(verbose_name='Lane Count')

    def __str__(self):
        return '{}: {}'.format(self.name, self.count)

class Results(models.Model):
    run = models.ForeignKey(Run)