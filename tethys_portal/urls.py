"""
********************************************************************************
* Name: urls.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

account_urls = [
    url(r'^login/$', 'tethys_portal.views.accounts.login_view', name='login'),
    url(r'^logout/$', 'tethys_portal.views.accounts.logout_view', name='logout'),
    url(r'^register/$', 'tethys_portal.views.accounts.register', name='register'),
    url(r'^password/reset/$', 'django.contrib.auth.views.password_reset',
        {'post_reset_redirect': '/accounts/password/reset/done/'},
        name='password_reset'),
    url(r'^password/reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm',
        {'post_reset_redirect': '/accounts/password/done/'},
        name='password_confirm'),
    url(r'^password/done/$', 'django.contrib.auth.views.password_reset_complete'),
]

user_urls = [
    url(r'^$', 'tethys_portal.views.user.profile', name='profile'),
    url(r'^settings/$', 'tethys_portal.views.user.settings', name='settings'),
    url(r'^change-password/$', 'tethys_portal.views.user.change_password', name='change_password'),
    url(r'^disconnect/(?P<provider>[\w.@+-]+)/(?P<association_id>[0-9]+)/$', 'tethys_portal.views.user.social_disconnect', name='disconnect'),
    url(r'^delete-account/$', 'tethys_portal.views.user.delete_account', name='delete'),
]

developer_urls = [
    url(r'^$', 'tethys_portal.views.developer.home', name='developer_home'),
    url(r'^gizmos/', include('tethys_gizmos.urls', namespace='gizmos')),
    url(r'^services/', include('tethys_services.urls', namespace='services')),
]

# development_error_urls = [
#     url(r'^400/$', 'tethys_portal.views.error.handler_400', name='error_400'),
#     url(r'^403/$', 'tethys_portal.views.error.handler_403', name='error_403'),
#     url(r'^404/$', 'tethys_portal.views.error.handler_404', name='error_404'),
#     url(r'^500/$', 'tethys_portal.views.error.handler_500', name='error_500'),
# ]

urlpatterns = patterns('',
    url(r'^$', 'tethys_portal.views.home.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include(account_urls, namespace='accounts')),
    url(r'^oauth2/', include('social.apps.django_app.urls', namespace='social')),
    url(r'^user/(?P<username>[\w.@+-]+)/', include(user_urls, namespace='user')),
    url(r'^apps/', include('tethys_apps.urls')),
    url(r'^developer/', include(developer_urls)),
    url(r'^handoff/(?P<app_name>[\w-]+)/$', 'tethys_apps.views.handoff_capabilities', name='handoff_capabilities'),
    url(r'^handoff/(?P<app_name>[\w-]+)/(?P<handler_name>[\w-]+)/$', 'tethys_apps.views.handoff', name='handoff'),
    #url(r'^error/', include(development_error_urls)),
)

handler400 = 'tethys_portal.views.error.handler_400'
handler403 = 'tethys_portal.views.error.handler_403'
handler404 = 'tethys_portal.views.error.handler_404'
handler500 = 'tethys_portal.views.error.handler_500'