#!/bin/bash

echo "Building new Docker image..."
docker build -t leileigwl/wechatrec:1.0.3 .

if [ $? -eq 0 ]; then
    echo "Build successful. Stopping and removing old container..."
    docker stop wechatrec
    docker rm wechatrec
    
    echo "Starting new container with the updated image..."
    docker run -d \
      --name wechatrec \
      --network wechat-network \
      -p 29212:8000 \
      -v $(pwd)/data/html:/artlist/html \
      -v $(pwd)/data/json:/artlist/json \
      -v $(pwd)/data/logs:/artlist/logs \
      -e MONGO_URI=mongodb://mongodb:27017/ \
      -e MONGO_DB=wechat_articles \
      leileigwl/wechatrec:1.0.3
    
    if [ $? -eq 0 ]; then
        echo "Container successfully started. Access the API at http://localhost:29212"
    else
        echo "Failed to start new container."
    fi
else
    echo "Build failed. No changes were made to running container."
fi 