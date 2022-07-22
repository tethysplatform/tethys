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
from django.conf import settings
from django.urls import reverse_lazy, include, re_path
from django.views.decorators.cache import never_cache
from django.contrib import admin
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from social_django import views as psa_views, urls as psa_urls

from tethys_apps.urls import extension_urls

from tethys_portal.views import accounts as tethys_portal_accounts, api as tethys_portal_api, \
    error as tethys_portal_error, home as tethys_portal_home, user as tethys_portal_user, \
    admin as tethys_portal_admin, psa as tethys_portal_psa, email as tethys_portal_email
from tethys_apps import views as tethys_apps_views
from tethys_compute.views import dask_dashboard as tethys_dask_views
from tethys_apps.base.function_extractor import TethysFunctionExtractor

# ensure at least staff users logged in before accessing admin login page
from django.contrib.admin.views.decorators import staff_member_required
admin.site.login = staff_member_required(admin.site.login, redirect_field_name="", login_url='/accounts/login/')

admin.autodiscover()
admin.site.login = staff_member_required(admin.site.login, redirect_field_name="", login_url='/accounts/login/')

# Extend admin urls
admin_url_list = admin.site.urls[0]

# Add dask dashboard url
admin_url_list.insert(0, re_path(r'^dask-dashboard/(?P<page>[\w-]+)/(?P<dask_scheduler_id>[\w-]+)/$',
                                 tethys_dask_views.dask_dashboard, name='dask_dashboard'))

# Add clear app workspace url
admin_url_list.insert(0, re_path(r'^tethys_apps/tethysapp/(?P<app_id>[0-9]+)/clear-workspace/$',
                                 tethys_portal_admin.clear_workspace, name='clear_workspace'))

# Recreate admin.site.urls tuple
admin_urls = (admin_url_list, admin.site.urls[1], admin.site.urls[2])

# default register controller
register_controller = tethys_portal_accounts.register
register_controller_setting = settings.REGISTER_CONTROLLER
if register_controller_setting:
    function_extractor = TethysFunctionExtractor(register_controller_setting, None)
    register_controller = function_extractor.function
    try:
        register_controller = register_controller.as_controller()
    except AttributeError:
        # not a class-based view
        pass

account_urls = [
    re_path(r'^login/$', tethys_portal_accounts.login_view, name='login'),
    re_path(r'^logout/$', tethys_portal_accounts.logout_view, name='logout'),
    re_path(r'^register/$', register_controller, name='register'),
    re_path(r'^password/reset/$', never_cache(tethys_portal_email.TethysPasswordResetView.as_view(
        success_url=reverse_lazy('accounts:password_reset_done'))
    ), name='password_reset'),
    re_path(r'^password/reset/done/$', never_cache(PasswordResetDoneView.as_view()), name='password_reset_done'),
    re_path(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', never_cache(PasswordResetConfirmView.as_view(
        success_url=reverse_lazy('accounts:password_done'))
    ), name='password_confirm'),
    re_path(r'^password/done/$', never_cache(PasswordResetCompleteView.as_view()), name='password_done'),
]

api_urls = [
    re_path(r'^csrf/$', tethys_portal_api.get_csrf, name='get_csrf'),
    re_path(r'^session/$', tethys_portal_api.get_session, name='get_session'),
    re_path(r'^whoami/$', tethys_portal_api.get_whoami, name='get_whoami'),
    re_path(r'^apps/(?P<app>[\w-]+)/$', tethys_portal_api.get_app, name='get_app'),
]

user_urls = [
    re_path(r'^$', tethys_portal_user.profile, name='profile'),
    re_path(r'^settings/$', tethys_portal_user.settings, name='settings'),
    re_path(r'^change-password/$', tethys_portal_user.change_password, name='change_password'),
    re_path(r'^disconnect/(?P<provider>[\w.@+-]+)/(?P<association_id>[0-9]+)/$', tethys_portal_user.social_disconnect,
            name='disconnect'),
    re_path(r'^delete-account/$', tethys_portal_user.delete_account, name='delete'),
    re_path(r'^clear-workspace/(?P<root_url>[\w.@+-]+)/$', tethys_portal_user.clear_workspace, name='clear_workspace'),
    re_path(r'^manage-storage/$', tethys_portal_user.manage_storage, name='manage_storage'),
]

developer_urls = [
    re_path(r'^gizmos/', include(('tethys_gizmos.urls', 'gizmos'), namespace='gizmos')),
    re_path(r'^services/', include(('tethys_services.urls', 'services'), namespace='services')),
]

oauth2_urls = [
    # authentication / association
    re_path(r'^login/(?P<backend>[^/]+)/$', tethys_portal_psa.auth, name='begin'),
    re_path(r'^complete/(?P<backend>[^/]+)/$', tethys_portal_psa.complete, name='complete'),
    # disconnection
    re_path(r'^disconnect/(?P<backend>[^/]+)/$', psa_views.disconnect, name='disconnect'),
    re_path(r'^disconnect/(?P<backend>[^/]+)/(?P<association_id>\d+)/$', psa_views.disconnect,
            name='disconnect_individual'),
    # get tenant name for multi-tenant support
    re_path(r'^tenant/(?P<backend>[^/]+)/$', tethys_portal_psa.tenant, name='tenant'),
]

# development_error_urls = [
#     re_path(r'^400/$', tethys_portal_error.handler_400, name='error_400'),
#     re_path(r'^403/$', tethys_portal_error.handler_403, name='error_403'),
#     re_path(r'^404/$', tethys_portal_error.handler_404, name='error_404'),
#     re_path(r'^500/$', tethys_portal_error.handler_500, name='error_500'),
# ]

urlpatterns = [
    re_path(r'^$', tethys_portal_home.home, name='home'),
    re_path(r'^admin/', admin_urls),
    re_path(r'^accounts/', include((account_urls, 'accounts'), namespace='accounts')),
    re_path(r'^captcha/', include('captcha.urls')),
    re_path(r'^oauth2/', include((oauth2_urls, psa_urls.app_name), namespace='social')),
    re_path(r'^user/', include((user_urls, 'user'), namespace='user')),
    re_path(r'^apps/', include('tethys_apps.urls')),
    re_path(r'^extensions/', include(extension_urls)),
    re_path(r'^developer/', include(developer_urls)),
    re_path(r'^handoff/(?P<app_name>[\w-]+)/$', tethys_apps_views.handoff_capabilities, name='handoff_capabilities'),
    re_path(r'^handoff/(?P<app_name>[\w-]+)/(?P<handler_name>[\w-]+)/$', tethys_apps_views.handoff, name='handoff'),
    re_path(r'^update-job-status/(?P<job_id>[\w-]+)/$', tethys_apps_views.update_job_status, name='update_job_status'),
    re_path(r'^update-dask-job-status/(?P<key>[\w-]+)/$', tethys_apps_views.update_dask_job_status,
            name='update_dask_job_status'),
    re_path(r'^terms/', include('termsandconditions.urls')),
    re_path(r'session_security/', include('session_security.urls')),
    re_path(r'^mfa/', include('mfa.urls')),
    re_path(r'devices/add$', mfa.TrustedDevice.add, name="mfa_add_new_trusted_device"),
    re_path(r'api/', include((api_urls, 'api'), namespace='api')),
    # re_path(r'^error/', include(development_error_urls)),
]

handler400 = tethys_portal_error.handler_400
handler403 = tethys_portal_error.handler_403
handler404 = tethys_portal_error.handler_404
handler500 = tethys_portal_error.handler_500
