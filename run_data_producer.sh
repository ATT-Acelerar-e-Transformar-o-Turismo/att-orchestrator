#!/bin/bash

# Script to copy data producer to indicator-service container and run it

echo "Starting data producer setup..."

# Check if indicator-service container is running
if ! docker ps | grep -q indicator-service; then
    echo "Error: indicator-service container is not running"
    exit 1
fi

echo "Copying data_producer.py to indicator-service container..."
docker cp indicator-service/data-producer-example/data_producer/data_producer.py indicator-service:/app/data_producer.py

if [ $? -ne 0 ]; then
    echo "Error: Failed to copy data_producer.py to container"
    exit 1
fi

echo "Installing required dependencies..."
docker exec indicator-service pip install aiohttp aio-pika

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "Starting data producer in background..."
docker exec indicator-service python /app/data_producer.py

