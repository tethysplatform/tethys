from django.shortcuts import render
from tethys_sdk.permissions import login_required
from tethys_sdk.gizmos import Button

from channels.generic.websocket import WebsocketConsumer
import json

from typing import Any

from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.embed import server_document


@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    save_button = Button(
        display_text='',
        name='save-button',
        icon='glyphicon glyphicon-floppy-disk',
        style='success',
        attributes={
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'Save'
        }
    )

    edit_button = Button(
        display_text='',
        name='edit-button',
        icon='glyphicon glyphicon-edit',
        style='warning',
        attributes={
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'Edit'
        }
    )

    remove_button = Button(
        display_text='',
        name='remove-button',
        icon='glyphicon glyphicon-remove',
        style='danger',
        attributes={
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'Remove'
        }
    )

    previous_button = Button(
        display_text='Previous',
        name='previous-button',
        attributes={
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'Previous'
        }
    )

    next_button = Button(
        display_text='Next',
        name='next-button',
        attributes={
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'Next'
        }
    )

    script = server_document(request.build_absolute_uri())

    context = {
        'save_button': save_button,
        'edit_button': edit_button,
        'remove_button': remove_button,
        'previous_button': previous_button,
        'next_button': next_button,
        'script': script
    }

    return render(request, 'test_app/home.html', context)


def home_handler(doc):
    data = {'x': [0, 1, 2, 3, 4, 5], 'y': [0, 10, 20, 30, 40, 50]}
    source = ColumnDataSource(data=data)

    plot = figure(x_axis_type="linear", y_range=(0, 50), title="Test App Bokeh + Channels Plot", height=250)
    plot.line(x="x", y="y", source=source)

    def callback(attr: str, old: Any, new: Any) -> None:
        if new == 1:
            data['y'] = [0, 10, 20, 30, 40, 50]
        else:
            data['y'] = [i * new for i in [0, 10, 20, 30, 40, 50]]
        source.data = dict(ColumnDataSource(data=data).data)
        plot.y_range.end = max(data['y'])

    slider = Slider(start=1, end=5, value=1, step=1, title="Test App Bokeh + Channels Controller")
    slider.on_change("value", callback)

    doc.add_root(column(slider, plot))


class TestWS(WebsocketConsumer):
    def connect(self):
        self.accept()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['client_message']

        self.send(text_data=json.dumps({
            'server_message': message
        }))

    def disconnect(self, close_code):
        pass
