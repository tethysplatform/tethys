from django.shortcuts import render
from tethys_sdk.permissions import login_required


@login_required()
def home(request, var1, var2):
    """
    Controller for the app home page.
    """
    context = {
        'var1': var1,
        'var2': var2,
    }

    return render(request, 'test_extension/home.html', context)
