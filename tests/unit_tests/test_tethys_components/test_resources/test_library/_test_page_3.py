def page_test(lib):
    """This comment is here as a test to ensure certain code gets executed"""
    # Register additional packages
    lib.register(
        package="fake-package", accessor="fp", styles=["style1.css", "style2.css"]
    )

    # Event handlers
    def handle_on_ready(e):
        print("Your video is ready.")

    # Layout
    return lib.html.div()(
        lib.rp.ReactPlayer(
            url="https://www.youtube.com/watch?v=xvFZjo5PgG0", onReady=handle_on_ready
        )
    )
