from django.conf.urls import url, patterns
from django.conf import settings
from django.conf.urls.static import static
import views

__author__ = 'Miguel'

urlpatterns = patterns('',
                       url(r'^login/', views.user_login, name='login'),
                       url(r'^logout/', views.user_logout, name='logout'),

                       url(r'^config/manage/$', views.config_manage, name='config manage'),
                       url(r'^config/submit/$', views.config_submit, name='config submit'),
                       url(r'^config/edit/(?P<config_id>\d+)/$', views.config_edit, name='config edit'),
                       url(r'^config/approve/(?P<config_id>\d+)/$', views.config_approve, name='config approve'),
                       url(r'^config/delete/(?P<config_id>\d+)/$', views.config_delete, name='config delete'),
                       url(r'^config/get/(?P<run_name>\S+)/$', views.config_get, name='config_get'),
                       url(r'^barcode/manage/$', views.barcode_manage, name='barcode manage'),

                       url(r'^ajax/config/lane/(?P<num_lanes>\d+)/$', views.ajax_config_lane,
                           name='ajax_config_lane'),
                       ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
