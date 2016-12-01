import hs_restclient as hs_r
from django.conf import settings


def get_oauth_hs(request):
    hs = None
    error_msg_head = "Failed to initialize hs object: "

    if request.user.social_auth.count() == 0:
        raise Exception(error_msg_head + "Not logged in through OAuth")
    if request.user.social_auth.count() > 1:
        raise Exception(error_msg_head + "Found multiple OAuth login objects")

    try:
        social_auth_obj = request.user.social_auth.first()
        hs_restclient_para_dict = social_auth_obj.extra_data['hs_restclient']

        client_id = getattr(settings, hs_restclient_para_dict['key_name'], 'None')
        client_secret = getattr(settings, hs_restclient_para_dict['secret_name'], 'None')
        token = hs_restclient_para_dict['token']
        auth = hs_r.HydroShareAuthOAuth2(client_id, client_secret, token=token)

        auth_server_hostname = hs_restclient_para_dict["auth_server_hostname"]
        hs = hs_r.HydroShare(auth=auth, hostname=auth_server_hostname)

    except Exception as ex:
        raise Exception(error_msg_head + ex.message)
    finally:
        return hs