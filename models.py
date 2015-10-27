from django.db import models
from django.contrib.auth.models import User
import datetime


class Barcode(models.Model):
    name = models.CharField(max_length=64, verbose_name='Barcode name')
    sequence = models.CharField(max_length=64, verbose_name='Barcode sequence')

    def __str__(self):
        return '{}:{}'.format(self.name, self.sequence)


class RunType(models.Model):
    name = models.CharField(max_length=8, verbose_name='RunType Name')
    description = models.TextField(verbose_name='RunType Description')


class SequencingMachine(models.Model):
    name = models.CharField(max_length=16, verbose_name='SequencingMachine Name')
    description = models.TextField(verbose_name='RunType Description')


class Config(models.Model):
    creation_date = models.DateTimeField(verbose_name='Config Creation Datetime')
    runtype = models.ForeignKey(RunType, verbose_name='Config RunType')
    read1_cycles = models.IntegerField(verbose_name='Config Read1 Cycles')
    read2_cycles = models.IntegerField(verbose_name='Config Read2 Cycles')
    barcode_cycles = models.IntegerField(verbose_name='Config Barcode Cycles')
    flowcell_id = models.CharField(max_length=64, verbose_name='Config Flowcell ID')
    machine = models.ForeignKey(SequencingMachine, verbose_name='Config Machine')
    created_by = models.ForeignKey(User, verbose_name='Config User Created By', related_name='created_by_user')
    approved_by = models.ForeignKey(User, verbose_name='Config User Approved By', related_name='approved_by_user')
    approved_date = models.DateTimeField(verbose_name='Config Approved By Datetime')


class Lane(models.Model):
    number = models.SmallIntegerField(verbose_name='Lane Number')
    config = models.ForeignKey(Config, verbose_name='Lane Config')


class Library(models.Model):
    lane = models.ManyToManyField(Lane, verbose_name='Library Lane')
    bionumbus_id = models.CharField(max_length=16, verbose_name='Library Bionimbus ID')
    submitter = models.ForeignKey(User, verbose_name='Library User Submitter')
    barcode = models.ForeignKey(Barcode, verbose_name='Library Barcode')
    cluster_station_concentration = models.FloatField(
        verbose_name='Library Cluster Station Concentration')
