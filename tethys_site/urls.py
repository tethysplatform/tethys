from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

account_urls = [
    url(r'^login/$', 'tethys_site.views.accounts.login_view', name='login'),
    url(r'^logout/$', 'tethys_site.views.accounts.logout_view', name='logout'),
    url(r'^register/$', 'tethys_site.views.accounts.register', name='register'),
]

user_urls = [
    url(r'^$', 'tethys_site.views.user.profile', name='profile'),
    url(r'^settings/$', 'tethys_site.views.user.settings', name='settings'),
]

urlpatterns = patterns('',
    url(r'^$', 'tethys_site.views.home.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include(account_urls, namespace='accounts')),
    url(r'^user/(?P<username>\w+)/', include(user_urls, namespace='user')),
)
