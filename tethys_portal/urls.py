"""
********************************************************************************
* Name: urls.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
import mfa.TrustedDevice
from django.conf.urls import include, url
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.contrib import admin
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from social_django import views as psa_views, urls as psa_urls

from tethys_apps.urls import extension_urls

from tethys_portal.views import accounts as tethys_portal_accounts, developer as tethys_portal_developer, \
    error as tethys_portal_error, home as tethys_portal_home, user as tethys_portal_user, \
    admin as tethys_portal_admin, psa as tethys_portal_psa
from tethys_apps import views as tethys_apps_views
from tethys_compute.views import dask_dashboard as tethys_dask_views

# ensure at least staff users logged in before accessing admin login page
from django.contrib.admin.views.decorators import staff_member_required
admin.site.login = staff_member_required(admin.site.login, redirect_field_name="", login_url='/accounts/login/')

admin.autodiscover()
admin.site.login = staff_member_required(admin.site.login, redirect_field_name="", login_url='/accounts/login/')

# Add Dask Dashboard Url
admin_urls = admin.site.urls
admin_urls[0].append(url(r'^dask-dashboard/(?P<page>[\w-]+)/(?P<dask_scheduler_id>[\w-]+)/$',
                         tethys_dask_views.dask_dashboard, name='dask_dashboard'))

# Add clear app workspace url
admin_urls[0].insert(0, url(r'^tethys_apps/tethysapp/(?P<app_id>[0-9]+)/clear-workspace/$',
                            tethys_portal_admin.clear_workspace, name='clear_workspace'))

account_urls = [
    url(r'^login/$', tethys_portal_accounts.login_view, name='login'),
    url(r'^logout/$', tethys_portal_accounts.logout_view, name='logout'),
    url(r'^register/$', tethys_portal_accounts.register, name='register'),
    url(r'^password/reset/$', never_cache(PasswordResetView.as_view(
        success_url=reverse_lazy('accounts:password_reset_done'))
    ), name='password_reset'),
    url(r'^password/reset/done/$', never_cache(PasswordResetDoneView.as_view()), name='password_reset_done'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', never_cache(PasswordResetConfirmView.as_view(
        success_url=reverse_lazy('accounts:password_done'))
    ), name='password_confirm'),
    url(r'^password/done/$', never_cache(PasswordResetCompleteView.as_view()), name='password_done'),
]

user_urls = [
    url(r'^$', tethys_portal_user.profile, name='profile'),
    url(r'^settings/$', tethys_portal_user.settings, name='settings'),
    url(r'^change-password/$', tethys_portal_user.change_password, name='change_password'),
    url(r'^disconnect/(?P<provider>[\w.@+-]+)/(?P<association_id>[0-9]+)/$', tethys_portal_user.social_disconnect,
        name='disconnect'),
    url(r'^delete-account/$', tethys_portal_user.delete_account, name='delete'),
    url(r'^clear-workspace/(?P<root_url>[\w.@+-]+)/$', tethys_portal_user.clear_workspace, name='clear_workspace'),
    url(r'^manage-storage/$', tethys_portal_user.manage_storage, name='manage_storage'),
]

developer_urls = [
    url(r'^$', tethys_portal_developer.home, name='developer_home'),
    url(r'^gizmos/', include(('tethys_gizmos.urls', 'gizmos'), namespace='gizmos')),
    url(r'^services/', include(('tethys_services.urls', 'services'), namespace='services')),
]

oauth2_urls = [
    # authentication / association
    url(r'^login/(?P<backend>[^/]+)/$', tethys_portal_psa.auth, name='begin'),
    url(r'^complete/(?P<backend>[^/]+)/$', psa_views.complete, name='complete'),
    # disconnection
    url(r'^disconnect/(?P<backend>[^/]+)/$', psa_views.disconnect, name='disconnect'),
    url(r'^disconnect/(?P<backend>[^/]+)/(?P<association_id>\d+)/$', psa_views.disconnect,
        name='disconnect_individual'),
    # get tenant name for multi-tenant support
    url(r'^tenant/(?P<backend>[^/]+)/$', tethys_portal_psa.tenant, name='tenant'),
]

# development_error_urls = [
#     url(r'^400/$', tethys_portal_error.handler_400, name='error_400'),
#     url(r'^403/$', tethys_portal_error.handler_403, name='error_403'),
#     url(r'^404/$', tethys_portal_error.handler_404, name='error_404'),
#     url(r'^500/$', tethys_portal_error.handler_500, name='error_500'),
# ]

urlpatterns = [
    url(r'^$', tethys_portal_home.home, name='home'),
    url(r'^admin/', admin_urls),
    url(r'^accounts/', include((account_urls, 'accounts'), namespace='accounts')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^oauth2/', include((oauth2_urls, psa_urls.app_name), namespace='social')),
    url(r'^user/(?P<username>[\w.@+-]+)/', include((user_urls, 'user'), namespace='user')),
    url(r'^apps/', include('tethys_apps.urls')),
    url(r'^extensions/', include(extension_urls)),
    url(r'^developer/', include(developer_urls)),
    url(r'^handoff/(?P<app_name>[\w-]+)/$', tethys_apps_views.handoff_capabilities, name='handoff_capabilities'),
    url(r'^handoff/(?P<app_name>[\w-]+)/(?P<handler_name>[\w-]+)/$', tethys_apps_views.handoff, name='handoff'),
    url(r'^update-job-status/(?P<job_id>[\w-]+)/$', tethys_apps_views.update_job_status, name='update_job_status'),
    url(r'^update-dask-job-status/(?P<key>[\w-]+)/$', tethys_apps_views.update_dask_job_status,
        name='update_dask_job_status'),
    url(r'^terms/', include('termsandconditions.urls')),
    url(r'session_security/', include('session_security.urls')),
    url(r'^mfa/', include('mfa.urls')),
    url(r'devices/add$', mfa.TrustedDevice.add, name="mfa_add_new_trusted_device"),
    # url(r'^error/', include(development_error_urls)),
]

handler400 = tethys_portal_error.handler_400
handler403 = tethys_portal_error.handler_403
handler404 = tethys_portal_error.handler_404
handler500 = tethys_portal_error.handler_500
