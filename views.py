from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from models import Config
from models import Library
from forms import ConfigForm
from django.core import serializers


def config_manage(request):
    configs = Config.objects.all()
    context = {'configs': configs}
    return render(request, 'seqConfig/config/config_manage.html', context)


def config_submit(request):
    if request.method == 'POST':
        config_form = ConfigForm(request.POST, instance=Config())
        if config_form.is_valid():
            config_form.save()
        return HttpResponseRedirect('/seqConfig/config/manage/')
    else:
        config_form = ConfigForm(instance=Config())
        context = {'config_form': config_form}
        context.update(csrf(request))
        return render(request, 'seqConfig/config/config_submit.html', context)


def config_get(request, flowcell_id):
    #config = Config.objects.get(flowcell_id__iexact=flowcell_id)
    config = Config.objects.select_related().get(flowcell_id__iexact=flowcell_id)
    lanes = config.lane_set.all()
    object_list = [lane for lane in lanes]
    object_list.append(config)
    for lane in lanes:
        print lane
        object_list.append(Library.objects.get(lane=lane.number))
    json_response = serializers.serialize('json', object_list)
    #json_response = serializers.serialize('json', [config, ])
    return HttpResponse(json_response)
