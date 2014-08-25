from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'tethys_site.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'tethys_site.views.login_view', name='login'),
    url(r'^accounts/logout/$', 'tethys_site.views.logout_view', name='logout'),
    url(r'^accounts/register/$', 'tethys_site.views.register', name='register')
)
