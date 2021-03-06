import json
import re
from copy import copy

from django.conf import settings
import sys
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from forms import BarcodeForm
from forms import ConfigForm
from models import *

from util import summary_parser


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/seq-config/config/manage/')
            else:
                # user is inactive
                messages.error(request, 'Sorry, your account is disabled')
                context = {}
                context.update(csrf(request))
                return render(request, 'seqConfig/auth/login.html')
        else:
            # Bad login details
            print 'Invalid login details: {0}, {1}'.format(username, password)
            messages.error(request, 'Invalid login details')
            context = {}
            context.update(csrf(request))
            return render(request, 'seqConfig/auth/login.html')
    else:
        context = {}
        context.update(csrf(request))
        return render(request, 'seqConfig/auth/login.html', context)


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/seq-config/login/')


# Create your views here.
@login_required
def config_manage(request):
    configs = Config.objects.all()
    context = {'configs': reversed(configs)}
    return render(request, 'seqConfig/config/config_manage.html', context)


@login_required
def config_submit(request):
    if request.method == 'POST':
        config_form = ConfigForm(request.POST, instance=Config())
        if config_form.is_valid():
            try:
                with transaction.atomic():
                    new_config = config_form.save(commit=False)
                    new_config.created_by = request.user
                    new_config.save()

                    num_lanes = request.POST.get('lane_count')
                    for lane in range(1, int(num_lanes) + 1):
                        new_lane = Lane(
                            number=lane,
                            config=new_config
                        )
                        new_lane.save()

                        num_libraries = request.POST.get('num_libraries__lane_' + str(lane))
                        for library in range(1, int(num_libraries) + 1):
                            library_tag = '__lane_{}__lib_{}'.format(lane, library)

                            # If no Barcode is provided, make NULL in database
                            barcode_id = request.POST.get('barcode' + library_tag)
                            if barcode_id != '':
                                barcode = Barcode.objects.get(pk=barcode_id)
                            else:
                                barcode = None

                            # If no cluster_station_concentration is provided, store 0.0 in database
                            cluster_station_concentration = request.POST.get('cluster_station_concentration' + library_tag)
                            if cluster_station_concentration == '':
                                cluster_station_concentration = 0.0

                            # Create the new library model, hooked up to the newly created lane_model
                            new_library = Library(
                                lane=new_lane,
                                bionimbus_id=request.POST.get('bionimbus_id' + library_tag),
                                submitter=request.POST.get('submitter' + library_tag),
                                barcode=barcode,
                                cluster_station_concentration=cluster_station_concentration
                            )
                            new_library.save()
                    messages.info(request, 'Successfully added configuration for run {}'. format(new_config.run_name))
            except Exception, e:
                messages.warning(request, 'Adding configuration failed', 'warning')
        else:
            messages.warning(request, 'Configuration was not properly filled out', 'thumbs-o-down')
        return HttpResponseRedirect('/seq-config/config/manage/')
    else:
        config_form = ConfigForm(instance=Config())
        lane_counts = LaneCount.objects.all()
        context = {
            'config_form': config_form,
            'lane_counts': lane_counts
        }
        context.update(csrf(request))
        return render(request, 'seqConfig/config/config_submit.html', context)


def config_get(request, run_name):
    """
    return a dict -
    {run_name: 151015_SN673_0235_AH4BHLCXX
     run_type: paired-end
     read1_cycles: 101
     read2_cycles: 101
     barcode_cycles: 6
     Lanes: {
        1: {
            2015-1234: {
            submitter:
            barcode_name:
            barcode_seq:
            },
            2015-1235: {
            }
        }
        2: {
        }
     }
    :param request:
    :param run_name:
    :return: HttpResponse(json)
    """
    config = Config.objects.select_related().get(run_name__iexact=run_name)
    if config.approved_by is None:
        return HttpResponse('{}')
    lanes = config.lane_set.all()
    json_response = {'run_name': config.run_name,
                     'run_type': config.runtype.name,
                     'read1_cycles': config.read1_cycles,
                     'read2_cycles': config.read2_cycles,
                     'barcode_cycles': config.barcode_cycles}
    json_response['Lanes'] = {}

    for lane in lanes:
        related = Library.objects.select_related().filter(lane=lane.pk)
        json_response['Lanes'][lane.number] = {}
        for cur in related:
            json_response['Lanes'][lane.number][cur.bionimbus_id] = {
                'submitter': cur.submitter,
                'barcode_name': cur.barcode.name,
                'barcode_seq': cur.barcode.sequence
            }
    pretty = json.dumps(json_response, sort_keys=True, indent=4)
    return HttpResponse(pretty)


