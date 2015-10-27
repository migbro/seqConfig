from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class Barcode(models.Model):
    name = models.CharField(max_length=64, verbose_name='Barcode name')
    sequence = models.CharField(max_length=64, verbose_name='Barcode sequence')

    def __str__(self):
        return '{}:{}'.format(self.name, self.sequence)
