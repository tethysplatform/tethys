# Generated by Django 3.2.20 on 2024-08-30 18:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tethys_compute", "0001_initial_41"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tethysjob",
            options={
                "permissions": [
                    (
                        "jobs_table_actions",
                        "Can access job's table endpoints for all jobs.",
                    )
                ],
                "verbose_name": "Job",
            },
        ),
    ]
