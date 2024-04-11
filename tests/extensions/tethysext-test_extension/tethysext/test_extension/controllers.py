from tethys_sdk.routing import controller
from .ext import Extension


@controller(
    url="test-extension/{var1}/{var2}",
)
def home(request, var1, var2):
    """
    Controller for the app home page.
    """
    context = {
        "var1": var1,
        "var2": var2,
    }

    return Extension.render(request, "home.html", context)
