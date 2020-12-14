from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from social_core.utils import setting_name
from social_core.actions import do_auth
from social_django.utils import psa

from forms import SsoTenantForm

NAMESPACE = getattr(settings, setting_name('URL_NAMESPACE'), None) or 'social'


@never_cache
@psa('social:complete')
def auth(request, backend):
    print('CUSTOM SOCIAL AUTH VIEW')
    # TODO: Detect if multi-tenant applies for given backend
    # TODO: Redirect to tenant view if multi-tenant applies
    # TODO: Otherwise call do_auth like normal
    return do_auth(request.backend, redirect_name=REDIRECT_FIELD_NAME)


@never_cache
@psa('social:complete')
def tenant(request, backend):
    """
    Handle tenant page request.
    """
    # Get SSO_TENANT_ALIAS setting
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
                normalized_tenant = cleaned_tenant.lower()
                print(f'"{cleaned_tenant}", "{normalized_tenant}"')
                # TODO: validate that the normalized_tenant given is a valid tenant in settings
                # TODO: get settings for matching tenant name
                # TODO: set settings on backend
                # TODO: redirect to auth provider to handle auth
    else:
        # Create new empty form
        form = SsoTenantForm()

    context = {
        'form': form,
        'form_title': tenant_alias,
        'page_title': tenant_alias
    }

    return render(request, 'tethys_portal/accounts/sso_tenant.html', context)

# TODO: implement custom versions of the other methods? complete, disconnect, disconnect single
