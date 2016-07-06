"""
********************************************************************************
* Name: tests.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User


class LoginTestCase(TestCase):
    """
    Tests for the login view
    """
    def setUp(self):
        """
        Perform the work that every test will need.
        """
        # Create client
        self.client = Client()

        # Create test users
        User.objects.create(username='darth_vadar', password='darthpass', email='darth@deathstar.com', is_active=False)
        User.objects.create(username='han_solo', password='hanpass', email='han@meleniumfalcon.com', is_active=True)

    def login_active_user_correct_credentials(self):
        """
        Active user with correct credentials
        """
        form_data = {'username': 'han_solo',
                     'password': 'hanpass'}

        action_url = reverse('accounts:login')

        response = self.client.post(action_url, form_data)

        self.assertEqual(response.status_code, 200)
        print(response.context)