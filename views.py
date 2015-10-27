from django.shortcuts import render

# Create your views here.
def config_manage(request):
    return render(request, 'seqConfig/config/config_manage.html')