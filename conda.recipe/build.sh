#!/usr/bin/env bash

python setup.py install --single-version-externally-managed --record=record.txt

# Copy non-.py files

# tethys_apps
cp -r $SRC_DIR/tethys_apps/static $SP_DIR/tethys_apps/
cp -r $SRC_DIR/tethys_apps/templates $SP_DIR/tethys_apps/

# tethys_cli
cp -r $SRC_DIR/tethys_cli/gen_templates $SP_DIR/tethys_cli/
cp -r $SRC_DIR/tethys_cli/scaffold_templates $SP_DIR/tethys_cli/

# tethys_compute
cp -r $SRC_DIR/tethys_compute/static $SP_DIR/tethys_compute/
cp -r $SRC_DIR/tethys_compute/templates $SP_DIR/tethys_compute/

# tethys_gizmos
cp -r $SRC_DIR/tethys_gizmos/static $SP_DIR/tethys_gizmos/
cp -r $SRC_DIR/tethys_gizmos/templates $SP_DIR/tethys_gizmos/

# tethys_portal
cp -r $SRC_DIR/tethys_portal/static $SP_DIR/tethys_portal/
cp -r $SRC_DIR/tethys_portal/templates $SP_DIR/tethys_portal/

# tethys_quotas
cp -r $SRC_DIR/tethys_quotas/templates $SP_DIR/tethys_quotas/

# tethys_services
cp -r $SRC_DIR/tethys_services/static $SP_DIR/tethys_services/
cp -r $SRC_DIR/tethys_services/templates $SP_DIR/tethys_services/


rm -rf $SP_DIR/tethys_tests/
rm $SP_DIR/tethys_portal/settings.py*