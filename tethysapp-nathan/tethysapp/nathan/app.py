from tethys_sdk.components import ReactPyBase


class App(ReactPyBase):
    """
    Tethys app class for Nathan.
    """

    name = "Nathan"
    description = ""
    package = "nathan"  # WARNING: Do not change this value
    index = "home"
    icon = f"{package}/images/icon.png"
    root_url = "nathan"
    color = "#718093"
    tags = ""
    enable_feedback = False
    feedback_emails = []
    exit_url = "/apps/"
    default_layout = "NavHeader"
    nav_links = "auto"


@App.page
def home(lib):
    map_center, set_map_center = lib.hooks.use_state([39.254852, -98.593853])
    map_zoom, set_map_zoom = lib.hooks.use_state(4)

    return lib.html.div(
        lib.pm.Map(
            height="calc(100vh - 62px)", defaultCenter=map_center, defaultZoom=map_zoom
        )
    )
