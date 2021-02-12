from django.conf import settings
from django.contrib.auth.views import PasswordResetView

from_email_address = settings.EMAIL_HOST_USER
if '@' not in from_email_address:
    from_email_address = settings.DEFAULT_FROM_EMAIL
# This removes the first and last angle brackets if email format is <foo@email.com>
# and is for Tethys backwards compatibility
if from_email_address[0] == '<':
    from_email_address = from_email_address[1:len(from_email_address)]
if from_email_address[len(from_email_address) - 1] == '>':
    from_email_address = from_email_address[0:len(from_email_address) - 1]
from_email = f"{settings.EMAIL_FROM} <{from_email_address}>".strip()


class TethysPasswordResetView(PasswordResetView):
    # Subclass Django's PasswordResetView and override the 'from_email' form input
    # This now uses the same settings format as django-mfa2
    from_email = from_email
