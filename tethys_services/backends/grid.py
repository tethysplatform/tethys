from social_core.backends.oauth import BaseOAuth2

class GRiDOAuth2(BaseOAuth2):
    """
    GRiD OAuth2 authentication backend.
    """
    auth_server_hostname = "grid.nga.mil"
    http_scheme = "https"
    name = "grid"

    auth_server_full_url = "{0}://{1}".format(http_scheme, auth_server_hostname)
    AUTHORIZATION_URL = "{0}/grid/api/authorize".format(auth_server_full_url)
    ACCESS_TOKEN_URL = "{0}/grid/api/token".format(auth_server_full_url)
    ACCESS_TOKEN_METHOD = "POST"

    REDIRECT_STATE = False

    DEFAULT_SCOPE = ["api"]

    SCOPE_SEPARATOR = ","


    def get_user_details(self, response):
        return {"username": response.get("username", "")}
    

    def user_data(self, access_token, *args, **kwargs):
        return {"test_data": "This is a placeholder for GRiD user data. The actual implementation would fetch user info from GRiD using the access token."}
