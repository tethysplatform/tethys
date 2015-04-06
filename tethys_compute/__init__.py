import os

default_app_config = 'tethys_compute.apps.TethysComputeConfig'

TETHYSCLUSTER_CFG_DIR = os.path.join(os.path.expanduser('~'), '.tethyscluster')
print TETHYSCLUSTER_CFG_DIR
TETHYSCLUSTER_CFG_FILE = os.path.join(TETHYSCLUSTER_CFG_DIR, 'config')
TETHYSCLUSTER_TETHYS_CFG_FILE = os.path.join(TETHYSCLUSTER_CFG_DIR, 'tethys_config')

TETHYSCLUSTER_CFG_TEMPLATE = """[global]
DEFAULT_TEMPLATE=default_cluster
INCLUDE=~/.tethyscluster/tethys_config

[aws info]
AWS_ACCESS_KEY_ID=%(aws_access_key_id)s
AWS_SECRET_ACCESS_KEY=%(aws_secret_access_key)s
AWS_USER_ID=%(aws_user_id)s

[key %(key_name)s]
KEY_LOCATION=%(key_location)s

[cluster default_cluster]
KEYNAME = %(key_name)s
CLUSTER_SIZE = 1
CLUSTER_SHELL = bash
NODE_IMAGE_ID = ami-3393a45a
NODE_INSTANCE_TYPE = t2.micro
PLUGINS = condor

[plugin condor]
SETUP_CLASS = tethyscluster.plugins.condor.CondorPlugin
"""

if not os.path.isdir(TETHYSCLUSTER_CFG_DIR):
    os.mkdir(TETHYSCLUSTER_CFG_DIR)
if not os.path.isfile(TETHYSCLUSTER_TETHYS_CFG_FILE):
    with open(TETHYSCLUSTER_TETHYS_CFG_FILE, 'w') as config_file:
        pass
if not os.path.isfile(TETHYSCLUSTER_CFG_FILE):
    with open(TETHYSCLUSTER_CFG_FILE, 'w') as config_file:
        pass
