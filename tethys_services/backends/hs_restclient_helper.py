import logging
import hs_restclient as hs_r
from django.conf import settings

logger = logging.getLogger(__name__)


def get_oauth_hs(request):
    hs = None
    error_msg_head = "Failed to initialize hs object: "

    try:
        for social_auth_obj in request.user.social_auth.all():
            backend_instance = social_auth_obj.get_backend_instance()
            backend_name = backend_instance.name
            logger.debug("Found oauth backend: {0}".format(backend_name))

            if "hydroshare" in backend_name.lower():
                user_id = social_auth_obj.extra_data['id']
                auth_server_hostname = backend_instance.auth_server_hostname
                client_id = getattr(settings, "SOCIAL_AUTH_{0}_KEY".format(backend_name.upper()), 'None')
                client_secret = getattr(settings, "SOCIAL_AUTH_{0}_SECRET".format(backend_name.upper()), 'None')

                if hs is None:
                    auth = hs_r.HydroShareAuthOAuth2(client_id, client_secret, token=social_auth_obj.extra_data)
                    hs = hs_r.HydroShare(auth=auth, hostname=auth_server_hostname)
                    logger.debug("hs object initialized: {0} @ {1}".format(user_id, auth_server_hostname))
                else:
                    raise Exception("Found another hydroshare oauth instance: {0} @ {1}".format(user_id, auth_server_hostname))

        if hs is None:
            raise Exception("Not logged in through HydroShare")

        return hs

    except Exception as ex:
        logger.exception(error_msg_head + ex.message)
        raise HSClientInitException(ex.message)


class HSClientInitException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)