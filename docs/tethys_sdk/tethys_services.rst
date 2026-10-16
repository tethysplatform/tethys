.. _tethys_services_api:

********************
Tethys Services APIs
********************

**Last Updated:** August 2026

Tethys Services consists of several APIs that can be used to work with external data and processing services. Use the Persistent Store Services APIs to connect to SQL databases. Use the Dataset Services to consume file dataset services like CKAN or HydroShare. The Spatial Dataset Services can be used to connect to map servers like GeoServer and the Web Processing Services can be used to consume processing services such as those hosted by 52 North installations. Use the Secure Map Services to securely consume map services that require an API key or an OAuth2 access token.

.. toctree::
  :maxdepth: 1

  tethys_services/persistent_store
  tethys_services/spatial_persistent_store
  tethys_services/dataset_services
  tethys_services/spatial_dataset_services
  tethys_services/secure_map_services
  tethys_services/web_processing_services