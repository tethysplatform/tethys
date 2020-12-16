import datetime as dt
import hashlib
import random
import string
from unittest import mock
import uuid
from social_core.exceptions import AuthTokenError
from jose.jwt import JWTError
from jose import jwt
from jose.utils import base64url_encode
from django import test
from tethys_services.backends.onelogin import OneLoginOIDC
from tethys_services.backends.multi_tenant_mixin import MultiTenantMixin


client_id = '182f8cb0-b8b2-0138-3936-0647e35409d7174645'


@test.override_settings(
    SOCIAL_AUTH_ONELOGIN_OIDC_KEY=client_id,
    SOCIAL_AUTH_ONELOGIN_OIDC_SECRET='032f86d0f5f367171fd6270f7f5fa383fa27604bace9c5f1a0a5d5d2b4227ace',
    SOCIAL_AUTH_ONELOGIN_OIDC_SUBDOMAIN='https://my-org.onelogin.mok'
)
class OneLoginOIDCBackendTest(test.SimpleTestCase):

    def setUp(self):
        numbers = "0123456789"
        alphanumeric = string.ascii_letters + numbers
        self.nounce = "".join(random.choices(alphanumeric, k=64))
        self.sub = "".join(random.choices(numbers, k=8))
        self.iat = dt.datetime.utcnow()
        self.id_exp = self.iat + dt.timedelta(hours=3)
        self.access_exp = self.iat + dt.timedelta(hours=1)
        self.sid = str(uuid.uuid4())
        self.jti = "".join(random.choices(string.ascii_letters, k=21))
        self.kid = "".join(random.choices(alphanumeric + '_', k=43))
        self.issuer = 'https://aquaveo-dev.onelogin.com/oidc/2'

        self.pub_key = {
            "kty": "RSA",
            "e": "AQAB",
            "use": "sig",
            "kid": "APiZ0bGTMSgbLm_UitMgU7TDlE_9UC-RZArArPU4vcc",
            "n": "ynmjBq8tJtmvvlKIhSHFBPWu1maBVa4y-r6Q4_ODbP956CvDd9w7ttHojyn-kMeIqiNTdDe7O3B7KRJ7qlLRRWERrwm-FVeQGV"
                 "ltNY5h7QuLjiwyA5Wcc5auczPeAPPJLy-MVo0xgmQHt_otr8nPM-groDwhecpZPlsF8XSRU5RBjfu04s52bFku26PonBLUopkJ"
                 "05EKCf2r4sPqhunhfZi_nJ6iR5DHFovKOKJ5m4ER44vZW2WnuqSFZuO2zgeRwnJo2gdBLLDh6fiJmnyaTrW0oD4h7sW1BLJWgc"
                 "EBBMC2-9qyeCdGwSQLqGGdoEI4JnFGbM6y6U6twNUsCB7mmQ"
        }

        self.key_pair = {
            "p": "5lRvOpLl0ryH9ReBhZfojJuY69Z-UhwcfaxCuxfNY19ehCQav5qpNL-A8DX3e7jfKQ7MLRWmVjOR8PAkIx7-lBn_U5Pd9DdE9l"
                 "cUfGSvrNDnKkwMIx-7ybsUau2qi-SfHAjk3a-1scOInmTsY6uO9RmpotZvc5c31plSBNRzRH8",
            "kty": "RSA",
            "q": "4Qp6OV-Nm2jrea1hLGPaITjdV0V8AaXxken3AY0qdATJPTxddXi903-U4mMCTjoX3yoDsmI_xiy-VAH1pyMt7JPhFDPtMPBKxY"
                 "qnka6BI96cTG5vld8xe2jyiTE7vBHDXzCMld00teABThE6gYe7uI3nuvCp3c2-lxdVLXl36Oc",
            "d": "QsRHkQ20-umvvTfkEtqm6FLHu6WDoqhV4T9z8ec8AHZiUcAUrfKuskOXx5XWfxF9LHWHsHwsPpaB1nJk2y6CGbm_phO1Xb5JI0"
                 "LM82snOY6kD1bdizcLp0YZ8p046OF7BxdL1MKsf83SicVyyVPoArrdn_IUK-Ag-6HyXMPOpFtZ9Sm0xk2OdiqO5DIEfGrR0QnA"
                 "s4t8Qk5uIQMzzB0PXYJYI6ecPSZC6zPYWwq6Gf6i320rIuzNHBVKR_jKCvhLMphOyB-QMdTTgMXJCj1gmCFuLdSk2-poQhLh16"
                 "0-dtF2LU6dU973yAApp1ubszsRrXLSecpNBOJBBdTTU6Z4vQ",
            "e": "AQAB",
            "use": "sig",
            "kid": "APiZ0bGTMSgbLm_UitMgU7TDlE_9UC-RZArArPU4vcc",
            "qi": "udVEXUjdnR-1Hh7QrYz3SHXcJRILy_AS1bbNQ5PaU-26IVkJquuUgHXIJHsqN8SjUwGSNJTtDkFlodo9O6sUgCtphMUzl8Hrr"
                  "5wc6gcQTai4F8VEevRSSb7aElGlmHLHNJ49Sh2X_0ClWHbV8YbU_NplkTEMEos6LhGTUiAi-Bg",
            "dp": "N6Ukbhk5Ls1fZ0Xzg6vsgbPBoRBj2kByXaY1RO_-LcjHk9MJJ0sdH-I4K1BOZvSF7WxmxWmaku7IjlXl1RpS1MLnHXD2yV5k6"
                  "cKl71t_2ZdqkZxnvkCXZKguyZp7fmqQSfyYFjqyAa1En0ewmG_FDM_TXMTDjkB1PAI0f3g4FM8",
            "dq": "2M6CUHIJeHdNnY13OA__H9CsFh9ASEo6gMw6h4kcJGhUBKX6mGk54OBibPTcTMdVJlBQ_XQAYwnKWB8HLv4KiYky6IbadjKap"
                  "tRdelH34rneNRiUcnx0LKRAPgJrvVYTtsqMNvnFhY-JUk_w4MgHB9fXMFgaHzHP87qr-kKzTnM",
            "n": "ynmjBq8tJtmvvlKIhSHFBPWu1maBVa4y-r6Q4_ODbP956CvDd9w7ttHojyn-kMeIqiNTdDe7O3B7KRJ7qlLRRWERrwm-FVeQGV"
                 "ltNY5h7QuLjiwyA5Wcc5auczPeAPPJLy-MVo0xgmQHt_otr8nPM-groDwhecpZPlsF8XSRU5RBjfu04s52bFku26PonBLUopkJ"
                 "05EKCf2r4sPqhunhfZi_nJ6iR5DHFovKOKJ5m4ER44vZW2WnuqSFZuO2zgeRwnJo2gdBLLDh6fiJmnyaTrW0oD4h7sW1BLJWgc"
                 "EBBMC2-9qyeCdGwSQLqGGdoEI4JnFGbM6y6U6twNUsCB7mmQ"
        }

    def tearDown(self):
        pass

    def generate_access_token(self):
        """
        Generate JWT Access Token.
        """
        access_claims = {
            "jti": self.jti,
            "sub": self.sub,
            "iss": self.issuer,
            "iat": self.iat,
            "exp": self.access_exp,
            "scope": "openid profile email",
            "aud": client_id
        }
        access_token = jwt.encode(
            access_claims,
            self.key_pair,
            algorithm='RS256',
            headers={'kid': self.kid}
        )
        return access_token

    def generate_id_token(self, access_token, at_hash=None):
        """
        Generate JWT ID Token.
        """
        id_claims = {
            "sub": self.sub,
            "email": "foo.bar@baz.com",
            "preferred_username": "fbar",
            "name": "Foo Bar",
            "updated_at": 1599689662,
            "given_name": "Foo",
            "family_name": "Bar",
            "nonce": self.nounce,
            "at_hash": self.generate_at_hash(access_token) if not at_hash else at_hash,
            "sid": self.sid,
            "aud": client_id,
            "exp": int(self.id_exp.timestamp()),
            "iat": int(self.iat.timestamp()),
            "iss": self.issuer
        }
        id_token = jwt.encode(
            id_claims,
            self.key_pair,
            algorithm='RS256',
            headers={'kid': self.kid}
        )
        return id_token

    @staticmethod
    def generate_at_hash(access_token):
        """
        Get hash for JWT access token.
        """
        hash = hashlib.sha256()
        hash.update(access_token.encode())
        digest = hash.digest()
        digest_truncated = digest[:(int(len(digest) / 2))]
        at_hash = base64url_encode(digest_truncated).decode()
        return at_hash

    def test_is_mtm(self):
        inst = OneLoginOIDC()
        self.assertIsInstance(inst, MultiTenantMixin)

    def test_oidc_endpoint(self):
        inst = OneLoginOIDC()
        ret = inst.OIDC_ENDPOINT
        self.assertEqual('https://my-org.onelogin.mok/oidc/2', ret)

    @test.override_settings(SOCIAL_AUTH_ONELOGIN_OIDC_SUBDOMAIN='')
    def test_oidc_endpoint__no_subdomain(self):
        inst = OneLoginOIDC()

        with self.assertRaises(ValueError) as exc:
            inst.OIDC_ENDPOINT
            self.assertEqual('You must specify your OneLogin subdomain via the "SOCIAL_AUTH_ONELOGIN_OIDC_SUBDOMAIN" '
                             'setting (e.g. https://my-org.onelogin.com).', str(exc))

    @test.override_settings(SOCIAL_AUTH_ONELOGIN_OIDC_SUBDOMAIN='https://my-org.onelogin.mok/')
    def test_oidc_endpoint__subdomain_end_slash(self):
        inst = OneLoginOIDC()
        ret = inst.OIDC_ENDPOINT
        self.assertEqual('https://my-org.onelogin.mok/oidc/2', ret)

    @test.override_settings(SOCIAL_AUTH_ONELOGIN_OIDC_SUBDOMAIN='https://my-org.onelogin.mok')
    def test_oidc_endpoint__subdomain_no_end_slash(self):
        inst = OneLoginOIDC()
        ret = inst.OIDC_ENDPOINT
        self.assertEqual('https://my-org.onelogin.mok/oidc/2', ret)

    def test_find_valid_key(self):
        access_token = self.generate_access_token()
        id_token = self.generate_id_token(access_token)
        inst = OneLoginOIDC()
        inst.get_jwks_keys = mock.MagicMock(return_value=[self.pub_key])
        ret = inst.find_valid_key(id_token)
        self.assertEqual(self.pub_key, ret)

    def test_validate_and_return_id_token(self):
        access_token = self.generate_access_token()
        id_token = self.generate_id_token(access_token)
        inst = OneLoginOIDC()
        inst.find_valid_key = mock.MagicMock(return_value=self.pub_key)
        inst.id_token_issuer = mock.MagicMock(return_value=self.issuer)
        inst.validate_claims = mock.MagicMock()
        inst.validate_and_return_id_token(id_token, access_token)

    def test_validate_and_return_id_token__no_valid_key(self):
        access_token = self.generate_access_token()
        id_token = self.generate_id_token(access_token)
        inst = OneLoginOIDC()
        inst.find_valid_key = mock.MagicMock(return_value=None)

        with self.assertRaises(AuthTokenError) as cm:
            inst.validate_and_return_id_token(id_token, access_token)

        self.assertEqual(str(cm.exception), 'Token error: Signature verification failed')

    def test_validate_and_return_id_token__expired_signature(self):
        # Backdate iat and exp parameters 1 day to make them expired
        self.iat = dt.datetime.utcnow() - dt.timedelta(days=1)
        self.id_exp = self.iat + dt.timedelta(hours=3)
        self.access_exp = self.iat + dt.timedelta(hours=1)

        access_token = self.generate_access_token()
        id_token = self.generate_id_token(access_token)

        inst = OneLoginOIDC()
        inst.find_valid_key = mock.MagicMock(return_value=self.pub_key)
        inst.id_token_issuer = mock.MagicMock(return_value=self.issuer)

        with self.assertRaises(AuthTokenError) as cm:
            inst.validate_and_return_id_token(id_token, access_token)

        self.assertEqual(str(cm.exception), 'Token error: Signature has expired')

    def test_validate_and_return_id_token__claims_error(self):
        # Generate id_token with an invalid access token hash
        access_token = self.generate_access_token()
        id_token = self.generate_id_token(access_token, at_hash='iNvAlIdAtHaSh')

        inst = OneLoginOIDC()
        inst.find_valid_key = mock.MagicMock(return_value=self.pub_key)
        inst.id_token_issuer = mock.MagicMock(return_value=self.issuer)

        with self.assertRaises(AuthTokenError) as cm:
            inst.validate_and_return_id_token(id_token, access_token)

        self.assertEqual(str(cm.exception), 'Token error: at_hash claim does not match access_token.')

    @mock.patch('tethys_services.backends.onelogin.jwt.decode')
    def test_validate_and_return_id_token__jwt_error(self, mock_decode):
        access_token = self.generate_access_token()
        id_token = self.generate_id_token(access_token)
        inst = OneLoginOIDC()
        inst.find_valid_key = mock.MagicMock(return_value=self.pub_key)
        inst.id_token_issuer = mock.MagicMock(return_value=self.issuer)
        mock_decode.side_effect = JWTError

        with self.assertRaises(AuthTokenError) as cm:
            inst.validate_and_return_id_token(id_token, access_token)

        self.assertEqual(str(cm.exception), 'Token error: Invalid signature')
