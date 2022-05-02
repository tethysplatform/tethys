.. _gizmo_slide_sheet:

***********
Slide Sheet
***********

**Last Updated:** March 2022

Python API
--------------

.. autoclass:: tethys_sdk.gizmos.SlideSheet

JavaScript API
--------------

The slide sheet can be opened and closed dynamically using the JavaScript API.

SLIDE_SHEET.open(id)
++++++++++++++++++++

Open the slide sheet gizmo with the given ID.

::

    $(function() { //wait for page to load
        SLIDE_SHEET.open('slide-sheet');
    });

SLIDE_SHEET.close(id)
+++++++++++++++++++++

Close the slide sheet gizmo with the given ID.

::

    $(function() { //wait for page to load
        SLIDE_SHEET.close('slide-sheet');
    });
