from tethys_cli.settings_commands import read_settings, write_settings
tethys_settings = read_settings()
if 'INSTALLED_APPS' not in tethys_settings:
    tethys_settings['INSTALLED_APPS'] = []
if 'reactpy_django' not in tethys_settings['INSTALLED_APPS']:
    tethys_settings['INSTALLED_APPS'].append('reactpy_django')
    write_settings(tethys_settings)
