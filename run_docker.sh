#!/bin/bash

# 构建Docker镜像（如果需要）
# docker build -t wechat-article-downloader .

# 确保数据目录存在
mkdir -p data/html data/json data/logs

# 获取主机IP地址，这在Linux上通常更可靠
HOST_IP=$(ip route get 1 | awk '{print $7;exit}')

# 启动容器
docker run -d \
  --name wechatrec \
  --network host \
  -p 29212:8000 \
  -v $(pwd)/data/html:/artlist/html \
  -v $(pwd)/data/json:/artlist/json \
  -v $(pwd)/data/logs:/artlist/logs \
  -e MONGO_URI=mongodb://${HOST_IP}:27017/ \
  -e MONGO_DB=wechat_articles \
  leileigwl/wechatrec:1.0.1

echo "Container started. Access the API at http://localhost:29212" 