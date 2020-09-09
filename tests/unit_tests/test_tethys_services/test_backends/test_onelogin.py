from unittest import mock
from django import test
from social_core.exceptions import AuthTokenError
from jose.jwt import JWTError, JWTClaimsError, ExpiredSignatureError
from tethys_services.backends.onelogin import OneLoginOIDC


@test.override_settings(
    SOCIAL_AUTH_ONELOGIN_OIDC_KEY='182f8cb0-b8b2-0138-3936-0647e35409d7174645',
    SOCIAL_AUTH_ONELOGIN_OIDC_SECRET='032f86d0f5f367171fd6270f7f5fa383fa27604bace9c5f1a0a5d5d2b4227ace',
    SOCIAL_AUTH_ONELOGIN_OIDC_SUBDOMAIN='https://my-org.onelogin.mok'
)
class OneLoginOIDCBackendTest(test.SimpleTestCase):

    def setUp(self):
        self.id_token = \
            'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkpSY080bnhzNWpnYzhZZE43STJoTE80Vl9xbDFiZG9pTVhtY1lnSG00SHMi' \
            'fQ.eyJzdWIiOiI5MTI5MTU4NiIsImVtYWlsIjoibnN3YWluQGFxdWF2ZW8uY29tIiwicHJlZmVycmVkX3VzZXJuYW1lIjoibnN3YWluQ' \
            'GFxdWF2ZW8uY29tIiwibmFtZSI6Ik5hdGhhbiBTd2FpbiIsInVwZGF0ZWRfYXQiOjE1OTk2ODk2NjIsImdpdmVuX25hbWUiOiJOYXRoY' \
            'W4iLCJmYW1pbHlfbmFtZSI6IlN3YWluIiwibm9uY2UiOiJVQmY4bzlNRHd4M01aWUFaNlpPMVY4VWVybUVmSDc1dVhyT09CTUdoSGxFb' \
            '2dzaU5WdEsydGd5M1dmbk9CUVZKIiwiYXRfaGFzaCI6InBYZ0VkR3RFUU5vRGRrMlU2RnRzcmciLCJzaWQiOiIwNzM5NGE2YS01YzgyL' \
            'TRjMTctYmFjMS1iYTJmZWE4ZmFhYjgiLCJhdWQiOiIxODJmOGNiMC1iOGIyLTAxMzgtMzkzNi0wNjQ3ZTM1NDA5ZDcxNzQ2NDUiLCJle' \
            'HAiOjE1OTk2OTg3OTIsImlhdCI6MTU5OTY5MTU5MiwiaXNzIjoiaHR0cHM6Ly9hcXVhdmVvLWRldi5vbmVsb2dpbi5jb20vb2lkYy8yI' \
            'n0.yhr6PujjojakrIHkzfOXYhBpgA3fEUcpbet4XvmM0zwoAJUfwXlsxS8hJZ0ub67H9CShhSbW7apUVZCjC_E6ENzyah9ccdF5-G0wJ' \
            'Uw4dnraP_WROaXpOY4bx18PBSzjFEFSsg2-b32zMkOsL4vnKUXrgN1itekrX9BTUqwPd_Q-WelRMnA3Rrmp7galL1pbSl-QIU33Zubyv' \
            'J1_rf6hMWKhB5NaUVX_ZlnYZpxNy1m1hPqyVDSXHjZ3PZj0CpD0Zc60_XNgRzOl03RXZb_XmImuXsf6Pk3X3TV2xGnQxaXXKFN0ctGiW' \
            'QsQyeoIdYzgEv_XLGCuCjEz-wFU1p-ylA'

        self.access_token = \
            'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkpSY080bnhzNWpnYzhZZE43STJoTE80Vl9xbDFiZG9pTVhtY1lnSG00SHM' \
            'ifQ.eyJqdGkiOiJlS1pWVGpkUHVHOG5IeVFnbGp5dm8iLCJzdWIiOiI5MTI5MTU4NiIsImlzcyI6Imh0dHBzOi8vYXF1YXZlby1kZXY' \
            'ub25lbG9naW4uY29tL29pZGMvMiIsImlhdCI6MTU5OTY5MTU5MiwiZXhwIjoxNTk5Njk1MTkyLCJzY29wZSI6Im9wZW5pZCBwcm9maW' \
            'xlIGVtYWlsIiwiYXVkIjoiMTgyZjhjYjAtYjhiMi0wMTM4LTM5MzYtMDY0N2UzNTQwOWQ3MTc0NjQ1In0.Vwr-QII98aopLNRtYG5qv' \
            '2DqWAd2Q2Z7DGCbH_Ck9nNKp-zXmDnUYPB9lbOs1HIJVzCYvRxsyjjzcPwOfuYSoJHm1Jd1bNX5n-GnzmuLyicUdjHprlDM5lRxkdPE' \
            'CAMUAdAJupc9OLVUs5hJwaoHlfGrkz-DiUpP6TjVbPIgB3XqkmkyvoEftzJ4Pz62Jr9zP0WGjVFhySLVmYgvnsPwwKa6nlkhiRABNux' \
            'Qr8OR7gy9sUgcIaTYGI9TXCjO4sY_ITL08-vhXJIFd3zj0oDlIL15NnX_6ehgDEapDh60S0EHIhzJ4oqGyV8YjJcq2avk3cPGGXvjjV' \
            'ztpUN011HjhQ'

        self.key = {
            'kty': 'RSA',
            'kid': 'JRcO4nxs5jgc8YdN7I2hLO4V_ql1bdoiMXmcYgHm4Hs',
            'use': 'sig',
            'n': 'z8fZszkUNh1y1iSI6ZCkrwoZx1ZcFuQEngI8G_9VPjJXupqbgXedsV0YqDzQzYmdXd_lLb_OYWdyAP1FV6d2d4PfVjw4rGLqgYN'
                 '5hEPFYqDEusiKtXyeh38xl37Nb8LGTX1qdstZjcXRo2YQ64W4UyuMko_TGOCxRNJg1fAfxRt1yV_ZeFV_93BMNjubV2D7kvpzaS'
                 'tJmYJi8A6QHqaqHaQkxAvYhJVi9XDajD3vvUlTVyOjURAnuaByA749glGBio5N9AfFTnYbHbeBOK3VJi6EJZzsuj3-5P4GUTYnS'
                 'frScs_kblaoeqt4GkExJqMZXGJTfGnX2UbYAjGHSTAoQw',
            'e': 'AQAB'
        }
        self.issuer = 'https://aquaveo-dev.onelogin.com/oidc/2'

    def tearDown(self):
        pass

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
        inst = OneLoginOIDC()
        inst.get_jwks_keys = mock.MagicMock(return_value=[self.key])
        ret = inst.find_valid_key(self.id_token)
        self.assertEqual(self.key, ret)

    def test_validate_and_return_id_token(self):
        inst = OneLoginOIDC()
        inst.find_valid_key = mock.MagicMock(return_value=self.key)
        inst.id_token_issuer = mock.MagicMock(return_value=self.issuer)
        inst.validate_claims = mock.MagicMock()
        inst.validate_and_return_id_token(self.id_token, self.access_token)

    def test_validate_and_return_id_token__no_valid_key(self):
        inst = OneLoginOIDC()
        inst.find_valid_key = mock.MagicMock(return_value=None)
        with self.assertRaises(AuthTokenError) as cm:
            inst.validate_and_return_id_token(self.id_token, self.access_token)

        self.assertEqual(str(cm.exception), 'Token error: Signature verification failed')

    @mock.patch('tethys_services.backends.onelogin.jwt.decode')
    def test_validate_and_return_id_token__expired_signature(self, mock_decode):
        inst = OneLoginOIDC()
        inst.find_valid_key = mock.MagicMock(return_value=self.key)
        inst.id_token_issuer = mock.MagicMock(return_value=self.issuer)
        mock_decode.side_effect = ExpiredSignatureError

        with self.assertRaises(AuthTokenError) as cm:
            inst.validate_and_return_id_token(self.id_token, self.access_token)

        self.assertEqual(str(cm.exception), 'Token error: Signature has expired')

    @mock.patch('tethys_services.backends.onelogin.jwt.decode')
    def test_validate_and_return_id_token__claims_error(self, mock_decode):
        inst = OneLoginOIDC()
        inst.find_valid_key = mock.MagicMock(return_value=self.key)
        inst.id_token_issuer = mock.MagicMock(return_value=self.issuer)
        mock_decode.side_effect = JWTClaimsError('Foo bar')

        with self.assertRaises(AuthTokenError) as cm:
            inst.validate_and_return_id_token(self.id_token, self.access_token)

        self.assertEqual(str(cm.exception), 'Token error: Foo bar')

    @mock.patch('tethys_services.backends.onelogin.jwt.decode')
    def test_validate_and_return_id_token__jwt_error(self, mock_decode):
        inst = OneLoginOIDC()
        inst.find_valid_key = mock.MagicMock(return_value=self.key)
        inst.id_token_issuer = mock.MagicMock(return_value=self.issuer)
        mock_decode.side_effect = JWTError

        with self.assertRaises(AuthTokenError) as cm:
            inst.validate_and_return_id_token(self.id_token, self.access_token)

        self.assertEqual(str(cm.exception), 'Token error: Invalid signature')
