from django.shortcuts import render
from tethys_sdk.routing import controller


@controller(
    url='test-extension/{var1}/{var2}',
)
def home(request, var1, var2):
    """
    Controller for the app home page.
    """
    context = {
        'var1': var1,
        'var2': var2,
    }

    return render(request, 'test_extension/home.html', context)
