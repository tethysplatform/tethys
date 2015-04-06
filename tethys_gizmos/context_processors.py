


def tethys_gizmos_context(request):
    """
    Add the gizmos_rendered context to the global context.
    """

    # Setup variables
    context = {'gizmos_rendered': []}
    return context