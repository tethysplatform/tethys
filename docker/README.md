# Docker Support Files

This project houses the docker file and scripts needed to make usable docker image.

### Environment

| Argument              | Description                 |Phase| Default                 |
|-----------------------|-----------------------------|-----|-------------------------|
|ALLOWED_HOSTS          | Django Setting              |Run  |['127.0.0.1', 'localhost']|
|BASH_PROFILE           | Where to create aliases     |Run  |.bashrc                  |
|CONDA_HOME             | Path to Conda Home Dir      |Build|${TETHYS_HOME}/miniconda”|
|CONDA_ENV_NAME         | Name of Conda environ       |Build|tethys                   |
|MINICONDA_URL          | URL of conda install script |Build|“https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh”|
|PYTHON_VERSION         | Version of Python to use    |Build|2                        |
|TETHYS_HOME            | Path to Tethys Home Dir     |Build|/usr/lib/tethys          |
|TETHYS_PORT            | Port for external web access|Run  |80                       |
|TETHYS_DB_USERNAME     | Postgres connection username|Run  |tethys_default           |
|TETHYS_DB_PASSWORD     | Postgres connection password|Run  |pass                     |
|TETHYS_DB_HOST         | Postgres connection address |Run  |172.17.0.1               |
|TETHYS_DB_PORT         | Postgres connection Port    |Run  |5432                     |
|TETHYS_SUPER_USER      | Default superuser username  |Run  |""                       |
|TETHYS_SUPER_USER_EMAIL| Default superuser email     |Run  |“”                       |
|TETHYS_SUPER_USER_PASS | Default superuser password  |Run  |""                       |
|UWSGI_PROCESSES        | Number of uwsgi processes   |Run  |10                       |
|CLIENT_MAX_BODY_SIZE   | Maximum size of file uploads|Run  |75M                      |

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
