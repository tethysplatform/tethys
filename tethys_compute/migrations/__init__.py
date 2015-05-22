# from . import initialize_settings
# add the following  to operations in migrations
    # migrations.RunPython(initialize_settings),


def initialize_settings(apps, schema_editor):
    SettingsCategory = apps.get_model('tethys_compute', 'SettingsCategory')
    Setting = apps.get_model('tethys_compute', 'Setting')

    category = SettingsCategory(name='Cluster Management')
    category.save()
    for setting in ['SCHEDULER_IP', 'SCHEDULER_KEY_LOCATION', 'DEFAULT_CLUSTER']:
        s = Setting(name=setting, category=category)
        s.save()

    category = SettingsCategory(name='Amazon Credentials')
    category.save()
    for setting in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_USER_ID', 'KEY_NAME', 'KEY_LOCATION']:
        s = Setting(name=setting, category=category)
        s.save()

    category = SettingsCategory(name='Azure Credentials')
    category.save()
    for setting in['SUBSCRIPTION_ID', 'CERTIFICATE_PATH']:
        s = Setting(name=setting, category=category)
        s.save()