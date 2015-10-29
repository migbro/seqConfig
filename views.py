from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from models import Config, LaneCount
from models import Library
from models import Barcode
from forms import ConfigForm
from django.core import serializers


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
    context = {'configs': configs}
    return render(request, 'seqConfig/config/config_manage.html', context)


@login_required
def config_submit(request):
    if request.method == 'POST':
        config_form = ConfigForm(request.POST, instance=Config())
        if config_form.is_valid():
            new_config = config_form.save(commit=False)
            new_config.created_by = request.user
            new_config.save()
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
    config = Config.objects.select_related().get(run_name__iexact=run_name)
    lanes = config.lane_set.all()
    object_list = [lane for lane in lanes]
    object_list.append(config)
    for lane in lanes:
        print lane
        object_list.append(Library.objects.get(lane=lane.number))
    json_response = serializers.serialize('json', object_list)
    #json_response = serializers.serialize('json', [config, ])
    return HttpResponse(json_response)


@login_required
def config_edit(request, config_id):
    config = Config.objects.get(pk=config_id)
    if request.method == 'POST':
        updated_config_form = ConfigForm(request.POST, instance=config)
        if updated_config_form.is_valid():
            updated_config_form.save()
            return HttpResponseRedirect('/seqConfig/config/manage/')
    else:
        config_form = ConfigForm(instance=config)
        for field in config_form:
            print 'field!'
        context = {'config_form': config_form,
                   'config_id': config.pk}
        context.update(csrf(request))
        return render(request, 'seqConfig/config/config_edit.html', context)


@login_required
def config_approve(request, config_id):
    pass


@login_required
def config_delete(request, config_id):
    if request.method == 'POST':
        Config.objects.get(pk=config_id).delete()
    return HttpResponseRedirect('/seqConfig/config/manage/')


@login_required
def barcode_manage(request):
    barcodes = Barcode.objects.all()
    context = {'barcodes': barcodes}
    return render(request, 'seqConfig/config/barcode_manage.html', context)


def ajax_config_lane(request, num_lanes):
    return render(request, 'seqConfig/ajax/config_lane.html', {'num_lanes': range(1, int(num_lanes) + 1)})