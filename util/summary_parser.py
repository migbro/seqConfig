import re
import string

from seqConfig.models import Library

__author__ = 'A. Jason Grundstad'


def add_checkboxes_to_summary(summary_html=None):
    updated_html = ''
    print "Updating html_summary with checkboxes."
    pattern = re.compile('<tr><td>(\d+)</td><td>(\d+-\d+)</td>.*')
    for line in summary_html.split('\n'):
        m = pattern.match(line)  # match library lines for adding checkboxes
        if m:
            old = '<tr><td>'
            new = old + '<input type="checkbox" name="{}" checked>&nbsp;'.format(m.group(2))
            line = string.replace(line, old, new, 1)
        updated_html += line
    return updated_html


def add_status_to_summary(libraries, summary_html=None):
    updated_html = ''
    pattern = re.compile('<tr><td>(\d+)</td><td>(\d+-\d+)</td>.*')
    for line in summary_html.split('\n'):
        m = pattern.match(line)
        if m:
            old = '<tr><td>'
            bid = m.group(2)
            lib_release_status = libraries.filter(bionimbus_id=bid).first().release
            if lib_release_status == Library.ReleaseStatus.YES:
                new = old + '<span class="fa fa-check" style="color:green"></span>&nbsp;'.format(m.group(2))
            elif lib_release_status == Library.ReleaseStatus.NO:
                new = old + '<span class="fa fa-close" style="color:red"></span>&nbsp;'.format(m.group(2))
            else:
                new = old + '<span class="fa fa-question" style="color:yellow"></span>&nbsp;'.format(m.group(2))
            line = string.replace(line, old, new, 1)
        updated_html += line
    return updated_html
