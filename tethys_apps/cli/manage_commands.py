import os
import shutil


def pre_collectstatic(installed_apps, static_root):
    """
    Symbolically link the static directories of each app into the static/public directory specified by the STATIC_ROOT
    parameter of the settings.py. Do this prior to running Django's collectstatic method.
    """
    # Provide feedback to user
    print('INFO: Linking static and public directories of apps to "{0}".'.format(static_root))

    for app, path in installed_apps.iteritems():
        # Check for both variants of the static directory (public and static)
        public_path = os.path.join(path, 'public')
        static_path = os.path.join(path, 'static')
        static_root_path = os.path.join(static_root, app)

        # Clear out old symbolic links/directories if necessary
        try:
            os.remove(static_root_path)
        except OSError:
            # Remove directory
            shutil.rmtree(static_root_path)

        # Create appropriate symbolic link
        if os.path.isdir(public_path):
            os.symlink(public_path, static_root_path)
            print('INFO: Successfully linked public directory to STATIC_ROOT for app "{0}".'.format(app))

        elif os.path.isdir(static_path):
            os.symlink(static_path, static_root_path)
            print('INFO: Successfully linked static directory to STATIC_ROOT for app "{0}".'.format(app))