# Build

```bash
cd docker/app-dev-environment
docker build -t tethysplatform/tethys-dev -f ./Dockerfile ../../
```

# Docker Compose

Copy the `docker-compose.yml` file to the location where you will store your app code.

## Start

```bash
docker compose up -d && docker compose logs -f tethys
```

## Start with Logs

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