@csrf_exempt
def post_demultiplex_file(request, run_name):
    """
    post summary html data, replacing any existing for the provided run
    :param request:
    :param run_name:
    :return:
    """
    if request.method == 'POST':
        print "run: {}\nrequest: {}".format(run_name, request)
        demux_json = json.loads(request.body)  # {"html": "<html-data>"}
        print "request.body: {}".format(demux_json)
        # access the run object by name
        config = Config.objects.get(run_name=run_name)
        print "{} {},{},{}".format(config.run_name, config.read1_cycles,
                                   config.barcode_cycles, config.read2_cycles)
        config.summary = demux_json['html']
        config.status = Config.RunStatus.PROCESSED
        config.save()
        response_json = {"response": "Success!"}
        return HttpResponse(json.dumps(response_json))
    else:
        return HttpResponse(json.dumps({"response": "Failed!"}))


@login_required
def config_edit(request, config_id):
    config = Config.objects.get(pk=config_id)
    if request.method == 'POST':
        updated_config_form = ConfigForm(request.POST, instance=config)
        if updated_config_form.is_valid():
            try:
                with transaction.atomic():
                    updated_config = updated_config_form.save()
                    Library.objects.filter(lane__config=updated_config).delete()
                    updated_config.lane_set.all().delete()
                    num_lanes = request.POST.get('lane_count')
                    for lane in range(1, int(num_lanes) + 1):
                        new_lane = Lane(
                            number=lane,
                            config=updated_config
                        )
                        new_lane.save()

                        num_libraries = request.POST.get('num_libraries__lane_' + str(lane))
                        for library in range(1, int(num_libraries) + 1):
                            library_tag = '__lane_{}__lib_{}'.format(lane, library)

                            # If no Barcode is provided, make NULL in database
                            barcode_id = request.POST.get('barcode' + library_tag)
                            if barcode_id != '':
                                barcode = Barcode.objects.get(pk=barcode_id)
                            else:
                                barcode = None

                            # If no cluster_station_concentration is provided, store 0.0 in database
                            cluster_station_concentration = request.POST.get('cluster_station_concentration' + library_tag)
                            if cluster_station_concentration == '':
                                cluster_station_concentration = 0.0

                            new_library = Library(
                                lane=new_lane,
                                bionimbus_id=request.POST.get('bionimbus_id' + library_tag),
                                submitter=request.POST.get('submitter' + library_tag),
                                barcode=barcode,
                                cluster_station_concentration=cluster_station_concentration
                            )
                            new_library.save()
                    messages.info(request, 'Successfully edited configuration for run {}'.format(updated_config.run_name))
            except Exception, e:
                messages.warning(request, 'Editing configuration failed', 'warning')
        else:
            messages.warning(request, 'Configuration was not properly edited', 'thumbs-o-down')
        return HttpResponseRedirect('/seq-config/config/manage/')
    else:
        config_form = ConfigForm(instance=config)

        num_lanes = config.lane_set.count()
        lane_counts = LaneCount.objects.all()
        if config.status == Config.RunStatus.PROCESSED:
            summary_html = summary_parser.add_checkboxes_to_summary(config.summary)
        elif config.status >= Config.RunStatus.COMPLETED:
            summary_html = summary_parser.add_status_to_summary(
                Library.objects.filter(lane__config__pk=config_id),
                config.summary
            )
        else:
            summary_html = config.summary

        context = {
            'config_form': config_form,
            'config_id': config.pk,
            'config_approved': True if config.approved_by is not None else False,
            'num_lanes': int(num_lanes),
            'lane_counts': lane_counts,
            'display_results': True if config.status >= Config.RunStatus.PROCESSED else False,
            'allow_release': True if config.status == Config.RunStatus.PROCESSED else False,
            'run_summary': summary_html,
            'displayable_status': config.get_status_display()
        }
        context.update(csrf(request))
        return render(request, 'seqConfig/config/config_edit.html', context)


