DOCKER_VERSION=$1
TEST_SCRIPT=$2

echo "Running with docker compose ${DOCKER_VERSION}"

if [ $DOCKER_VERSION == "v2" ]; then
    docker compose up -d grafana influxdb
    docker compose run k6 run /scripts/${TEST_SCRIPT}
fi

if [ $DOCKER_VERSION == "v1" ]; then
    docker-compose up -d grafana influxdb
    docker-compose run k6 run /scripts/${TEST_SCRIPT}
fi
