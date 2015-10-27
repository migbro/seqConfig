from django.conf.urls import url, patterns
from django.conf import settings
from django.conf.urls.static import static
import views

__author__ = 'Miguel'

urlpatterns = patterns('',
                       url(r'^config/manage', views.config_manage, name='config manage'),
                       url(r'^config/submit', views.config_manage, name='config submit')
                       ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
