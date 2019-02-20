"""
********************************************************************************
* Name: django_user
* Author: nswain
* Created On: May 15, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""
import datetime
from hashlib import md5
import factory
from django.contrib.auth.models import User


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

    username = factory.LazyAttribute(
        lambda x: md5(datetime.datetime.now().strftime('%Y%,%d%H%M%S').encode('utf-8')).hexdigest()[0:30]
    )
    email = factory.Sequence(lambda n: 'user{0}@example.com'.format(n))

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = 'test123'
        if 'password' in kwargs:
            password = kwargs.pop('password')
        user = super().prepare(create, **kwargs)
        user.set_password(password)
        if create:
            user.save()
        return user
