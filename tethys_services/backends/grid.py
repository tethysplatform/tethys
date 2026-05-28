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


    def user_data(self, access_token, *args, **kwargs):
        return self.get_json(
            f"{self.auth_server_full_url}/grid/api/user",  # ← replace with Grid's real endpoint
            headers={"Authorization": f"Bearer {access_token}"},
        )

    def get_user_details(self, response):
        return {
            "username": response.get("username", ""),
            "email": response.get("email", ""),
            "first_name": response.get("first_name", ""),
            "last_name": response.get("last_name", ""),
        }