"""
*******************************************************************************
* Name: tokenauth.py
* Author: Michael Souffront
* Created On: February 15, 2017
* Copyright: (c) Brigham Young University 2017
* License: BSD 2-Clause
*******************************************************************************
"""

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

class TokenBackend(ModelBackend):
    def authenticate(self, token=None):
        try:
            user = User.objects.get(auth_token=token)
        except User.DoesNotExist:
            return None
        if user is not None: 
            return user
        else:
            return None