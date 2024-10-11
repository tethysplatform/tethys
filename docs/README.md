# Documentation for Tethys Platform

This directory contains the Sphinx documentation project for Tethys Platform. Use these instructions to create a Conda environment and build the documentation.

## Create Conda Environment

Create a conda environment with the dependencies installed using the `docs_environment.yml`:

```
cd docs
conda env create -f docs_environment.yml
```

## Initialize git lfs

Use Git LFS to download the images:

```
# Install git-lfs (see: https://git-lfs.com/)
apt install git-lfs

# In the Tethys repository
git lfs install
git lfs pull
```

## Build Docs

Activate the conda environment and build the documentation using these commands:

```
conda activate tethys-docs
make html
```

## Autobuild

Alternatively, use autobuild to build the docs, host them with a dev server, and automatically rebuild when changes are made:

```
cd docs
sphinx-autobuild --host 127.0.0.1 --port 8001 . ./_build/html
```