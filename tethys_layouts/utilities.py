class classproperty:
    """
    Decorator that converts a method with a single cls argument into a property
    that can be accessed directly from the class.

    Source: https://docs.djangoproject.com/en/3.2/_modules/django/utils/functional/#classproperty
    Remove after updating to Django 3.2.
    """
    def __init__(self, method=None):
        self.fget = method

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self
