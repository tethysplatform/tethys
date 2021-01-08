from jose import jwk, jwt
from jose.jwt import JWTError, JWTClaimsError, ExpiredSignatureError
from jose.utils import base64url_decode
from jose.constants import ALGORITHMS
from social_core.backends.open_id_connect import OpenIdConnectAuth
from social_core.exceptions import AuthTokenError

from tethys_services.backends.multi_tenant_mixin import MultiTenantMixin


class OneLoginOIDC(OpenIdConnectAuth):
    """OneLogin OpenIDConnect authentication backend."""
    name = 'onelogin-oidc'

    @property
    def OIDC_ENDPOINT(self):
        subdomain = self.setting('SUBDOMAIN')
        if not subdomain:
            raise ValueError('You must specify your OneLogin subdomain via the "SOCIAL_AUTH_ONELOGIN_OIDC_SUBDOMAIN" '
                             'setting (e.g. https://my-org.onelogin.com).')

        if subdomain[-1] == '/':
            subdomain = subdomain[0:-1]

        return subdomain + '/oidc/2'

    def find_valid_key(self, id_token):
        for key in self.get_jwks_keys():
            rsakey = jwk.construct(key, algorithm=ALGORITHMS.RS256)
            message, encoded_sig = id_token.rsplit('.', 1)
            decoded_sig = base64url_decode(encoded_sig.encode('utf-8'))
            if rsakey.verify(message.encode('utf-8'), decoded_sig):
                return key

    def validate_and_return_id_token(self, id_token, access_token):
        """
        Validates the id_token according to the steps at
        http://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation.
        """
        client_id, client_secret = self.get_key_and_secret()

        key = self.find_valid_key(id_token)

        if not key:
            raise AuthTokenError(self, 'Signature verification failed')

        rsakey = jwk.construct(key, algorithm=ALGORITHMS.RS256)

        try:
            claims = jwt.decode(
                id_token,
                rsakey.to_pem().decode('utf-8'),
                algorithms=[ALGORITHMS.HS256, ALGORITHMS.RS256, ALGORITHMS.ES256],
                audience=client_id,
                issuer=self.id_token_issuer(),
                access_token=access_token,
                options=self.JWT_DECODE_OPTIONS,
            )
        except ExpiredSignatureError:
            raise AuthTokenError(self, 'Signature has expired')
        except JWTClaimsError as error:
            raise AuthTokenError(self, str(error))
        except JWTError:
            raise AuthTokenError(self, 'Invalid signature')

        self.validate_claims(claims)


class OneLoginOIDCMultiTenant(MultiTenantMixin, OneLoginOIDC):
    pass
