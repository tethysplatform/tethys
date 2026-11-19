"""
********************************************************************************
* Name: utilities.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""


def get_app_basemaps(app):
    """
    MapView basemap definitions for the portal basemaps chosen for an app
    on its settings page.

    Args:
        app: A TethysApp database object, an app class (TethysAppBase subclass), or None.

    Returns:
        list<dict>: Basemap definitions to add to a MapView's basemap list.
    """
    from tethys_basemaps.models import BasemapCapture, BasemapImage

    if app is None:
        return []
    # MapLayout.app is the app class; get_active_app() returns the database row
    db_app = app.db_object if hasattr(app, "db_object") else app

    # Only the basemaps selected for this app (the apps M2M on PortalBasemap)
    assigned = db_app.portal_basemaps.select_related(
        "portalbasemapsource", "basemapcapture"
    ).order_by("name")

    basemaps = []
    for basemap in assigned:
        source = getattr(basemap, "portalbasemapsource", None)
        capture = getattr(basemap, "basemapcapture", None)
        image = getattr(basemap, "basemapimage", None)
        if source is not None:
            basemaps.append(source.format_options())
        elif (
            capture is not None and capture.status == BasemapCapture.StatusChoices.READY
        ):
            basemaps.append(capture.as_basemap())
        elif image is not None and image.status == BasemapImage.StatusChoices.READY:
            basemaps.append(image.as_basemap())
    return basemaps
