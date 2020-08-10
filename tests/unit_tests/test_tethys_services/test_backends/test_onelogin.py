import unittest
from unittest import mock
from django import test
from jose import jwk, jwt
import datetime as dt
from tethys_services.backends.onelogin import OneLoginOIDC


@test.override_settings(
    SOCIAL_AUTH_ONELOGIN_OIDC_KEY='182f8cb0-b8b2-0138-3936-0647e35409d7171986',
    SOCIAL_AUTH_ONELOGIN_OIDC_SECRET='032f86d0f5f367171fd6270f7f5fa383fa27604fake9c5f1a0a5d5d2b4227ace',
    SOCIAL_AUTH_ONELOGIN_OIDC_SUBDOMAIN='https://my-org.onelogin.mok'
)
class OneLoginOIDCBackendTest(test.SimpleTestCase):

    def setUp(self):
        pass

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

    # def test_find_valid_key(self):
    #     inst = OneLoginOIDC()
    #     test_private_key = {
    #         "p": "4r8B8ToefXmlwkJ0EEC5FH8fHDCIEv9uz_Gq-I4jAmcIh-P1QAS2KdEsUHhAp9Sz9JX76-uK5blzkRwYaAGUTx11BYaH3eFogiL0AvuyE1B8IuTc_7l7JYVP3ehmPDmjpW5ISPhQ-mug4ppm9xvsFX5ERBoSMhJGH6w1iAanLn0",
    #         "kty": "RSA",
    #         "q": "stC1jeWWHIvCY96eae3m5Y1irJNfvROrpeqG4oL1ppd6iQlu20BJhllr4gufeZR9CdAXsBJgyep1MznsDzlDyvWHSvk83ZX55hAoVWWcWefC_R-dsSGA7BVMjpgovc-oe_73luK0TkGKVo0iCCru3_uQGckFO-PwB94711Zpoqc",
    #         "d": "eUOKsLspFWmUQJiUMHmyjU4Uo14vl19I5QG_cNPiF7L0zXTNT7MPAdg4YoNDKFirOT72ZnpMwsJTmmJeri2tS7TyOvIzm9IDnxCuhecN0-yVJ6yHMUvcNOYDn6wllaf1fuLcDCM3prXQ9DqTrwBz0rUWr-WFl_s8qu_prmgov3tNgLOTOBjzbZv_BaKuZqqDMs1YAkyDogfmgU7gy_N-ok08jQK1tRlsKHdXGtK_DDmy9K5GKlwlE7fm47UqrGq1CVMMop6b8nF2DKqvWTbKqH80nqHqbEM3rhrGsLZ4tPSoeDqcF0rlHgn77KhSJ0E6dJ4qzm3ytLyjLHAFgEvY0Q",
    #         "e": "AQAB",
    #         "use": "sig",
    #         "kid": "_DVFG_Bmcv-2V1FUjVSmcnlcdhGnpVzd3SUaYAG9DeE",
    #         "qi": "WnuwFnWp2FKpJ-Pc4h3sVAi-Tyqqsy9SQk7M4PjOpGbBYH6IooTPohFVWTJvf3Ya31dwq0OZ3_9SAchuYhW9gGrsL140tMQzNeiFb4MkDBRu0xxwEn1jOIt85pJHQeZb3uX4sYaxzWp76H4Te77cdg-Em-iMnws9_3H1ZKYBPuM",
    #         "dp": "W0CxwGo6cRbu7cIewZe6pJQQaiDh8ntYFlnVC9jwH_xlQ4MrZUtAII4s_mmW47RHhAyEaUrPCGrdJq4e6GSSUlCxkrq0nUgk7hKxDy5KWVmPy989TbFQ7SW8obrwwhYUVPSQJMXCmTWNdwTaoWJcXb4GLT4synfuPrrohEjhKWU",
    #         "alg": "RS256",
    #         "dq": "cFP9iOrNVpdRAM2q8943qsIbV0-o16zQqgRewVIFIKaNmiIr2l1TEqt_wtsMTiLCPXTUPI3-8ThwcUKUkKend4qvd6CD5Kq-9g_2VlbjVfLqIXpH5CqowyVKF1VsWnhlXac4PzegjnxLe71iwIC_2EI-LoSB3jJ86WRocQheiYc",
    #         "n": "nmGrWglV3em0CNczEyQ6cQofK16ssefRkyPotTv2JCBZJDNb6DT4i7RsLEMBf3k_gdpYvQ6optiItmP7JVZKMBIcd7tshsIM9tQUzusM7D9uefu6pQzAhtzz-n0k77Ez8OZ-3gxyiS-Jhn4D0wCjB7Ah-7csfEj1p4RF_RdU3LZBaWW0GYNBFrgzMr5RSuyi4rSNOZjthnQaN4ZSgUmHTPUJCodqNuH2B8bq8oiaTH4EYUmCbLlT_Xtq0TJNds7YJfw7jJxuQBPUvzs4vO0FjpRFLa827CKblbSUekIw60Eon_eftF0rlJAtoKdtvVZUfeIzMqyANZ0jwr4dMb9tiw"
    #     }
    #
    #     test_pub_key = {
    #         "kty": "RSA",
    #         "e": "AQAB",
    #         "use": "sig",
    #         "kid": "_DVFG_Bmcv-2V1FUjVSmcnlcdhGnpVzd3SUaYAG9DeE",
    #         "alg": "RS256",
    #         "n": "nmGrWglV3em0CNczEyQ6cQofK16ssefRkyPotTv2JCBZJDNb6DT4i7RsLEMBf3k_gdpYvQ6optiItmP7JVZKMBIcd7tshsIM9tQUzusM7D9uefu6pQzAhtzz-n0k77Ez8OZ-3gxyiS-Jhn4D0wCjB7Ah-7csfEj1p4RF_RdU3LZBaWW0GYNBFrgzMr5RSuyi4rSNOZjthnQaN4ZSgUmHTPUJCodqNuH2B8bq8oiaTH4EYUmCbLlT_Xtq0TJNds7YJfw7jJxuQBPUvzs4vO0FjpRFLa827CKblbSUekIw60Eon_eftF0rlJAtoKdtvVZUfeIzMqyANZ0jwr4dMb9tiw"
    #     }
    #
    #     test_key = jwk.construct(test_private_key, 'RS256')
    #
    #     exp_dt = dt.datetime.utcnow() + dt.timedelta(seconds=30)  # expire 30 seconds from now
    #     epoch_dt = dt.datetime.utcfromtimestamp(0)
    #     test_payload = {
    #         'typ': 'id_token',
    #         'exp': (exp_dt - epoch_dt).total_seconds() * 1000.0
    #     }
    #     test_token = jwt.encode(test_payload, key=test_key, algorithm='RS256')
    #     inst.get_jwks_keys = mock.MagicMock(return_value=[test_pub_key])
    #
    #     ret = inst.find_valid_key(test_token)
    #     self.assertEqual(test_pub_key, ret)
    #
    # def test_validate_and_return_id_token(self):
    #     pass


