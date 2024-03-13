"""
********************************************************************************
* Name: unit_tests
* Author: nswain
* Created On: May 15, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

import uuid
import factory
from unittest import mock
from django.contrib.auth.models import User

import tethys_apps.base.app_base as tethys_app_base

# mock bokeh_django functionality
tethys_app_base.has_bokeh_django = True
tethys_app_base.autoload = mock.MagicMock(
    return_value=mock.MagicMock(app_context="app_context", url="basename")
)
tethys_app_base.WSConsumer = mock.MagicMock()
tethys_app_base.AutoloadJsConsumer = mock.MagicMock()


class UserFactory(factory.Factory):
    """
    Creates a new ``User`` object.
    Username will be a random 30 character md5 value.
    Email will be ``userN@example.com`` with ``N`` being a counter.
    Password will be ``test123`` by default.
    """

    class Meta:
        model = User
        abstract = False

    username = factory.LazyAttribute(lambda x: str(uuid.uuid4())[:30])
    email = factory.Sequence(lambda n: "user{0}@example.com".format(n))

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = "test123"
        if "password" in kwargs:
            password = kwargs.pop("password")
        user = super().prepare(create, **kwargs)
        user.set_password(password)
        if create:
            user.save()
        return user
