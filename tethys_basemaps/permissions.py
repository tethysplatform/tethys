"""
********************************************************************************
* Name: permissions.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""

CAPTURE_PERMISSION = "tethys_basemaps.add_basemapcapture"


def can_capture(user):
    """Check if the user has permission to capture basemaps."""
    if user is None or not user.is_authenticated or not user.is_active:
        return False
    return user.is_staff or user.has_perm(CAPTURE_PERMISSION)
