import logging
import requests_mock
import uuid
import random

from django.test import TestCase
from django.contrib.auth.models import User

from social.p3 import urlparse
from social.actions import do_auth, do_complete, do_disconnect
from social.utils import module_member, parse_qs
from social.strategies.django_strategy import DjangoStrategy
from social.apps.django_app.default.models import DjangoStorage, UserSocialAuth


logger = logging.getLogger(__name__)


@requests_mock.Mocker()
class HydroShareBackendTest(TestCase):
    """
    This test case creates a mock-up for HydroShare OAuth Server that returns pre-defined access_token
    as well as other oauth parameters. No real external call happens.

    The code was inspired and modified from test cases of python-social-oauth (PSA). The 'requests_mock' lib is
    used instead of 'httpretty' (used in PSA) as we found 'httpretty' is incompatible to 'pyOpenSSL'
    lib (a dependency of tethys cluster/compute lib), which caused a strange error:
    "SSLError: ("bad handshake: SysCallError(32, 'EPIPE')",)".

    Currently three scenarios are tested:
    1) tethys creates a new user after a success oauth login;
    2) tethys create a new user with a random string appended to its username to avoid duplication;
    3) connect/disconnect social account to/from an existing user;

    """

    def setUp(self):

        self.backend_module_path = "tethys_services.backends.hydroshare.HydroShareOAuth2"
        self.Backend_Class = module_member(self.backend_module_path)
        self.client_complete_url = "https://apps.hydroshare.org/complete/hydroshare/"

        self.access_token = str(uuid.uuid4())
        self.refresh_token = str(uuid.uuid4())
        self.expires_in = random.randint(1, 30*60*60)  # 1 sec to 30 days
        self.token_type = "bearer"
        self.scope = "read write"

        self.social_username="drew"
        self.social_email="drew@byu.edu"

    def tearDown(self):
        pass

    def test_oauth_create_new_user(self, m):
        # test: oauth should create a new user

        # expect for only 1 user: anonymous user
        self.assertEqual(User.objects.all().count(), 1)

        username_new, social, backend=self.run_oauth(m)

        # expect for 2 users: anonymous and newly created social user
        self.assertEqual(User.objects.all().count(), 2)
        self.assertEqual(User.objects.filter(username=self.social_username).count(), 1)
        user = User.objects.filter(username=self.social_username).first()
        self.assertEqual(user.email, self.social_email)

        # check extra_data
        extra_data_dict = social.extra_data
        self.assertEqual(extra_data_dict["access_token"], self.access_token)
        self.assertEqual(extra_data_dict["refresh_token"], self.refresh_token)
        self.assertEqual(extra_data_dict["expires_in"], self.expires_in)
        self.assertEqual(extra_data_dict["token_type"], self.token_type)
        self.assertEqual(extra_data_dict["scope"], self.scope)

    def test_oauth_avoid_duplicate_user(self, m):
        # test: if django already has a user with the same username as social_user,
        #       to avoid duplication, a new user should be created with a random string
        #       appended to its username

        # expect for only 1 user: anonymous user
        self.assertEqual(User.objects.all().count(), 1)
        # manually create a new user named self.social_username
        self.user = User.objects.create_user(username=self.social_username,
                                             email=self.social_email,
                                             password='top_secret')
        # expect for 2 users: anonymous and self.social_username
        self.assertEqual(User.objects.all().count(), 2)

        username_new, social, backend = self.run_oauth(m)

        # expect for 3 users
        self.assertEqual(User.objects.all().count(), 3)

        # test username
        self.assertEqual(User.objects.filter(username=username_new).count(), 1)
        self.assertTrue(len(username_new) > len(self.social_username))
        self.assertEqual(username_new[0:len(self.social_username)], self.social_username)

        # check extra_data
        extra_data_dict = social.extra_data
        self.assertEqual(extra_data_dict["access_token"], self.access_token)
        self.assertEqual(extra_data_dict["refresh_token"], self.refresh_token)
        self.assertEqual(extra_data_dict["expires_in"], self.expires_in)
        self.assertEqual(extra_data_dict["token_type"], self.token_type)
        self.assertEqual(extra_data_dict["scope"], self.scope)

    def test_oauth_connection_to_user(self, m):
        # tests: 1) connect social to an existing user
        #        2) disconnect social from the user

        # expect for only 1 user: anonymous user
        self.assertEqual(User.objects.all().count(), 1)
        # manually create a new user named self.social_username
        user_sherry = User.objects.create_user(username="sherry",
                                             email="sherry@byu.edu",
                                             password='top_secret')
        logger.debug(user_sherry.is_authenticated())
        logger.debug(user_sherry.is_active)

        # expect for 2 users: anonymous and sherry
        self.assertEqual(User.objects.all().count(), 2)

        username_new, social, backend = self.run_oauth(m, user=user_sherry)

        # still expect for 2 users
        self.assertEqual(User.objects.all().count(), 2)
        # check social is connected to user_sherry
        self.assertEqual(social.user, user_sherry)

        # check extra_data
        extra_data_dict = social.extra_data
        self.assertEqual(extra_data_dict["access_token"], self.access_token)
        self.assertEqual(extra_data_dict["refresh_token"], self.refresh_token)
        self.assertEqual(extra_data_dict["expires_in"], self.expires_in)
        self.assertEqual(extra_data_dict["token_type"], self.token_type)
        self.assertEqual(extra_data_dict["scope"], self.scope)

        # test disconnect
        self.assertEqual(UserSocialAuth.objects.count(), 1)
        do_disconnect(backend, user_sherry, association_id=social.id)
        self.assertEqual(UserSocialAuth.objects.count(), 0)

    def run_oauth(self, m, user=None):

        strategy = DjangoStrategy(DjangoStorage)
        backend = self.Backend_Class(strategy, redirect_uri=self.client_complete_url)

        start_url = do_auth(backend).url
        start_query = parse_qs(urlparse(start_url).query)

        # set 'state' in client
        backend.data.update({'state': start_query['state']})

        m.get(backend.USER_DATA_URL,
              json={"username": self.social_username,
                    "email": self.social_email},
              status_code=200)

        m.post(backend.ACCESS_TOKEN_URL,
               json={'access_token': self.access_token,
                     'token_type': self.token_type,
                     'expires_in': self.expires_in,
                     'scope': self.scope,
                     'refresh_token': self.refresh_token},
               status_code=200)

        def _login(backend, user, social_user):
            backend.strategy.session_set('username', user.username)

        do_complete(backend, user=user, login=_login)

        social = backend.strategy.storage.user.get_social_auth(backend.name, self.social_username)

        return strategy.session_get('username'), social, backend
