from setuptools import setup, find_namespace_packages
from tethys_apps.app_installation import find_all_resource_files
from tethys_apps.base.app_base import TethysExtensionBase

# -- Extension Definition -- #
ext_package = 'test_extension'
release_package = f'{TethysExtensionBase.package_namespace}-{ext_package}'

# -- Python Dependencies -- #
dependencies = []

# -- Get Resource File -- #
resource_files = find_all_resource_files(ext_package, TethysExtensionBase.package_namespace)

setup(
    name=release_package,
    version='0.0.0',
    description='',
    long_description='',
    keywords='',
    author='',
    author_email='',
    url='',
    license='',
    packages=find_namespace_packages(),
    package_data={'': resource_files},
    include_package_data=True,
    zip_safe=False,
    install_requires=dependencies
)
