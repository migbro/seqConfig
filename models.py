import django.utils.timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class Run(models.Model):
    class RunStatus:
        SEQUENCING = 0
        PROCESSING = 1
        FINISHED = 2
        COMPLETED = 3

    name = models.CharField(max_length=128, verbose_name='')
    status_choices = (
        (RunStatus.SEQUENCING, 'Sequencing'),
        (RunStatus.PROCESSING, 'Processing'),
        (RunStatus.FINISHED, 'Finished'),
        (RunStatus.COMPLETED, 'Completed')
    )
    status = models.SmallIntegerField(choices=status_choices,
                                      verbose_name='Run Status')


class Barcode(models.Model):
    name = models.CharField(max_length=64, verbose_name='Barcode name')
    sequence = models.CharField(max_length=64, verbose_name='Barcode sequence')

    @classmethod
    def get_media_path(cls):
        """
        The path to /viewer/files is different in DEBUG vs Non-DEBUG
        :return:
        """
        if settings.DEBUG:
            media_path = settings.MEDIA_ROOT
        else:
            media_path = settings.MEDIA_URL
        print "settings.DEBUG is {}, set media_path to: {}".format(settings.DEBUG,
                                                                   media_path)
        return media_path
    @classmethod
    def create_file(cls, bc_fn, bc_mem):
        new = open(str(bc_fn), 'wb+')
        for chunk in bc_mem:
            new.write(chunk)
        new.close()

    @classmethod
    def load_into_db(cls, bc_mem):
        media_path = cls.get_media_path()
        bc_fn = media_path + '/' + str(bc_mem)
        print 'Request received, creating file' + bc_fn
        cls.create_file(bc_fn, bc_mem)
        print 'Opening file'
        fh = open(bc_fn, 'r')
        all_barcodes = []
        for line in fh:
            line = line.rstrip('\n')
            info = line.split('\t')
            barcode = Barcode()
            barcode.name = info[0]
            barcode.sequence = info[1]
            all_barcodes.append(barcode)
        fh.close()
        print 'File processed, saving'
        Barcode.objects.bulk_create(all_barcodes)
        return True

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
    run_name = models.CharField(max_length=64, verbose_name='Run Folder ID',
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


class Library(models.Model):
    lane = models.ForeignKey(Lane, verbose_name='Library Lane')
    bionimbus_id = models.CharField(max_length=16, verbose_name='Library Bionimbus ID')
    submitter = models.CharField(max_length=128, verbose_name='Library Submitter')
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
