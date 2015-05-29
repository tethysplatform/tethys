# add the following  to operations in migrations
# from . import initialize_settings
    # migrations.RunPython(initialize_settings),


def initialize_settings(apps, schema_editor):
    SettingsCategory = apps.get_model('tethys_compute', 'SettingsCategory')
    Setting = apps.get_model('tethys_compute', 'Setting')

    category = SettingsCategory(name='Cluster Management')
    category.save()
    for setting in ['Scheduler IP', 'Scheduler Key Location', 'Default Cluster']:
        s = Setting(name=setting, category=category)
        s.save()

    category = SettingsCategory(name='Amazon Credentials')
    category.save()
    for setting in ['AWS Access Key ID', 'AWS Secret Access Key', 'AWS User ID', 'Key Name', 'Key Location']:
        s = Setting(name=setting, category=category)
        s.save()

    category = SettingsCategory(name='Azure Credentials')
    category.save()
    for setting in['Subscription ID', 'Certificate Path']:
        s = Setting(name=setting, category=category)
        s.save()

def clear_settings(apps, schema_edititor):
    SettingsCategory = apps.get_model('tethys_compute', 'SettingsCategory')
    Setting = apps.get_model('tethys_compute', 'Setting')

    SettingsCategory.objects.all().delete()
    Setting.objects.all().delete()