from tethys_sdk.components import ComponentBase


class App(ComponentBase):
    pass


@App.page
def home(lib):
    return None


@App.page
def another_page(lib):
    return None
