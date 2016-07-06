"""
********************************************************************************
* Name: tethys_compute/__init__.py
* Author: Scott Christensen
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
import os

default_app_config = 'tethys_compute.apps.TethysComputeConfig'

TETHYSCLUSTER_CFG_DIR = os.path.join(os.path.expanduser('~'), '.tethyscluster')
TETHYSCLUSTER_CFG_FILE = os.path.join(TETHYSCLUSTER_CFG_DIR, 'config')
TETHYSCLUSTER_TETHYS_CFG_FILE = os.path.join(TETHYSCLUSTER_CFG_DIR, 'tethys_config')
TETHYSCLUSTER_AWS_CFG_FILE = os.path.join(TETHYSCLUSTER_CFG_DIR, 'aws_config')
TETHYSCLUSTER_AZURE_CFG_FILE = os.path.join(TETHYSCLUSTER_CFG_DIR, 'azure_config')

TETHYSCLUSTER_CFG_TEMPLATE = """#Global settings for TethysCluster
[global]
DEFAULT_TEMPLATE=%(default_cluster)s
INCLUDE=~/.tethyscluster/tethys_config, ~/.tethyscluster/aws_config, ~/.tethyscluster/azure_config

[plugin condor]
SETUP_CLASS = tethyscluster.plugins.condor.CondorPlugin
"""

TETHYSCLUSTER_AWS_CFG_TEMPLATE = """#AWS settings for TethysCluster
[aws info]
AWS_ACCESS_KEY_ID=%(aws_access_key_id)s
AWS_SECRET_ACCESS_KEY=%(aws_secret_access_key)s
AWS_USER_ID=%(aws_user_id)s

[key %(key_name)s]
KEY_LOCATION=%(key_location)s

[cluster aws_default_cluster]
CLOUD_PROVIDER = AWS
KEYNAME = %(key_name)s
CLUSTER_SIZE = 1
CLUSTER_SHELL = bash
NODE_IMAGE_ID = ami-3393a45a
NODE_INSTANCE_TYPE = m3.medium
PLUGINS = condor
"""

TETHYSCLUSTER_AZURE_CFG_TEMPLATE = """#Azure settings for TethysCluster
[azure info]
SUBSCRIPTION_ID = %(subscription_id)s
CERTIFICATE_PATH = %(certificate_path)s

[key %(certificate_fingerprint)s]
KEY_LOCATION=%(certificate_path)s

[cluster azure_default_cluster]
CLOUD_PROVIDER = Azure
KEYNAME = %(certificate_fingerprint)s
CLUSTER_SIZE = 1
CLUSTER_SHELL = bash
NODE_IMAGE_ID = tc-linux12-2
NODE_INSTANCE_TYPE = Small
PLUGINS = condor
"""

if not os.path.isdir(TETHYSCLUSTER_CFG_DIR):
    os.mkdir(TETHYSCLUSTER_CFG_DIR)
for config_file in [TETHYSCLUSTER_CFG_FILE,
                    TETHYSCLUSTER_TETHYS_CFG_FILE,
                    TETHYSCLUSTER_AWS_CFG_FILE,
                    TETHYSCLUSTER_AZURE_CFG_FILE]:
    if not os.path.isfile(config_file):
        with open(config_file, 'w') as config_file:
            pass