@login_required
def config_approve(request, config_id):
    try:
        config = Config.objects.get(pk=config_id)
        if config.approved_by is not None:
            config.approved_by = None
            config.approved_date = None
            config.status = Config.RunStatus.CREATED
            messages.info(request, 'Configuration for {} has been unapproved'.format(
                config.run_name
            ), 'undo')
        else:
            config.approved_by = request.user
            config.approved_date = timezone.now()
            config.status = Config.RunStatus.APPROVED
            messages.info(request, 'Configuration for {} has been approved by {}'.format(
                config.run_name,
                config.approved_by.username
            ), 'check-circle')
        config.save()
    except Exception, e:
        messages.warning(request, 'Something went wrong', 'warning')
    return HttpResponseRedirect('/seq-config/config/manage/')

@login_required
def config_release(request):
    if request.method == 'POST':
        fields = copy(request.POST)
        config_id = fields['config_id']
        del fields['config_id']
        del fields['csrfmiddlewaretoken']
        released_bids = list(fields)
        try:
            config = Config.objects.get(pk=config_id)
            libraries = Library.objects.filter(lane__config__pk=config_id)
            num_released = 0
            with transaction.atomic():
                for library in libraries:
                    if library.bionimbus_id in released_bids:
                        library.release = Library.ReleaseStatus.YES
                        num_released += 1
                    else:
                        library.release = Library.ReleaseStatus.NO
                    library.save()
                config.status = Config.RunStatus.COMPLETED
                config.save()
            messages.info(request, 'Released {}/{} libraries for configuration {}'.format(
                num_released,
                len(libraries),
                config.run_name
            ))
        except Exception, e:
            messages.warning(request, 'Something went wrong, no libraries were released', 'warning')
    else:
        messages.warning(request, 'Request was invalid, no libraries were released', 'warning')
    return HttpResponseRedirect('/seq-config/config/manage/')

@login_required
def config_delete(request, config_id):
    if request.method == 'POST':
        try:
            config = Config.objects.get(pk=config_id)
            config_run_name = config.run_name
            config.delete()
            messages.info(request, 'Successfully deleted configuration for run {}'.format(
                config_run_name
            ), 'trash')
        except Exception, e:
            messages.warning(request, 'Configuration could not be deleted', 'warning')
    return HttpResponseRedirect('/seq-config/config/manage/')


@csrf_exempt
def get_runs_by_status(request, status):
    configs = Config.objects.filter(status=status)
    return_json = dict()
    for i, c in enumerate(configs):
        return_json[i] = c.run_name
    return HttpResponse(json.dumps(return_json))


@csrf_exempt
def set_run_status(request, run_name, status):
    config = Config.objects.get(run_name=run_name)
    if int(status) in [int(i[0]) for i in Config.status_choices]: # valid status?
        config.status = status
        config.save()
        return HttpResponse(json.dumps({"response": "Success!"}))
    else:
        return HttpResponse(json.dumps({"response": "Failed, bad status: " + status}))


@csrf_exempt
def get_library_status(request, run_name, lane_number, bionimbus_id):
    config = Config.objects.get(run_name=run_name)
    lane = Lane.objects.get(number=lane_number, config=config)
    library = Library.objects.get(lane=lane, bionimbus_id=bionimbus_id)
    return HttpResponse(json.dumps({bionimbus_id: library.release}))


@login_required
def barcode_manage(request):
    barcodes = Barcode.objects.all()
    context = {'barcodes': barcodes}
    return render(request, 'seqConfig/barcode/barcode_manage.html', context)


@login_required
def barcode_submit(request):
    if request.method == 'POST':
        print request.POST
        barcode_form = BarcodeForm(request.POST, instance=Barcode())
        new_barcodes = []
        existing_barcodes = []
        req = Barcode()
        req.name = request.POST['name']
        req.sequence = request.POST['sequence']
        if barcode_form.is_valid():
            try:
                Barcode.objects.get(sequence=request.POST['sequence'])
                existing_barcodes.append(req)
            except:
                new_barcodes.append(req)
                new_barcode = barcode_form.save(commit=False)
                new_barcode.created_by = request.user
                new_barcode.save()

        context = barcode_status(request, new_barcodes, existing_barcodes)
        return render(request, 'seqConfig/barcode/barcode_status.html', context)
    else:
        barcode_form = BarcodeForm(instance=Barcode())
        context = {
            'barcode_form': barcode_form
        }
        context.update(csrf(request))
        return render(request, 'seqConfig/barcode/barcode_submit.html', context)


