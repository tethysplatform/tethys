import os
from setuptools import setup, find_packages
from tethys_apps.app_installation import find_resource_files

# -- Extension Definition -- #
ext_package = 'test_extension'
release_package = 'tethysext-' + ext_package
ext_class = 'test_extension.ext:TestExtension'
ext_package_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tethysext', ext_package)

# -- Python Dependencies -- #
dependencies = []

# -- Get Resource File -- #
resource_files = find_resource_files('tethysext/' + ext_package + '/templates')
resource_files += find_resource_files('tethysext/' + ext_package + '/public')

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
    packages=find_packages(
        exclude=['ez_setup', 'examples', 'tethysext/' + ext_package + '/tests', 'tethysext/' + ext_package + '/tests.*']
    ),
    package_data={'': resource_files},
    namespace_packages=['tethysext', 'tethysext.' + ext_package],
    include_package_data=True,
    zip_safe=False,
    install_requires=dependencies,
)
