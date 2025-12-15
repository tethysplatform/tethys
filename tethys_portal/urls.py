"""
********************************************************************************
* Name: urls.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

import logging
from importlib import import_module

from django.conf import settings
from django.conf.urls.static import static
from django.urls import reverse_lazy, include, re_path
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.contrib import admin
from django.contrib.auth.views import (
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from tethys_apps.urls import extension_urls

from tethys_portal.views import (
    accounts as tethys_portal_accounts,
    api as tethys_portal_api,
    error as tethys_portal_error,
    home as tethys_portal_home,
    user as tethys_portal_user,
    admin as tethys_portal_admin,
    psa as tethys_portal_psa,
    email as tethys_portal_email,
    app_lifecycle,
)
from tethys_portal.optional_dependencies import has_module
from tethys_apps import views as tethys_apps_views
from tethys_compute import views as tethys_compute_views
from tethys_apps.base.function_extractor import TethysFunctionExtractor

# ensure at least staff users logged in before accessing admin login page
from django.contrib.admin.views.decorators import staff_member_required

from tethys_portal.optional_dependencies import optional_import

# optional imports
TrustedDevice = optional_import("mfa.TrustedDevice")
psa_views = optional_import("views", from_module="social_django")
psa_urls = optional_import("social_django.urls")
REACTPY_WEBSOCKET_ROUTE = optional_import(
    "REACTPY_WEBSOCKET_ROUTE", from_module="reactpy_django"
)

logger = logging.getLogger(f"tethys.{__name__}")


prefix_url = settings.PREFIX_URL
login_url_setting = settings.LOGIN_URL
admin.site.login = staff_member_required(
    admin.site.login,
    redirect_field_name="",
    login_url=login_url_setting,
)

admin.autodiscover()

# Extend admin urls
admin_url_list = admin.site.urls[0]

# Add dask dashboard url
admin_url_list.insert(
    0,
    re_path(
        r"^dask-dashboard/(?P<page>[\w-]+)/(?P<dask_scheduler_id>[\w-]+)/$",
        tethys_compute_views.dask_dashboard,
        name="dask_dashboard",
    ),
)

# Add clear app workspace url
admin_url_list.insert(
    0,
    re_path(
        r"^tethys_apps/tethysapp/(?P<app_id>[0-9]+)/clear-workspace/$",
        tethys_portal_admin.clear_workspace,
        name="clear_workspace",
    ),
)

# Add build app
admin_url_list.insert(
    0,
    re_path(
        r"^remove_app/(?P<app_id>[0-9]+)/$",
        app_lifecycle.remove_app,
        name="remove_app",
    ),
)
admin_url_list.insert(
    0,
    re_path(r"^create_app/$", app_lifecycle.create_app, name="create_app"),
)
admin_url_list.insert(
    0,
    re_path(r"^import_app/$", app_lifecycle.import_app, name="import_app"),
)

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
    re_path(r"^login/$", tethys_portal_accounts.login_view, name="login"),
    re_path(r"^logout/$", tethys_portal_accounts.logout_view, name="logout"),
    re_path(r"^register/$", register_controller, name="register"),
    re_path(
        r"^password/reset/$",
        never_cache(
            tethys_portal_email.TethysPasswordResetView.as_view(
                success_url=reverse_lazy("accounts:password_reset_done")
            )
        ),
        name="password_reset",
    ),
    re_path(
        r"^password/reset/done/$",
        never_cache(PasswordResetDoneView.as_view()),
        name="password_reset_done",
    ),
    re_path(
        r"^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$",
        never_cache(
            PasswordResetConfirmView.as_view(
                success_url=reverse_lazy("accounts:password_done")
            )
        ),
        name="password_confirm",
    ),
    re_path(
        r"^password/done/$",
        never_cache(PasswordResetCompleteView.as_view()),
        name="password_done",
    ),
]

api_urls = [
    re_path(r"^csrf/$", tethys_portal_api.get_csrf, name="get_csrf"),
    re_path(r"^session/$", tethys_portal_api.get_session, name="get_session"),
    re_path(r"^whoami/$", tethys_portal_api.get_whoami, name="get_whoami"),
    re_path(
        r"^token/$",
        tethys_portal_api.get_jwt_token,
        name="token_obtain_pair",
    ),
    re_path(r"^token/refresh/$", TokenRefreshView.as_view(), name="token_refresh"),
    re_path(r"^token/verify/$", TokenVerifyView.as_view(), name="token_verify"),
    re_path(r"^apps/(?P<app>[\w-]+)/$", tethys_portal_api.get_app, name="get_app"),
]

user_urls = [
    re_path(r"^$", tethys_portal_user.profile, name="profile"),
    re_path(r"^settings/$", tethys_portal_user.settings, name="settings"),
    re_path(
        r"^change-password/$",
        tethys_portal_user.change_password,
        name="change_password",
    ),
    re_path(
        r"^disconnect/(?P<provider>[\w.@+-]+)/(?P<association_id>[0-9]+)/$",
        tethys_portal_user.social_disconnect,
        name="disconnect",
    ),
    re_path(r"^delete-account/$", tethys_portal_user.delete_account, name="delete"),
    re_path(
        r"^clear-workspace/(?P<root_url>[\w.@+-]+)/$",
        tethys_portal_user.clear_workspace,
        name="clear_workspace",
    ),
    re_path(
        r"^manage-storage/$", tethys_portal_user.manage_storage, name="manage_storage"
    ),
]

developer_urls = [
    re_path(r"^gizmos/", include(("tethys_gizmos.urls", "gizmos"), namespace="gizmos")),
    re_path(
        r"^services/",
        include(("tethys_services.urls", "services"), namespace="services"),
    ),
]

# Uncomment these lines to debug the error views more easily (e.g. http://localhost:8000/developer/500/)
# development_error_urls = [
#     re_path(r'^400/$', tethys_portal_error.handler_400, name='error_400'),
#     re_path(r'^403/$', tethys_portal_error.handler_403, name='error_403'),
#     re_path(r'^404/$', tethys_portal_error.handler_404, name='error_404'),
#     re_path(r'^500/$', tethys_portal_error.handler_500, name='error_500'),
# ]
# developer_urls.extend(development_error_urls)

urlpatterns = [
    re_path(r"^admin/", admin_urls),
    re_path(r"^accounts/", include((account_urls, "accounts"), namespace="accounts")),
    re_path(r"^user/", include((user_urls, "user"), namespace="user")),
    re_path(r"^extensions/", include(extension_urls)),
    re_path(r"^developer/", include(developer_urls)),
    re_path(
        r"^handoff/(?P<app_name>[\w-]+)/$",
        tethys_apps_views.handoff_capabilities,
        name="handoff_capabilities",
    ),
    re_path(
        r"^handoff/(?P<app_name>[\w-]+)/(?P<handler_name>[\w-]+)/$",
        tethys_apps_views.handoff,
        name="handoff",
    ),
    re_path(
        r"^update-job-status/(?P<job_id>[\w-]+)/$",
        tethys_compute_views.update_job_status,
        name="update_job_status",
    ),
    re_path(
        r"^update-dask-job-status/(?P<key>[\w-]+)/$",
        tethys_compute_views.update_dask_job_status,
        name="update_dask_job_status",
    ),
    re_path(r"^api/", include((api_urls, "api"), namespace="api")),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]


if has_module(psa_views):
    oauth2_urls = [
        # authentication / association
        re_path(r"^login/(?P<backend>[^/]+)/$", tethys_portal_psa.auth, name="begin"),
        re_path(
            r"^complete/(?P<backend>[^/]+)/$",
            tethys_portal_psa.complete,
            name="complete",
        ),
        # disconnection
        re_path(
            r"^disconnect/(?P<backend>[^/]+)/$", psa_views.disconnect, name="disconnect"
        ),
        re_path(
            r"^disconnect/(?P<backend>[^/]+)/(?P<association_id>\d+)/$",
            psa_views.disconnect,
            name="disconnect_individual",
        ),
        # get tenant name for multi-tenant support
        re_path(
            r"^tenant/(?P<backend>[^/]+)/$", tethys_portal_psa.tenant, name="tenant"
        ),
    ]
    urlpatterns.append(
        re_path(
            r"^oauth2/", include((oauth2_urls, psa_urls.app_name), namespace="social")
        )
    )
if has_module("oauth2_provider"):
    url_namespace = settings.OAUTH2_PROVIDER_URL_NAMESPACE
    if not url_namespace.endswith("/"):
        url_namespace += "/"
    urlpatterns.append(
        re_path(
            url_namespace,
            include("oauth2_provider.urls", namespace="oauth2_provider"),
        )
    )
if has_module("django_recaptcha"):
    urlpatterns.append(re_path(r"^captcha/", include("captcha.urls")))
if has_module("termsandconditions"):
    urlpatterns.append(re_path(r"^terms/", include("termsandconditions.urls")))
if has_module("cookie_consent"):
    urlpatterns.append(re_path(r"^cookies/", include("cookie_consent.urls")))
if has_module("session_security"):
    urlpatterns.append(re_path(r"session_security/", include("session_security.urls")))
if has_module("mfa"):
    urlpatterns.append(re_path(r"^mfa/", include("mfa.urls")))
    urlpatterns.append(
        re_path(r"devices/add$", TrustedDevice.add, name="mfa_add_new_trusted_device")
    )

additional_url_patterns = []
additional_url_pattern_paths = settings.ADDITIONAL_URLPATTERNS

for url_pattern_path in additional_url_pattern_paths:
    try:
        mod, attr = url_pattern_path.rsplit(".", 1)
        mod = import_module(mod)
        url_patterns = getattr(mod, attr)
        assert isinstance(url_patterns, (list, tuple))
        additional_url_patterns.extend(url_patterns)
    except Exception as e:
        logger.exception(
            f'Additional urlpatterns "{url_pattern_path}" could not be imported and will be ignored.'
        )
        logger.exception(e)

urlpatterns = additional_url_patterns + urlpatterns

websocket_urlpatterns = [
    re_path(
        r"ws/app-lifecycle/(?P<app_name>\w+)/",
        app_lifecycle.AppLifeCycleConsumer.as_asgi(),
    ),
]

if has_module("reactpy_django"):
    urlpatterns.append(re_path("^reactpy/", include("reactpy_django.http.urls")))
    websocket_urlpatterns += [REACTPY_WEBSOCKET_ROUTE]

if settings.MULTIPLE_APP_MODE:
    urlpatterns.extend(
        [
            re_path(r"^$", tethys_portal_home.home, name="home"),
            re_path(r"^apps/", include("tethys_apps.urls")),
        ]
    )
else:
    urlpatterns.append(re_path(r"^", include("tethys_apps.urls")))

handler400 = tethys_portal_error.handler_400
handler403 = tethys_portal_error.handler_403
handler404 = tethys_portal_error.handler_404
handler500 = tethys_portal_error.handler_500

if prefix_url is not None and prefix_url != "/":
    urlpatterns = [
        re_path(r"^$", lambda request: redirect(f"{prefix_url}/", permanent=True)),
        re_path(
            rf"^{prefix_url}/",
            include((urlpatterns)),
        ),
    ]

if (
    login_url_setting is not None
    and login_url_setting != f"/{prefix_url}/accounts/login/"
):
    urlpatterns.append(
        re_path(
            rf"^{login_url_setting.strip('/')}/",
            tethys_portal_accounts.login_view,
            name="login_prefix",
        )
    )
