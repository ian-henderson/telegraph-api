echo "Running prod environment"

sudo docker compose --file docker/docker_compose.yaml \
                    --file docker/docker_compose.prod.yaml \
                 up --build
