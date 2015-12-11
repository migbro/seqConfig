import re
import string

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
