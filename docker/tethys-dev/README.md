# Example workflow

1. Copy one of the docker-compose files to the directory where you want to store your Tethys app code.

2. Start containers using `docker compose` (start in the background and follow the logs):

```bash
docker compose up -d && docker compose logs -f tethys
```

3. In a separate terminal, exec in to run Tethys commands, like scaffolding and installing an app:

```bash
docker compose exec tethys /bin/bash
tethys scaffold my_first_app
cd tethysapp-my_first_app
tethys install -d
```

4. Back in the first terminal, `CTRL-C`` to stop following the logs, then restart the tethys container to load the new app (and follow logs):

```bash
docker compose restart tethys && docker compose logs -f tethys
```

5. You should see the app source code in your working directory. You can now edit the code in your favorite IDE. The container is running the dev server, so it should restart automatically.

6. If you need to run Tethys commands, exec in to the container again.

7. The portal_config.yml is also added to your working directory. You can edit this file to change the portal settings, and then restart the Tethys container to load the new settings (see step 4).

8. When you are done, stop the containers:

```bash
docker compose stop
```

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
docker compose up -d && docker compose logs -f tethys
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


