#!/bin/bash

# Status variables
DJANGO_STATUS="not checked"
PYTHON_STATUS="not checked"
EXIT_CODE=0

# Verify Django version in conda matches DJANGO_VERSION build arg
if [ -n "$DJANGO_VERSION" ]; then
    INSTALLED_DJANGO=$(micromamba run -n "$CONDA_ENV_NAME" python -c 'import django; print(django.get_version())')
    DJANGO_VERSION_CLEAN=$(echo "$DJANGO_VERSION" | sed 's/\.[*]$//')
    if ! echo "$INSTALLED_DJANGO" | grep -q "^$DJANGO_VERSION_CLEAN"; then
        DJANGO_STATUS="ERROR: Installed Django version $INSTALLED_DJANGO does not match DJANGO_VERSION build arg $DJANGO_VERSION"
        EXIT_CODE=1
    else
        DJANGO_STATUS="Verified: Installed Django version $INSTALLED_DJANGO matches DJANGO_VERSION build arg $DJANGO_VERSION"
    fi
else
    DJANGO_STATUS="SKIPPED: DJANGO_VERSION build arg not set"
fi

# Verify Python version in conda matches PYTHON_VERSION build arg
if [ -n "$PYTHON_VERSION" ]; then
    INSTALLED_PYTHON=$(micromamba run -n "$CONDA_ENV_NAME" python -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')
    PYTHON_VERSION_CLEAN=$(echo "$PYTHON_VERSION" | sed 's/\.[*]$//')
    if ! echo "$INSTALLED_PYTHON" | grep -q "^$PYTHON_VERSION_CLEAN"; then
        PYTHON_STATUS="ERROR: Installed Python version $INSTALLED_PYTHON does not match PYTHON_VERSION build arg $PYTHON_VERSION"
        EXIT_CODE=1
    else
        PYTHON_STATUS="Verified: Installed Python version $INSTALLED_PYTHON matches PYTHON_VERSION build arg $PYTHON_VERSION"
    fi
else
    PYTHON_STATUS="SKIPPED: PYTHON_VERSION build arg not set"
fi

echo "$PYTHON_STATUS"
echo "$DJANGO_STATUS"

exit $EXIT_CODE
