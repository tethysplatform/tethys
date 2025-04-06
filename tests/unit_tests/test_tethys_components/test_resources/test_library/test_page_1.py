def test(lib):
    lib.register("@monaco-editor/react", "me", default_export="Editor")

    return lib.html.div()(
        lib.bs.Container(fluid=True, style=lib.utils.Props(height="calc(100vh - 75px"))(
            lib.bs.Row()(lib.bs.Button()("Render")),
            lib.bs.Row()(
                lib.bs.Col(style=lib.Props(width="50vw"))(
                    lib.me.Editor(
                        height="80vh",
                        language="python",
                        theme="vs-dark",
                        value="",
                        options=lib.Props(
                            inlineSuggest=True, fontSize="16px", formatOnType=True
                        ),
                    )
                ),
                lib.bs.Col(style=lib.Props(width="50vw"))(
                    lib.html.iframe(
                        style=lib.Props(height="100%", width="100%"),
                        src="/apps/reactpy-playground/render",
                        title="Result",
                    )
                ),
            ),
            lib.bs.Row()(lib.bs.Button()("Render")),
        )
    )
