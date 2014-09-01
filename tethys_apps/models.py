from django.db import models
from tethys_apps.harvesters.app_harvester import SingletonAppHarvester

# Perform App Harvesting
harvester = SingletonAppHarvester()
harvester.harvest_apps()
