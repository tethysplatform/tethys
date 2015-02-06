import os
import shutil
import subprocess

from setuptools.command.develop import develop
from setuptools.command.install import install


def get_tethysapp_directory():
    """
    Return the absolute path to the tethysapp directory.
    """
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tethysapp')


def _run_install(self):
    """
    The definition of the "run" method for the CustomInstallCommand metaclass.
    """
    # Get paths
    tethysapp_dir = get_tethysapp_directory()
    destination_dir = os.path.join(tethysapp_dir, self.app_package)

    # Notify user
    print('Copying App Package: {0} to {1}'.format(self.app_package_dir, destination_dir))

    # Copy files
    try:
        shutil.copytree(self.app_package_dir, destination_dir)

    except:
        try:
            shutil.rmtree(destination_dir)
        except:
            os.remove(destination_dir)

        shutil.copytree(self.app_package_dir, destination_dir)

    # Install dependencies
    for dependency in self.dependencies:
        subprocess.call(['pip', 'install', dependency])

    # Run the original install command
    install.run(self)


def _run_develop(self):
    """
    The definition of the "run" method for the CustomDevelopCommand metaclass.
    """
    # Get paths
    tethysapp_dir = get_tethysapp_directory()
    destination_dir = os.path.join(tethysapp_dir, self.app_package)

    # Notify user
    print('Creating Symbolic Link to App Package: {0} to {1}'.format(self.app_package_dir, destination_dir))

    # Create symbolic link
    try:
        os.symlink(self.app_package_dir, destination_dir)

    except:
        try:
            shutil.rmtree(destination_dir)
        except:
            os.remove(destination_dir)

        os.symlink(self.app_package_dir, destination_dir)

    # Install dependencies
    for dependency in self.dependencies:
        subprocess.call(['pip', 'install', dependency])

    # Run the original develop command
    develop.run(self)


def custom_install_command(app_package, app_package_dir, dependencies):
    """
    Returns a custom install command class that is tailored for the app calling it.
    """
    # Define the properties (and methods) for the class that will be created.
    properties = {'app_package': app_package,
                  'app_package_dir': app_package_dir,
                  'dependencies': dependencies,
                  'run': _run_install}

    return type('CustomInstallCommand', (install, object), properties)


def custom_develop_command(app_package, app_package_dir, dependencies):
    """
    Returns a custom develop command class that is tailored for the app calling it.
    """
    # Define the properties (and methods) for the class that will be created.
    properties = {'app_package': app_package,
                  'app_package_dir': app_package_dir,
                  'dependencies': dependencies,
                  'run': _run_develop}

    return type('CustomDevelopCommand', (develop, object), properties)