from os import devnull
from pathlib import Path
import subprocess
import sys

import pytest

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
        setup_path = tests_path / "apps" / "tethysapp-test_app"
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            stdout=FNULL,
            stderr=subprocess.STDOUT,
            cwd=str(setup_path),
            check=True,
        )
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
            [sys.executable, "-m", "pip", "install", "-e", "."],
            stdout=FNULL,
            stderr=subprocess.STDOUT,
            cwd=str(setup_path),
            check=True,
        )
        write_warning("Test Extension installed successfully.")


def remove_prereqs():
    FNULL = open(devnull, "w")
    # Remove Test App
    write_warning("Uninstalling Test App...")
    try:
        subprocess.run(["tethys", "uninstall", "test_app", "-f"], stdout=FNULL)
        write_warning("Test App uninstalled successfully.")
    except Exception:
        pass

    # Remove Test Extension
    write_warning("Uninstalling Test Extension...")
    try:
        subprocess.run(["tethys", "uninstall", "test_extension", "-f"], stdout=FNULL)
        write_warning("Test Extension uninstalled successfully.")
    except Exception:
        pass


@pytest.fixture(scope="session")
def test_dir():
    """Get path to the 'tests' directory"""
    return Path(__file__).parents[1].resolve()


@pytest.fixture(scope="session", autouse=True)
def global_setup_and_teardown(test_dir):
    """Install and remove test apps and extensions before and after tests run."""
    install_prereqs(test_dir)
    yield
    remove_prereqs()
