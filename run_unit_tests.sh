echo "Running unit tests"

sudo docker compose --file docker/docker_compose.unit_tests.yaml \
                 up --build
