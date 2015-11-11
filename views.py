import json
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from forms import BarcodeForm
from forms import ConfigForm
from models import *


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/seqConfig/config/manage/')
            else:
                # user is inactive
                return HttpResponse('Sorry, your account is disabled.')
        else:
            # Bad login details
            print 'Invalid login details: {0}, {1}'.format(username, password)
            return HttpResponse('Invalid login details provided.')
    else:
        context = {}
        context.update(csrf(request))
        return render(request, 'seqConfig/auth/login.html', context)


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/seqConfig/login/')


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
        return HttpResponseRedirect('/seqConfig/config/manage/')
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
    json_response = {'run_name': config.run_name, 'run_type': config.runtype.name,
                     'read1_cycles': config.read1_cycles, 'read2_cycles': config.read2_cycles,
                     'barcode_cycles': config.barcode_cycles}
    json_response['Lanes'] = {}

    for lane in lanes:
        related = Library.objects.select_related().filter(lane=lane.pk)
        json_response['Lanes'][lane.number] = {}
        for cur in related:
            json_response['Lanes'][lane.number][cur.bionimbus_id] = {'submitter': cur.submitter.name,
                                                                     'barcode_name': cur.barcode.name,
                                                                     'barcode_seq': cur.barcode.sequence}
            json_response['Lanes'][lane.number][cur.bionimbus_id] = {'submitter': cur.submitter.name,
                                                                     'barcode_name': cur.barcode.name,
                                                                     'barcode_seq': cur.barcode.sequence}
    pretty = json.dumps(json_response, sort_keys=True, indent=4)
    return HttpResponse(pretty)


@login_required
def config_edit(request, config_id):
    config = Config.objects.get(pk=config_id)
    if request.method == 'POST':
        updated_config_form = ConfigForm(request.POST, instance=config)
        if updated_config_form.is_valid():
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
        return HttpResponseRedirect('/seqConfig/config/manage/')
    else:
        config_form = ConfigForm(instance=config)

        num_lanes = config.lane_set.count()
        lane_counts = LaneCount.objects.all()
        context = {
            'config_form': config_form,
            'config_id': config.pk,
            'config_approved': True if config.approved_by is not None else False,
            'num_lanes': int(num_lanes),
            'lane_counts': lane_counts
        }
        context.update(csrf(request))
        return render(request, 'seqConfig/config/config_edit.html', context)


@login_required
def config_approve(request, config_id):
    config = Config.objects.get(pk=config_id)
    if config.approved_by is not None:
        config.approved_by = None
        config.approved_date = None
    else:
        config.approved_by = request.user
        config.approved_date = datetime.now()
    config.save()
    return HttpResponseRedirect('/seqConfig/config/manage/')


@login_required
def config_delete(request, config_id):
    if request.method == 'POST':
        Config.objects.get(pk=config_id).delete()
    return HttpResponseRedirect('/seqConfig/config/manage/')


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
        if barcode_form.is_valid():
            new_barcode = barcode_form.save(commit=False)
            new_barcode.created_by = request.user
            new_barcode.save()

        return HttpResponseRedirect('/seqConfig/barcode/manage/')
    else:
        barcode_form = BarcodeForm(instance=Barcode())
        context = {
            'barcode_form': barcode_form
        }
        context.update(csrf(request))
        return render(request, 'seqConfig/barcode/barcode_submit.html', context)


@login_required
def barcode_upload(request):
    print 'got request'
    print str(request.FILES['barcode_file'])
    Barcode.load_into_db(request.FILES['barcode_file'])
    return HttpResponseRedirect('/seqConfig/barcode/manage/')


@login_required
def barcode_edit(request, barcode_id):
    barcode = Barcode.objects.get(pk=barcode_id)
    if request.method == 'POST':
        updated_barcode_form = BarcodeForm(request.POST, instance=barcode)
        if updated_barcode_form.is_valid():
            updated_barcode_form.save()
            return HttpResponseRedirect('/seqConfig/barcode/manage/')
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
    return HttpResponseRedirect('/seqConfig/barcode/manage/')


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
