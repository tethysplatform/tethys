from reactpy import html, component
import json
from reactpy_django.components import django_js
from tethys_portal.dependencies import vendor_static_dependencies

vendor_js_dependencies = (vendor_static_dependencies["select2"].js_url,)
vendor_css_dependencies = (vendor_static_dependencies["select2"].css_url,)
gizmo_js_dependencies = ("tethys_gizmos/js/select_input.js",)


@component
def RESelectInput(
    name,
    display_text="",
    initial=None,
    multiple=False,
    original=False,
    select2_options=None,
    options="",
    disabled=False,
    error="",
    success="",
    attributes=None,
    classes="",
    on_change=None,
    on_click=None,
    on_mouse_over=None,
):
    # Setup/Fix variables and kwargs
    initial = initial or []
    initial_is_iterable = isinstance(initial, (list, tuple, set, dict))
    placeholder = False if select2_options is None else "placeholder" in select2_options
    select2_options = json.dumps(select2_options)

    # Setup div that will potentially contain the label, select input, and valid/invalid feedback
    return_div = html.div()
    return_div["children"] = []

    # Add label to return div if a display text is given
    if display_text:
        return_div["children"].append(
            html.label({"class_name": "form-label", "html_for": name}, display_text)
        )

    # Setup the select input attributes
    select_classes = "".join(
        [
            "form-select" if original else "tethys-select2",
            " is-invalid" if error else "",
            " is-valid" if success else "",
            f" {classes}" if classes else "",
        ]
    )
    select_style = {} if original else {"width": "100%"}
    select_attributes = {
        "id": name,
        "class_name": select_classes,
        "name": name,
        "style": select_style,
        "multiple": multiple,
        "disabled": disabled,
    }
    if select2_options:
        select_attributes["data-select2-options"] = select2_options
    if on_change:
        select_attributes["on_change"] = on_change
    if on_click:
        select_attributes["on_click"] = on_click
    if on_mouse_over:
        select_attributes["on_mouse_over"] = on_mouse_over
    if attributes:
        for key, value in attributes.items():
            select_attributes[key] = value

    # Create the select input with the associated attributes
    select = html.select(
        select_attributes,
    )

    # Add options to the select input if they are provided
    if options:
        if placeholder:
            select["children"] = [html.option()]
        else:
            select["children"] = []

        for option, value in options:
            select_option = html.option({"value": value}, option)
            if initial_is_iterable:
                if option in initial or value in initial:
                    select_option["attributes"]["selected"] = "selected"
            else:
                if option == initial or value == initial:
                    select_option["attributes"]["selected"] = "selected"
            select["children"].append(select_option)

    # Create the div for the select input
    input_group_classes = "".join(
        ["input-group mb-3", " has-validation" if error or success else ""]
    )
    input_group = html.div(
        {"class_name": input_group_classes},
        select,
    )

    # add invalid-feedback div to the select input group if needed
    if error:
        input_group["children"].append(
            html.div({"class_name": "invalid-feedback"}, error)
        )

    # add valid-feedback div to the select input group if needed
    if success:
        input_group["children"].append(
            html.div({"class_name": "valid-feedback"}, success)
        )
        
    # add select input group div to the returned div
    return_div["children"].append(input_group)

    # reload any gizmo JS dependencies after the react renders. This is required for the select2 dropdown to work
    for gizmo_js in gizmo_js_dependencies:
        return_div["children"].append(django_js(gizmo_js))

    return return_div
