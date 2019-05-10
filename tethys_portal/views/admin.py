from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from tethys_apps.models import TethysApp
from tethys_apps.utilities import get_app_class
from tethys_apps.base.workspace import _get_app_workspace


@staff_member_required
def clear_workspace(request, app_id):
    """
    Handle clear workspace requests.
    """
    url = reverse('admin:tethys_apps_tethysapp_change', args=(app_id,))
    app = get_app_class(TethysApp.objects.get(id=app_id))

    # Handle form submission
    if request.method == 'POST' and 'clear-workspace-submit' in request.POST:
        workspace = _get_app_workspace(app)

        app.pre_delete_app_workspace()
        workspace.clear()
        app.post_delete_app_workspace()

        # Give feedback
        messages.success(request, 'Your workspace has been successfully cleared.')

        # Redirect to home
        return redirect(url)

    context = {'app_name': app.name, 'change_url': url}

    return render(request, 'tethys_portal/admin/tethys_app/clear_workspace.html', context)
