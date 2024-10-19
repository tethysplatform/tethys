# ********************************************************************************
# * Name: routing.py
# * Author: Scott Christensen
# * Created On: 14 March 2022
# * Copyright: (c) Brigham Young University 2015
# * License: BSD 2-Clause
# ********************************************************************************

# flake8: noqa
# DO NOT ERASE
from tethys_apps.base.controller import (
    TethysController,
    controller,
    page,
    consumer,
    handler,
    register_controllers,
)
from tethys_apps.base.mixins import (
    TethysAsyncWebsocketConsumerMixin,
    TethysWebsocketConsumerMixin,
)
from tethys_apps.base.bokeh_handler import with_request, with_workspaces
from tethys_apps.base.url_map import url_map_maker
