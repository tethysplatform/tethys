# Generated by Django 3.2.23 on 2024-04-01 20:32

from django.db import migrations, models


def forward(apps, schema_editor):
    """From proxyapp with logo_url field to icon field"""
    ProxyApp = apps.get_model("tethys_apps", "proxyapp")

    db_alias = schema_editor.connection.alias

    for cs in ProxyApp.objects.using(db_alias).all():
        cs.icon = cs.logo_url
        cs.save()


def backward(apps, schema_editor):
    """From proxyapp with icon field to logo_url field"""
    ProxyApp = apps.get_model("tethys_apps", "proxyapp")

    db_alias = schema_editor.connection.alias

    for cs in ProxyApp.objects.using(db_alias).all():
        cs.logo_url = cs.icon
        cs.save()


class Migration(migrations.Migration):
    dependencies = [
        ("tethys_apps", "0005_customsettingbase_include_in_api"),
    ]

    operations = [
        migrations.AddField(
            model_name="proxyapp",
            name="icon",
            field=models.CharField(default="", max_length=512),
        ),
        migrations.RunPython(forward, backward),
        migrations.RemoveField(
            model_name="proxyapp",
            name="logo_url",
        ),
    ]
