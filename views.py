from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from models import Config
from forms import ConfigForm

# Create your views here.
def config_manage(request):
    configs = Config.objects.all()
    context = {'configs': configs}
    return render(request, 'seqConfig/config/config_manage.html', context)

def config_submit(request):
    if request.method == 'POST':
        config_form = ConfigForm(request.POST, instance=Config())
        if config_form.is_valid():
            config_form.save()
        return HttpResponseRedirect('seqConfig/config/manage/')
    else:
        config_form = ConfigForm(instance=Config())
        context = {'config_form': config_form}
        context.update(csrf(request))
        return render(request, 'seqConfig/config/config_submit.html', context)

def config_get(request, config_id):
    config = Config.objects.get(pk=config_id)
    json_response = ''
    return HttpResponse(json_response)
