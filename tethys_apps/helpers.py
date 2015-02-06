import os


def get_tethysapp_dir():
    """
    Returns absolute path to the tethysapp directory.
    """
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tethysapp')


def get_installed_tethys_apps():
    """
    Returns a list apps installed in the tethysapp directory.
    """
    tethysapp_dir = get_tethysapp_dir()

    tethysapp_contents = os.listdir(tethysapp_dir)

    tethys_apps = {}

    for item in tethysapp_contents:
        item_path = os.path.join(tethysapp_dir, item)
        if os.path.isdir(item_path):
            tethys_apps[item] = item_path

    return tethys_apps