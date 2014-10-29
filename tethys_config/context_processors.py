from .models import Setting


def tethys_global_settings_context(request):
    """
    Add the current Tethys app metadata to the template context.
    """

    # Get settings
    settings = Setting.as_dict()

    context = {'site_globals': settings}

    return context
