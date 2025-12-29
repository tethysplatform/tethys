from os import devnull
from pathlib import Path
import subprocess
import sys

import pytest

from tethys_apps.models import TethysApp
from tethys_cli.cli_colors import write_warning


def install_prereqs(tests_path):
    FNULL = open(devnull, "w")
    # Install the Test App if not Installed
    try:
        import tethysapp.test_app  # noqa: F401

        if tethysapp.test_app is None:
            raise ImportError
    except ImportError:
        write_warning("Test App not found. Installing.....")
        setup_path = Path(tests_path) / "apps" / "tethysapp-test_app"
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "."],
            stdout=FNULL,
            stderr=subprocess.STDOUT,
            cwd=str(setup_path),
            check=True,
        )
        import tethysapp.test_app  # noqa: F401

        write_warning("Test App installed successfully.")

    # Install the Test Extension if not Installed
    try:
        import tethysext.test_extension  # noqa: F401

        if tethysext.test_extension is None:
            raise ImportError
    except ImportError:
        write_warning("Test Extension not found. Installing.....")
        setup_path = Path(tests_path) / "extensions" / "tethysext-test_extension"
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "."],
            stdout=FNULL,
            stderr=subprocess.STDOUT,
            cwd=str(setup_path),
            check=True,
        )
        import tethysext.test_extension  # noqa: F401

        write_warning("Test Extension installed successfully.")


def remove_prereqs():
    FNULL = open(devnull, "w")
    # Remove Test App
    write_warning("Uninstalling Test App...")
    try:
        subprocess.run(["tethys", "uninstall", "test_app", "-f"], stdout=FNULL)
        write_warning("Test App uninstalled successfully.")
    except Exception:
        write_warning("Failed to uninstall Test App.")

    # Remove Test Extension
    write_warning("Uninstalling Test Extension...")
    try:
        subprocess.run(["tethys", "uninstall", "test_extension", "-f"], stdout=FNULL)
        write_warning("Test Extension uninstalled successfully.")
    except Exception:
        write_warning("Failed to uninstall Test Extension.")


@pytest.fixture(scope="session")
def test_dir():
    """Get path to the 'tests' directory"""
    return Path(__file__).parents[1].resolve()


@pytest.fixture(scope="session", autouse=True)
def global_setup_and_teardown(test_dir):
    """Install and remove test apps and extensions before and after tests run."""
    print("\n🚀 Starting global test setup...")
    install_prereqs(test_dir)
    print("✅ Global test setup completed!")
    yield
    print("\n🧹 Starting global test teardown...")
    remove_prereqs()
    print("✅ Global test teardown completed!")


def _reload_urlconf(urlconf=None):
    from django.conf import settings
    from django.urls import clear_url_caches
    from importlib import reload, import_module

    clear_url_caches()
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        reload(sys.modules[urlconf])
    else:
        import_module(urlconf)

    if "tethys_apps.urls" in sys.modules:
        reload(sys.modules["tethys_apps.urls"])
    else:
        import_module("tethys_apps.urls")


@pytest.fixture
def reload_urls():
    return _reload_urlconf


def _test_app():
    from tethys_apps.harvester import SingletonHarvester

    harvester = SingletonHarvester()
    harvester.harvest()
    _reload_urlconf()
    return TethysApp.objects.get(package="test_app")


@pytest.fixture(scope="function")
def lazy_test_app():
    return _test_app


@pytest.fixture(scope="function")
def test_app():
    return _test_app()
