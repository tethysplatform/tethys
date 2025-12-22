"""
********************************************************************************
* Name: tethys_quotas/decorators.py
* Author: tbayer, mlebaron
* Created On: February 22, 2019
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

import logging
from django.utils.functional import wraps
from django.http import HttpRequest
from tethys_apps.utilities import get_active_app
from tethys_quotas.models.resource_quota import ResourceQuota
from tethys_quotas.utilities import passes_quota

log = logging.getLogger("tethys." + __name__)


def enforce_quota(codename):
    """
    Decorator to enforce custom quotas

    Args:
        codename (string): codename of quota to enforce
    """  # noqa: E501

    def decorator(controller):
        def wrapper(*args, **kwargs):
            try:
                request = None
                for _, arg in enumerate(args):
                    if isinstance(arg, HttpRequest):
                        request = arg
                        break

                if request is None:
                    raise ValueError("Invalid request")

                rq = ResourceQuota.objects.get(codename=codename)

                if rq.applies_to == "django.contrib.auth.models.User":
                    entity = request.user
                elif rq.applies_to == "tethys_apps.models.TethysApp":
                    entity = get_active_app(request)
                    if not entity:
                        raise ValueError("Request could not be used to find app")
                else:
                    raise ValueError(
                        "ResourceQuota that applies_to {} is not supported".format(
                            rq.applies_to
                        )
                    )

                assert passes_quota(entity, codename)

            except ValueError as e:
                log.warning(str(e))

            except ResourceQuota.DoesNotExist:
                log.warning(
                    "ResourceQuota with codename {} does not exist.".format(codename)
                )

            return controller(*args, **kwargs)

        return wraps(controller)(wrapper)

    return decorator
