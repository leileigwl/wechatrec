#!/bin/bash

# MongoDB连接信息 - 修改为您的MongoDB地址
MONGO_IP="localhost"
MONGO_PORT="27017"
MONGO_DB="wechat_articles"

# 确保数据目录存在
mkdir -p data/html data/json data/logs

# 启动容器 - 使用host网络模式简化网络配置
docker run -d \
  --name wechat-downloader \
  --network host \
  -v $(pwd)/data/html:/artlist/html \
  -v $(pwd)/data/json:/artlist/json \
  -v $(pwd)/data/logs:/artlist/logs \
  -e MONGO_URI=mongodb://${MONGO_IP}:${MONGO_PORT}/ \
  -e MONGO_DB=${MONGO_DB} \
  wechat-article-downloader

echo "容器已启动，API地址: http://localhost:29212" 