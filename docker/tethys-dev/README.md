# Build

Build from Tethys source code:

```bash
cd docker/tethys-dev
docker build -t tethysplatform/tethys-dev -f ./Dockerfile ../../
```

Build with specific Python version:

```bash
cd docker/tethys-dev
docker build --build-arg="PYTHON_VERSION=3.11" -t tethysplatform/tethys-dev -f ./Dockerfile ../../
```

# Docker Compose

Copy the `docker-compose.yml` file to the location where you will store your app code.

## Start

```bash
docker compose up
```

# Start in Background w/ Logs

```bash
docker compose up -d && docker compose logs -f tethys
```

## Start with your UID/GID (unix only)

```bash
UID_GID="$(id -u):$(id -g)" docker compose up -d && docker compose logs -f tethys
```

## Attach

```bash
docker compose exec tethys /bin/bash
```

## Stop

```bash
docker compose stop
```

## Stop and Remove Containers

```bash
docker compose down
```