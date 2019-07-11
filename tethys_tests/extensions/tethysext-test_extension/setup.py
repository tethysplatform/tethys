from setuptools import setup, find_namespace_packages
from tethys_apps.app_installation import find_resource_files

# -- Extension Definition -- #
ext_package = 'test_extension'
release_package = 'tethysext-' + ext_package

# -- Python Dependencies -- #
dependencies = []

# -- Get Resource File -- #
resource_files = find_resource_files('tethysext/' + ext_package + '/templates', 'tethysext/' + ext_package)
resource_files += find_resource_files('tethysext/' + ext_package + '/public', 'tethysext/' + ext_package)

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
