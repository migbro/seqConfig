import views
from django.conf import settings
from django.conf.urls import url, patterns
from django.conf.urls.static import static

__author__ = 'Miguel'

urlpatterns = patterns('',
                       url(r'^login/', views.user_login, name='login'),
                       url(r'^logout/', views.user_logout, name='logout'),

                       url(r'^$', views.config_manage, name='config_manage_index'),
                       url(r'^config/manage/$', views.config_manage, name='config manage'),
                       url(r'^config/submit/$', views.config_submit, name='config submit'),
                       url(r'^config/edit/(?P<config_id>\d+)/$', views.config_edit, name='config edit'),
                       url(r'^config/approve/(?P<config_id>\d+)/$', views.config_approve, name='config approve'),
                       url(r'^config/delete/(?P<config_id>\d+)/$', views.config_delete, name='config delete'),
                       url(r'^config/get/(?P<run_name>\S+)/$', views.config_get, name='config_get'),

                       url(r'^barcode/manage/$', views.barcode_manage, name='barcode manage'),
                       url(r'^barcode/submit/$', views.barcode_submit, name='barcode submit'),
                       url(r'^barcode/upload/$', views.barcode_upload, name='barcode upload'),
                       url(r'^barcode/delete/(?P<barcode_id>\d+)/$', views.barcode_delete, name='barcode delete'),
                       url(r'^barcode/edit/(?P<barcode_id>\d+)/$', views.barcode_edit, name='barcode edit'),

                       url(r'^ajax/config/lane/(?P<num_lanes>\d+)/$', views.ajax_config_lane,
                           name='ajax_config_lane'),
                       url(r'^ajax/config/library/(?P<start>\d+)/(?P<stop>\d+)/(?P<lane>\d+)/$',
                           views.ajax_config_library,
                           name='ajax_config_library'),
                       url(r'^ajax/config/lane_edit/(?P<num_lanes>\d+)/(?P<config_id>\d+)/$', views.ajax_config_lane_edit,
                           name='ajax_config_lane'),
                       url(r'^ajax/config/library_edit/(?P<lane_id>\d+)/$',
                           views.ajax_config_library_edit,
                           name='ajax_config_library'),
                       ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
