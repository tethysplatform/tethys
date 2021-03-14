***************************
Tethys Platform Translation
***************************

Tethys uses the `Django Translation <https://docs.djangoproject.com/en/2.2/topics/i18n/translation/>`_ to provide translation support.

Follow the steps below to add a new translation:
================================================

1. Add the new language code to tethys_portal/settings.py
---------------------------------------------------------

::

    ...

    LANGUAGES = [
        ('en', _('English')),
        ('es', _('Spanish')),
    ]

    ...

Language codes can be found `here <https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-LANGUAGE_CODE>`_.

2. Go to tethys home and run the following commands:
----------------------------------------------------

::

    $ conda activate tethys
    $ python tethys_portal/manage.py makemessages -l <LANGUAGE_CODE>

A .po file with the new language will be created at <TETHYS_HOME>/tethys_locale.

3. Navigate to the .po file and populate the file with translations.
--------------------------------------------------------------------

``#:/path/to/file:line`` shows the location of the text, ``msgid`` is the original text, ``msgstr`` is where the translation for that text should go.

::

    ...

    #: tethys_portal/templates/admin/base.html:69
    msgid "Home"
    msgstr "Inicio"

    ...

.. note::

    Translation block with a ``fuzzy`` key, require revision. Remove the ``fuzzy`` key after confirming it looks the way it should (e.g. not a duplicate).

4. Compile the .mo file:
------------------------

::

    $ conda activate tethys
    $ python tethys_portal/manage.py complilemessages
