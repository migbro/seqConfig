from django.shortcuts import render
from models import Config

# Create your views here.
def config_manage(request):
    configs = Config.objects.all()
    context = {'configs': configs}
    return render(request, 'seqConfig/config/config_manage.html', context)

def config_submit(request):
    return render(request, 'seqConfig/config/config_submit.html')