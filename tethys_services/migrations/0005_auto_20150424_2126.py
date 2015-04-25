# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from itertools import izip

from django.db import migrations, connection
from django.db.utils import ProgrammingError, InternalError


def query_to_dicts(query_string, *query_args):
    """
    Utility that converts raw Django query to dictionary.
    """
    cursor = connection.cursor()
    cursor.execute(query_string, query_args)
    col_names = [desc[0] for desc in cursor.description]
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        row_dict = dict(izip(col_names, row))
        yield row_dict
    return


def migrate_to_services(apps, schema_editor):
    """
    Move data from old tethys_datasets and tethys_wps tables to the new unified tethys_services tables if they exist.
    """
    # Legacy table names
    DATASET_SERVICE_TABLE = 'tethys_datasets_datasetservice'
    SPATIAL_DATASET_SERVICE_TABLE = 'tethys_datasets_spatialdatasetservice'
    WPS_TABLE = 'tethys_wps_webprocessingservice'

    # Use SQL literal to query legacy tables
    generic_statement = 'SELECT * FROM {0}'

    # For dataset services
    dataset_service_statement = generic_statement.format(DATASET_SERVICE_TABLE)
    try:
        results = query_to_dicts(dataset_service_statement)
        DatasetService = apps.get_model('tethys_services', 'DatasetService')

        # Copy contents of old table to new table
        for row in results:
            d = DatasetService(name=row['name'],
                               engine=row['engine'],
                               endpoint=row['endpoint'],
                               apikey=row['apikey'],
                               username=row['username'],
                               password=row['password'])
            d.save()

    except ProgrammingError:
        pass
    except InternalError:
        pass

    # For spatial dataset services
    spatial_dataset_service_statement = generic_statement.format(SPATIAL_DATASET_SERVICE_TABLE)
    try:
        results = query_to_dicts(spatial_dataset_service_statement)
        SpatialDatasetService = apps.get_model('tethys_services', 'SpatialDatasetService')

        # Copy contents of old table to new table
        for row in results:
            d = SpatialDatasetService(name=row['name'],
                                      engine=row['engine'],
                                      endpoint=row['endpoint'],
                                      apikey=row['apikey'],
                                      username=row['username'],
                                      password=row['password'])
            d.save()

    except ProgrammingError:
        pass
    except InternalError:
        pass

    # For web processing services
    web_processing_service_statement = generic_statement.format(WPS_TABLE)
    try:
        results = query_to_dicts(web_processing_service_statement)
        WebProcessingService = apps.get_model('tethys_services', 'WebProcessingService')

        # Copy contents of old table to new table
        for row in results:
            w = WebProcessingService(name=row['name'],
                                     endpoint=row['endpoint'],
                                     username=row['username'],
                                     password=row['password'])
            w.save()

    except ProgrammingError:
        pass
    except InternalError:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_services', '0004_webprocessingservice'),
    ]

    operations = [
        migrations.RunPython(migrate_to_services),
    ]