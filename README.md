# telegraph-api

## Run locally

### Requirements

- docker, docker compose

### Env var file

The .env file should be located in the root/top directory of the project:

```bash
telegraph-api
├── app
├── docker-compose.dev.yaml
├── docker-compose.prod.yaml
├── docker-compose.yaml
├── Dockerfile
├── entrypoint.sh
├── README.md
├── run-docker-compose.dev.sh
├── run-docker-compose.prod.sh
└── .env
```

The DB env variables are determined by the docker-compose set up.

.env:

```bash
DB_HOST="postgres"
DB_NAME="telegraph"
DB_PASSWORD="password"
DB_PORT="5432"
DB_USER="admin"
```

## Docker Containers

- [redis](https://hub.docker.com/_/redis)

### Dev Environment

- [mailhog](https://hub.docker.com/r/mailhog/mailhog)
- [postres](https://hub.docker.com/_/postgres)

### Prod Environment
