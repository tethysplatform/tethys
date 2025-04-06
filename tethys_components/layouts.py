def NavHeader(lib, **kwargs):
    app = kwargs["app"]
    user = kwargs["user"]
    nav_links = kwargs.get("nav_links", [])
    content = kwargs.get("content")
    if not isinstance(content, list):
        content = [content]

    return lib.html.div(class_name="h-100")(
        lib.tethys.HeaderWithNavBar(app=app, user=user, nav_links=nav_links),
        lib.html.div(style=lib.Props(padding_top="56px"))(*content),
    )
