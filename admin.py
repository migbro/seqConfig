from django.contrib import admin

from models import Barcode, RunType, SequencingMachine, Lane, Library, Config


class BarcodeAdmin(admin.ModelAdmin):
    model = Barcode


class RunTypeAdmin(admin.ModelAdmin):
    model = RunType


class SequencingMachineAdmin(admin.ModelAdmin):
    model = SequencingMachine


class LaneAdmin(admin.ModelAdmin):
    model = Lane


class LibraryAdmin(admin.ModelAdmin):
    model = Library


class ConfigAdmin(admin.ModelAdmin):
    model = Config


admin.site.register(Barcode, BarcodeAdmin)
admin.site.register(RunType, RunTypeAdmin)
admin.site.register(SequencingMachine, SequencingMachineAdmin)
admin.site.register(Lane, LaneAdmin)
admin.site.register(Library, LibraryAdmin)
admin.site.register(Config, ConfigAdmin)
