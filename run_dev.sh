echo "Running dev environment"

sudo docker compose --file docker/docker_compose.yaml \
                    --file docker/docker_compose.dev.yaml \
                 up --build \
                    --watch
