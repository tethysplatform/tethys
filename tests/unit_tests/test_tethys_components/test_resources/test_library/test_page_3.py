def test(lib):
    lib.register(
        package="fake-package", accessor="fp", styles=["style1.css", "style2.css"]
    )

    def handle_on_ready(e):
        print("Your video is ready.")

    return lib.html.div()(
        lib.rp.ReactPlayer(
            url="https://www.youtube.com/watch?v=xvFZjo5PgG0", onReady=handle_on_ready
        )
    )
