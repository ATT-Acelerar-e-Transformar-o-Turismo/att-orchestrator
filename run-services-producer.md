# Services MQ Producer

This document describes how to run a data producer that sends messages to the `services-mq` RabbitMQ instance instead of `data-mq`.

## Docker Run Command

```bash
docker run -d \
  --name att-services-producer \
  --network att-orchestrator_att-network \
  -e RABBITMQ_URL="amqp://user:password@services-mq:5672/" \
  -e API_URL="http://resource-service:8080/resources/" \
  -e QUEUE_NAME="resource_data" \
  --restart unless-stopped \
  att-services-producer:latest
```

## Build Command

First, build the image from the resource-service data-producer directory:

```bash
cd resource-service/data-producer
docker build -t att-services-producer .
```

## Environment Variables

- `RABBITMQ_URL`: Connection string to services-mq (default: `amqp://user:password@services-mq:5672/`)
- `API_URL`: Resource service endpoint (default: `http://resource-service:8080/resources/`)
- `QUEUE_NAME`: Queue name for messages (default: `resource_data`)

## Network Configuration

The container runs on the `att-orchestrator_att-network` network to communicate with:
- `services-mq`: RabbitMQ message broker (port 5672)
- `resource-service`: REST API for resources (port 8080)

## Message Flow

1. Producer fetches resources from resource-service API
2. Generates sample data for each resource's wrapper_id
3. Sends messages to services-mq `resource_data` queue
4. Messages are consumed by the indicator-service

## Prerequisites

Ensure the following services are running:
- `services-mq` (RabbitMQ)
- `resource-service` (API endpoint)
- `att-network` (Docker network)

## Stopping the Producer

```bash
docker stop att-services-producer
docker rm att-services-producer
```