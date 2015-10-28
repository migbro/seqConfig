__author__ = 'Dominic Fitzgerald'

from django import forms
from models import Config

class ConfigForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ConfigForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = Config
        fields = ['runtype', 'read1_cycles', 'read2_cycles', 'barcode_cycles',
                  'flowcell_id', 'machine', 'created_by']
