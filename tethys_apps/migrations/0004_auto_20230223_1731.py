# Generated by Django 3.2.16 on 2023-02-23 17:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_apps', '0003_alter_tethysapp_feedback_emails'),
    ]

    operations = [
        ## Rename Model 
        migrations.RenameModel('customsetting', 'oldcustomsetting'),

        migrations.CreateModel(
            name='CustomSettingBase',
            fields=[
                ('tethysappsetting_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tethys_apps.tethysappsetting')),
                ('type_custom_setting', models.CharField(blank=True, default='', max_length=1024)),
            ],
            bases=('tethys_apps.tethysappsetting',),
        ),
        # migrations.RemoveField(
        #     model_name='customsetting',
        #     name='tethysappsetting_ptr',
        # ),
        migrations.CreateModel(
            name='JSONCustomSetting',
            fields=[
                ('customsettingbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tethys_apps.customsettingbase')),
                ('value', models.JSONField(blank=True, default=dict)),
                ('default', models.JSONField(blank=True, default=dict)),
            ],
            bases=('tethys_apps.customsettingbase',),
        ),
        migrations.CreateModel(
            name='SecretCustomSetting',
            fields=[
                ('customsettingbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tethys_apps.customsettingbase')),
                ('value', models.CharField(blank=True, default='', max_length=1024)),
            ],
            bases=('tethys_apps.customsettingbase',),
        ),
        
        #create new CustomSetting 
        migrations.CreateModel(
            name='CustomSetting',
            fields=[
                ('customsettingbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tethys_apps.customsettingbase')),
                ('value', models.CharField(blank=True, default='', max_length=1024)),
                ('default', models.CharField(blank=True, default='', max_length=1024)),
                ('type', models.CharField(choices=[('STRING', 'String'), ('INTEGER', 'Integer'), ('FLOAT', 'Float'), ('BOOLEAN', 'Boolean'), ('UUID', 'UUID')], default='STRING', max_length=200)),
            ],
            bases=('tethys_apps.customsettingbase',),
        ),

        # migrations.AddField(
        #     model_name='customsetting',
        #     name='customsettingbase_ptr',
        #     field=models.OneToOneField(auto_created=True, default='', on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tethys_apps.customsettingbase'),
        #     preserve_default=False,
        # ),
    ]
