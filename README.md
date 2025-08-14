<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tethysplatform/tethys/main/docs/images/features/tethys-on-blue.svg">
  <img alt="Tethys Platform Logo" src="https://raw.githubusercontent.com/tethysplatform/tethys/main/docs/images/features/tethys-on-white.svg">
</picture>

[![Test Status](https://github.com/tethysplatform/tethys/actions/workflows/tethys.yml/badge.svg)](https://github.com/tethysplatform/tethys/actions)
[![Coverage Status](https://coveralls.io/repos/github/tethysplatform/tethys/badge.svg?branch=main)](https://coveralls.io/github/tethysplatform/tethys?branch=main)
[![Documentation Status](https://readthedocs.org/projects/tethys-platform/badge/?version=stable)](http://docs.tethysplatform.org/en/stable/?badge=stable)

Tethys Platform provides both a development environment and a hosting environment for geoscientific web apps.

## Installation

### Quick Start

First create a virtual environment with the tool of your choice, then download and install Tethys Platform using one of the following methods:

**Using Conda (Recommended):**
```bash
conda install -c conda-forge tethys-platform
tethys quickstart
```

**Using Pip:**
```bash
pip install tethys-platform
tethys quickstart
```

The `tethys quickstart` command will set up your development environment and start the server. Your browser will automatically open to [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

**Default Login:**
- Username: admin
- Password: pass

### Detailed Installation

For more detailed installation instructions, including database configuration and production deployment, see our [Detailed Installation documentation](https://docs.tethysplatform.org/en/stable/installation.html).

## Next Steps

There are several directions you may want to go from here:

- **Learn to develop apps**: Complete one or more [Tutorials](https://docs.tethysplatform.org/en/stable/tutorials.html) to learn how to develop apps using Tethys Platform
- **See live examples**: Install the [Showcase Apps](https://docs.tethysplatform.org/en/stable/installation/showcase_apps.html) to see live demos and code examples of Gizmos and Layouts
- **Install existing apps**: Use the [Application Installation](https://docs.tethysplatform.org/en/stable/installation/application.html) guide to install apps you have already developed
- **Customize your portal**: Check out the [Web Admin Setup](https://docs.tethysplatform.org/en/stable/installation/web_admin_setup.html) docs to customize your Tethys Portal
- **Use Docker**: For help getting started with Docker, see [Using Docker](https://docs.tethysplatform.org/en/stable/installation/using_docker.html)
- **Full documentation**: Browse the complete [documentation](https://docs.tethysplatform.org/en/stable/) for comprehensive guides and API references

## Acknowledgments

This material is based upon work supported by the National Science Foundation under Grants [EPS-1135482](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1135482) and [TI-2303756](https://www.nsf.gov/awardsearch/showAward?AWD_ID=2303756).