@login_required
def barcode_status(request, new_barcodes, existing_barcodes):
    if request.method == 'POST':
        added = len(new_barcodes)
        ignored = len(existing_barcodes)
        total = added + ignored
        repeats = 'None'
        if ignored:
            temp = []
            for bc in existing_barcodes:
                temp.append(bc.name + ':' + bc.sequence)
            repeats = ', '.join(temp)
        print repeats
        context = {'total': total, 'added': added, 'ignored': ignored, 'exists': repeats}
        context.update(csrf(request))
        return context


@login_required
def barcode_upload(request):
    print str(request.FILES['barcode_file'])
    try:
        (new_barcodes, existing_barcodes) = Barcode.load_into_db(request.FILES['barcode_file'])
        context = barcode_status(request, new_barcodes, existing_barcodes)
        return render(request, 'seqConfig/barcode/barcode_status.html', context)
    except:
        media_path = settings.MEDIA_ROOT
        if not settings.DEBUG:
            media_path = settings.MEDIA_URL

        return HttpResponse('Failed.  Try checking settings, media path was ' + media_path)

@login_required
def barcode_edit(request, barcode_id):
    barcode = Barcode.objects.get(pk=barcode_id)
    if request.method == 'POST':
        updated_barcode_form = BarcodeForm(request.POST, instance=barcode)
        if updated_barcode_form.is_valid():
            updated_barcode_form.save()
            return HttpResponseRedirect('/seq-config/barcode/manage/')
    else:
        barcode_form = BarcodeForm(instance=barcode)
        context = {'barcode_form': barcode_form,
                   'barcode_id': barcode.pk}
        context.update(csrf(request))
        return render(request, 'seqConfig/barcode/barcode_edit.html', context)


@login_required
def barcode_delete(request, barcode_id):
    if request.method == 'POST':
        Barcode.objects.get(pk=barcode_id).delete()
    return HttpResponseRedirect('/seq-config/barcode/manage/')


def ajax_config_lane(request, num_lanes):
    return render(request, 'seqConfig/ajax/config_lane_submit.html', {'num_lanes': range(1, int(num_lanes) + 1)})


def ajax_config_library(request, start, stop, lane):
    return render(request, 'seqConfig/ajax/config_library_submit.html', {
        'lane': lane,
        'libs': range(int(start), int(stop) + 1),
        'barcodes': Barcode.objects.all()
    })


def ajax_config_lane_edit(request, num_lanes, config_id):
    lanes = Config.objects.get(pk=config_id).lane_set.all()
    context = {
        'num_lanes': range(1, int(num_lanes) + 1),
        'lanes': enumerate(lanes)
    }
    return render(request, 'seqConfig/ajax/config_lane_edit.html', context)


def ajax_config_library_edit(request, lane_id):
    lane = Lane.objects.get(pk=lane_id)
    context = {
        'lane_num': lane.number,
        'libs': enumerate(lane.library_set.all()),
        'barcodes': Barcode.objects.all()
    }
    return render(request, 'seqConfig/ajax/config_library_edit.html', context)


def ajax_bionimbus_project_by_id(request, bionimbus_id):
    return HttpResponse(json.dumps({'project_name': 'NA'}))
    if bionimbus_id == '':
        return HttpResponse(json.dumps({'project_name': ''}))
    if re.match(r'^\d+-\d+$', bionimbus_id) is None:
        return HttpResponse(json.dumps({'project_name': 'Invalid Format'}))
    try:
        eng = create_engine(settings.BIONIMBUS_PSQL_DB)
        con = eng.connect()
    except OperationalError, oe:
        print >>sys.stderr, oe
        return HttpResponse(json.dumps({'project_name': 'No DB conn'}))

    query = '''select t_project.f_name from t_project, t_experiment_unit where
    t_experiment_unit.f_bionimbus_id = '{}' and
    t_project.id = t_experiment_unit.f_project'''

    try:
        rs = con.execute(text(query.format(bionimbus_id)))
        project_name = rs.fetchone()[0]
        return HttpResponse(json.dumps({'project_name': project_name}))
    except TypeError, te:
        project_name = 'Not Found'
        return HttpResponse(json.dumps({'project_name': project_name}))
    except:
        project_name = 'Cannot query server, skipping!'
        return HttpResponse(json.dumps({'project_name': project_name}))


