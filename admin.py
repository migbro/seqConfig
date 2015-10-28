from django.contrib import admin

from models import Barcode, RunType, SequencingMachine, Lane, Library, Config


class BarcodeAdmin(admin.ModelAdmin):
    model = Barcode
    list_display = ('name', 'sequence')


class RunTypeAdmin(admin.ModelAdmin):
    model = RunType
    list_display = ('name', 'description')


class SequencingMachineAdmin(admin.ModelAdmin):
    model = SequencingMachine
    list_display = ('name', 'description')


class LaneAdmin(admin.ModelAdmin):
    model = Lane


class LibraryAdmin(admin.ModelAdmin):
    model = Library


class ConfigAdmin(admin.ModelAdmin):
    model = Config
    list_display = ('pk', 'creation_date', 'runtype', 'read1_cycles',
                    'read2_cycles', 'barcode_cycles', 'run_name')


admin.site.register(Barcode, BarcodeAdmin)
admin.site.register(RunType, RunTypeAdmin)
admin.site.register(SequencingMachine, SequencingMachineAdmin)
admin.site.register(Lane, LaneAdmin)
admin.site.register(Library, LibraryAdmin)
admin.site.register(Config, ConfigAdmin)
