"""
********************************************************************************
* Name: app_installation.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
import os
import shutil
import subprocess
from setuptools.command.develop import develop
from setuptools.command.install import install
from sys import platform as _platform
import ctypes
from termcolor import colored


def get_tethysapp_directory():
    """
    Return the absolute path to the tethysapp directory.
    """
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tethysapp')

def get_tethys_processes_directory():
    """
    Return the absolute path to the tethys_wps directory.
    """
    return os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'tethys_wps/processes')


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
	os_symlink = getattr(os,"symlink",None)
	if callable(os_symlink):
	    os.symlink(self.app_package_dir, destination_dir)
	else:
	    def symlink_ms(source,dest):
		csl = ctypes.windll.kernel32.CreateSymbolicLinkW
		csl.argtypes = (ctypes.c_wchar_p,ctypes.c_wchar_p,ctypes.c_uint32)
		csl.restype = ctypes.c_ubyte
		flags = 1 if os.path.isdir(source) else 0
		if csl(dest,source.replace('/','\\'),flags) == 0:
                   raise ctypes.WinError()
	    os.symlink = symlink_ms(self.app_package_dir, destination_dir)
    except Exception as e:
	print(e)
        try:
            shutil.rmtree(destination_dir)
        except Exception as e:
            os.remove(destination_dir)

        os.symlink(self.app_package_dir, destination_dir)

    # Get tethys app wps process file path
    app_process_name = self.app_package.replace('_', '').lower()
    app_process_file = app_process_name + '_process.py'
    app_process_full_path = os.path.join(self.app_package_dir, app_process_file)

    if os.path.exists(app_process_full_path):
        try:
            # Get tethys pywps processes folder and __init__ file path
            tethys_wps_processes_dir = get_tethys_processes_directory()
            pywps_destination_path = os.path.join(tethys_wps_processes_dir, app_process_file)

            # Copy the process file
            print('Creating Symbolic Link to WPS processes folder: {0} to {1}'.format(app_process_full_path,
                                                                                      pywps_destination_path))
            os.symlink(app_process_full_path, pywps_destination_path)

        except:
            try:
                shutil.rmtree(pywps_destination_path)
            except:
                os.remove(pywps_destination_path)

            os.symlink(app_process_full_path, pywps_destination_path)
    else:
        print(colored("Notice: no WPS process file found in this project.", color='red'))

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