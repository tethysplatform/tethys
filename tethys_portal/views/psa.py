from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.views.decorators.cache import never_cache

from social_core.utils import setting_name
from social_core.actions import do_auth
from social_django.utils import psa

NAMESPACE = getattr(settings, setting_name('URL_NAMESPACE'), None) or 'social'


@never_cache
@psa('social:complete')
def auth(request, backend):
    print('CUSTOM SOCIAL AUTH VIEW')
    # TODO: Detect if multi-tenant applies for given backend
    # TODO: Redirect to tenant view if multi-tenant applies
    # TODO: Otherwise call do_auth like normal
    return do_auth(request.backend, redirect_name=REDIRECT_FIELD_NAME)

# TODO: implement custom versions of the other methods? complete, disconnect, disconnect single