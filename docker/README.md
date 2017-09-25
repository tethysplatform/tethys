# Tethys Core Docker

This project houses the docker file and scripts needed to make the tethyscore 
docker.

### Building the Docker
To build the docker use the following commands in the terminal after
pulling the latest source code:

1. Make sure that there isn't already a docker container or docker
images with the desired name
```
> docker rm tethyscore
> docker rmi tethyscore
```

2. Build a new docker with the desired name and tag
```
> docker build -t tethyscore:latest
```
You can also use build arguments in this to change certain features
that you may find useful, such as the branch, and the configuration

Use the following syntax with arguments listed in the table

```
> docker build [--build-arg ARG=VAL] -t tethyscore:latest
```

| Argument                 | Description               | Default                |
|--------------------------|---------------------------|------------------------|
|TETHYSBUILD_BRANCH        | Tethys branch to be used  | release                |
|TETHYSBUILD_PY_VERSION    | Version of python         | 2                      |
|TETHYSBUILD_TETHYS_HOME   | Path to Tethys home dir   | /usr/lib/tethys        |
|TETHYSBUILD_CONDA_HOME    | Path to Conda home dir    | /usr/lib/tethys/conda/ |
|TETHYSBUILD_CONDA_ENV_NAME| Tethys environment name   | tethys                 |

### Running the docker
To run the docker you can use the following flags

use the following flag with the arguments listed in the table. (NOTE:
args in the build arg table can be used here as well)

```
-e TETHYSBUILD_CONDA_ENV='tethys'
```

| Argument                 | Description                | Default       |
|--------------------------|----------------------------|---------------|
|TETHYSBUILD_ALLOWED_HOST  | Django Allowed Hosts       | 127.0.0.1     |
|TETHYSBUILD_DB_USERNAME   | Database Username          | tethys_default|
|TETHYSBUILD_DB_PASSWORD   | Password for Database      | pass          |
|TETHYSBUILD_DB_HOST       | IPAddress for Database host| 127.0.0.1     |
|TETHYSBUILD_DB_PORT       | Port on Database host      | 5432          |
|TETHYSBUILD_SUPERUSER     | Tethys Superuser           | tethys_super  |
|TETHYSBUILD_SUPERUSER_PASS| Tethys Superuser Password  | admin         |

Example of Command:
```
> docker run -p 127.0.0.1:8000:8000 --name tethyscore \
    -e TETHYSBUILD_CONDA_ENV='tethys' -e TETHYSBUILD_CONFIG='develop' \
    -e TETHYSBUILD_DB_USERNAME='tethys_super' -e TETHYSBUILD_DB_PASSWORD='3x@m9139@$$' \
    -e TETHYSBUILD_DB_PORT='5432' TETHYSBUILD_SUPERUSER='admin' \
    -e TETHYSBUILD_SUPERUSER_PASS='admin' tethyscore
```
