from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

account_urls = [
    url(r'^login/$', 'tethys_portal.views.accounts.login_view', name='login'),
    url(r'^logout/$', 'tethys_portal.views.accounts.logout_view', name='logout'),
    url(r'^register/$', 'tethys_portal.views.accounts.register', name='register'),
    url(r'^reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 'tethys_portal.views.accounts.reset_confirm',
        name='password_reset_confirm'),
    url(r'^reset/$', 'tethys_portal.views.accounts.reset', name='password_reset'),
]

user_urls = [
    url(r'^$', 'tethys_portal.views.user.profile', name='profile'),
    url(r'^settings/$', 'tethys_portal.views.user.settings', name='settings'),
    url(r'^change-password/$', 'tethys_portal.views.user.change_password', name='change_password'),
]

developer_urls = [
    url(r'^$', 'tethys_portal.views.developer.home', name='developer_home'),
    url(r'^gizmos/', include('tethys_gizmos.urls', namespace='gizmos')),
    url(r'^datasets/', include('tethys_datasets.urls', namespace='datasets')),
    url(r'^wps/', include('tethys_wps.urls', namespace='wps')),
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
    url(r'^user/(?P<username>[\w.@+-]+)/', include(user_urls, namespace='user')),
    url(r'^apps/', include('tethys_apps.urls')),
    url(r'^developer/', include(developer_urls)),
    #url(r'^error/', include(development_error_urls)),
)

handler400 = 'tethys_portal.views.error.handler_400'
handler403 = 'tethys_portal.views.error.handler_403'
handler404 = 'tethys_portal.views.error.handler_404'
handler500 = 'tethys_portal.views.error.handler_500'