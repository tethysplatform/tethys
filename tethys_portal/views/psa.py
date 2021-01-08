import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from social_core.utils import setting_name
from social_core.actions import do_auth, do_complete
from social_django.utils import psa
from social_django.views import _do_login

from tethys_portal.forms import SsoTenantForm
from tethys_services.backends.multi_tenant_mixin import MultiTenantMixin

NAMESPACE = getattr(settings, setting_name('URL_NAMESPACE'), None) or 'social'
log = logging.getLogger(f'tethys.{__name__}')


@never_cache
@psa('social:complete')
def auth(request, backend):
    # Redirect to tenant page if MULTI_TENANT setting configured for supported backend
    if isinstance(request.backend, MultiTenantMixin) and request.backend.setting('MULTI_TENANT', None) is not None:
        return redirect('social:tenant', backend=backend)
    return do_auth(request.backend, redirect_name=REDIRECT_FIELD_NAME)


@never_cache
@csrf_exempt
@psa('social:complete')
def complete(request, backend, *args, **kwargs):
    """Authentication complete view"""
    if isinstance(request.backend, MultiTenantMixin):
        # Get tenant name from session storage
        saved_tenant = request.backend.strategy.session_get('tenant')
        if saved_tenant is None:
            log.error('Session contains no value for "tenant".')
            return redirect('accounts:login')

        try:
            # Setting the tenant on the backend performs normalization and validation of tenant
            # Part of the validation is that the provided tenant is in the MULTI_TENANT setting.
            request.backend.tenant = saved_tenant
        except (ImproperlyConfigured, ValueError) as e:
            log.error(str(e))
            return redirect('accounts:login')

    return do_complete(request.backend, _do_login, user=request.user,
                       redirect_name=REDIRECT_FIELD_NAME, request=request,
                       *args, **kwargs)


@never_cache
@psa('social:complete')
def tenant(request, backend):
    """
    Handle tenant page request.
    """
    # Send back to login of tenant page accessed for non-multi-tenant backend
    if not isinstance(request.backend, MultiTenantMixin):
        log.error(f'Backend "{request.backend.name}" does not support MULTI_TENANT features.')
        return redirect('accounts:login')

    # Get the Tenant alias to use for titles in the form
    tenant_alias = getattr(settings, 'SSO_TENANT_ALIAS', 'Tenant').title()

    # Handle form
    if request.method == 'POST':
        if 'sso-tenant-submit' not in request.POST:
            return HttpResponseBadRequest()
        else:
            # Create form bound to request data
            form = SsoTenantForm(request.POST)

            # Validate the form
            if form.is_valid():
                cleaned_tenant = form.cleaned_data.get('tenant')

                try:
                    # Setting the tenant on the backend performs normalization and validation of tenant
                    # Part of the validation is that the provided tenant is in the MULTI_TENANT setting.
                    request.backend.tenant = cleaned_tenant
                    response = do_auth(request.backend, redirect_name=REDIRECT_FIELD_NAME)
                    return response
                except ImproperlyConfigured as e:
                    # No MULTI_TENANT settings configured: log error and redirect back to login view
                    log.error(str(e))
                    return redirect('accounts:login')
                except ValueError:
                    # Set form error and re-render form
                    form.add_error('tenant', f'Invalid {tenant_alias.lower()} provided.')

    else:
        # Create new empty form
        form = SsoTenantForm()

    context = {
        'form': form,
        'form_title': tenant_alias,
        'page_title': tenant_alias,
        'backend': backend
    }

    return render(request, 'tethys_portal/accounts/sso_tenant.html', context)
