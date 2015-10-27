__author__ = 'Miguel'
from django.conf.urls import url, patterns
from django.conf import settings
from django.conf.urls.static import static
import views

urlpatterns = patterns('',
                       url(r'^config/manage', views.config_manage, name='config manage')
                       ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
