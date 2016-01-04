import django.utils.timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


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
        cls.create_file(bc_fn, bc_mem)
        fh = open(bc_fn, 'r')
        new_barcodes = []
        existing_barcodes = []
        for line in fh:
            line = line.rstrip('\n')
            info = line.split('\t')
            barcode = Barcode()
            barcode.name = info[0]
            barcode.sequence = info[1]
            try:
                Barcode.objects.get(sequence=info[1])
                existing_barcodes.append(barcode)
            except:
                new_barcodes.append(barcode)
        fh.close()
        Barcode.objects.bulk_create(new_barcodes)
        return new_barcodes, existing_barcodes

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
    description = models.TextField(verbose_name='Config Description', null=True, blank=True)
    created_by = models.ForeignKey(User, verbose_name='Config User Created By',
                                   related_name='created_by_user')
    approved_by = models.ForeignKey(User, verbose_name='Config User Approved By',
                                    related_name='approved_by_user', blank=True,
                                    null=True, default=None)
    approved_date = models.DateTimeField(verbose_name='Config Approved By Datetime',
                                         blank=True, null=True, default=None)
    summary = models.TextField(blank=True, null=True, verbose_name='Run Summary')

    class RunStatus:
        CREATED = 0
        APPROVED = 1
        SEQUENCING = 2
        PROCESSING = 3
        PROCESSED = 4
        COMPLETED = 5
        RELEASED = 6

    status_choices_lookup = {
        RunStatus.CREATED: "Created",
        RunStatus.APPROVED: "Approved",
        RunStatus.SEQUENCING: "Sequencing",
        RunStatus.PROCESSING: "Processing",
        RunStatus.PROCESSED: "Processed",
        RunStatus.COMPLETED: "Completed",
        RunStatus.RELEASED: "Released"
    }

    status_choices = (
        (RunStatus.CREATED, 'Created'),
        (RunStatus.APPROVED, 'Approved'),
        (RunStatus.SEQUENCING, 'Sequencing'),
        (RunStatus.PROCESSING, 'Processing'),
        (RunStatus.PROCESSED, 'Processed'),
        (RunStatus.COMPLETED, 'Completed'),
        (RunStatus.RELEASED, 'Released'),
    )

    status = models.SmallIntegerField(choices=status_choices,
                                      verbose_name='Run Status',
                                      default=RunStatus.CREATED)
    previous_status = models.SmallIntegerField(choices=status_choices,
                                      verbose_name='Run Status',
                                      default=RunStatus.CREATED)
    status_change_date = models.DateTimeField(verbose_name='Status Last Changed', null=True, default=None)

    def save(self, *args, **kwargs):
        if self.previous_status != self.status:
            self.previous_status = self.status
            self.status_change_date = timezone.now()
        super(Config, self).save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.pk)


class Lane(models.Model):
    number = models.SmallIntegerField(verbose_name='Lane Number')
    config = models.ForeignKey(Config, verbose_name='Config id')

    def __str__(self):
        return '{}'.format(self.number)


class Library(models.Model):
    lane = models.ForeignKey(Lane, verbose_name='Library Lane')
    bionimbus_id = models.CharField(max_length=16, verbose_name='Library Bionimbus ID', null=True, blank=True)
    submitter = models.CharField(max_length=128, verbose_name='Library Submitter', null=True, blank=True)
    barcode = models.ForeignKey(Barcode, verbose_name='Library Barcode', null=True, blank=True)
    cluster_station_concentration = models.FloatField(
        verbose_name='Library Cluster Station Concentration', null=True, blank=True)

    class ReleaseStatus:
        NA = 0
        NO = 1
        YES = 2

    release_choices = (
        (ReleaseStatus.NA, 'NA'),
        (ReleaseStatus.NO, 'NO'),
        (ReleaseStatus.YES, 'YES')
    )
    release = models.SmallIntegerField(choices=release_choices,
                                       verbose_name='Release status',
                                       default=ReleaseStatus.NA)

    def __str__(self):
        return self.bionimbus_id

    class Meta:
        verbose_name_plural = 'Libraries'


class LaneCount(models.Model):
    name = models.CharField(max_length=128, verbose_name='Lane Count Name')
    count = models.SmallIntegerField(verbose_name='Lane Count')

    def __str__(self):
        return '{}: {}'.format(self.name, self.count)
