from django.conf.urls import patterns, url

from tethys_compute import views

urlpatterns = patterns('',
    url(r'^cluster/$', views.index, name='index'),
    url(r'^cluster/add/$', views.create_cluster, name='create_cluster'),
    url(r'^cluster/(?P<pk>\d+)/update/$', views.update_cluster, name='update_cluster'),
    url(r'^cluster/(?P<pk>\d+)/delete/$', views.delete_cluster, name='delete_cluster'),
)