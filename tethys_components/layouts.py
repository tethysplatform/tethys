def NavHeader(lib, app, user, nav_links=None, content=None):
    nav_links = nav_links or []
    content = content or []
    if not isinstance(content, list):
        content = [content]

    return lib.html.div(style=lib.Style(height="100%", width="100%"))(
        lib.tethys.HeaderWithNavBar(app=app, user=user, nav_links=nav_links),
        lib.html.div(
            style=lib.Style(position="absolute", top="56px", bottom=0, right=0, left=0)
        )(*content),
    )
