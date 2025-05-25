#!/bin/bash

# 设置MongoDB连接信息
# 如果MongoDB在同一台主机上，请使用相应的IP地址
MONGO_IP="172.17.0.1"  # Docker默认网桥的主机IP，适用于大多数Linux环境
# MONGO_IP="host.docker.internal"  # macOS/Windows Docker Desktop
MONGO_PORT="27017"
MONGO_DB="wechat_articles"

# 创建数据目录
mkdir -p data/html data/json data/logs

# 启动容器
docker run -d \
  --name wechat-downloader \
  -p 29212:8000 \
  -v $(pwd)/data/html:/artlist/html \
  -v $(pwd)/data/json:/artlist/json \
  -v $(pwd)/data/logs:/artlist/logs \
  -e MONGO_URI=mongodb://${MONGO_IP}:${MONGO_PORT}/ \
  -e MONGO_DB=${MONGO_DB} \
  wechat-article-downloader

echo "容器已启动，API地址: http://localhost:29212" 