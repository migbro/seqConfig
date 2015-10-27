from django.conf.urls import url, patterns
from django.conf import settings
from django.conf.urls.static import static
import views

__author__ = 'Miguel'

urlpatterns = patterns('',
                       url(r'^config/manage', views.config_manage, name='config manage'),
                       url(r'^config/submit', views.config_manage, name='config submit'),
                       url(r'^config/get/(?P<config_id>\d+)/$', views.config_get, name='config_get')
                       ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
