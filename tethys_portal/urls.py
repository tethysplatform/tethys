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
]

urlpatterns = patterns('',
    url(r'^$', 'tethys_portal.views.home.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include(account_urls, namespace='accounts')),
    url(r'^user/(?P<username>\w+)/', include(user_urls, namespace='user')),
    url(r'^apps/', include('tethys_apps.urls')),
    url(r'^developer/', include(developer_urls))
)