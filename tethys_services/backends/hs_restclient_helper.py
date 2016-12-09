import logging
import time
import hs_restclient as hs_r
from django.conf import settings
from social.apps.django_app.utils import load_strategy

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

                    refresh_user_token(social_auth_obj)

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


def _send_refresh_request(user_social):
    """
    Private function that refresh an user access token
    """
    logger.debug("------------------refresh token-----------------")
    logger.debug("------------------old token---------------------")
    logger.debug(user_social.extra_data)

    strategy = load_strategy()
    user_social.refresh_token(strategy)

    # update token_dict for back compatible
    data = user_social.extra_data
    token_dict = {
       'access_token': data['access_token'],
       'token_type': data['token_type'],
       'expires_in': data['expires_in'],
       'expires_at': data['expires_at'],
       'refresh_token': data['refresh_token'],
       'scope': data['scope']
       }
    data["token_dict"] = token_dict
    user_social.set_extra_data(extra_data=data)
    user_social.save()

    logger.debug("------------------new token-----------------")
    logger.debug(user_social.extra_data)


def refresh_user_token(user_social):
    """
    Utility function to refresh the access token if is (almost) expired
    Args:
        user_social (UserSocialAuth): a user social auth instance
    """
    try:
        try:
            expires_at = user_social.extra_data.get('expires_at')
        except Exception:
            _send_refresh_request(user_social)
            return

        current_time = int(time.time())
        if current_time >= expires_at:
            _send_refresh_request(user_social)
    except Exception as ex:
        logger.error("Failed to refresh token: " + ex.message)
        raise ex