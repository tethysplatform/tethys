"""
********************************************************************************
* Name: urls.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""

from django.urls import path

from tethys_basemaps import views

urlpatterns = [
    path("images/<int:image_id>/tiles/<int:z>/<int:x>/<int:y>", views.image_tile, name="image_tile"),
    path("images/<int:image_id>/source/", views.original_image, name="original_image"),
    path("images/<int:image_id>/cancel/", views.image_cancel, name="image_cancel"),
    path("<int:basemap_id>/status/", views.basemap_status, name="basemap_status")
]