#!/bin/bash

echo "重新部署wechatrec容器到29212端口，修复所有问题..."
echo "停止和删除旧容器（如果存在）..."
docker stop wechatrec 2>/dev/null || true
docker rm wechatrec 2>/dev/null || true

# 获取主机IP地址
HOST_IP=$(ip route get 1 | awk '{print $7;exit}')
echo "主机IP: ${HOST_IP}"

# 确保目录存在
mkdir -p $(pwd)/data/html
mkdir -p $(pwd)/data/json
mkdir -p $(pwd)/data/logs

# 确保MongoDB可用
echo "检查MongoDB连接..."
mongosh --quiet --eval "db.serverStatus()" > /dev/null && echo "MongoDB已连接" || echo "警告：MongoDB未连接"

echo "启动容器 (将29212端口映射到容器的8000端口)..."
docker run -d \
  --name wechatrec \
  -p 29212:8000 \
  -v $(pwd)/data/html:/artlist/html \
  -v $(pwd)/data/json:/artlist/json \
  -v $(pwd)/data/logs:/artlist/logs \
  -e MONGO_URI=mongodb://${HOST_IP}:27017/ \
  -e MONGO_DB=wechat_articles \
  leileigwl/wechatrec:1.0.5

if [ $? -eq 0 ]; then
    echo "容器成功启动。访问API: http://${HOST_IP}:29212"
    echo "也可以尝试访问: http://localhost:29212"
    echo "容器日志:"
    docker logs wechatrec
    
    # 测试API可访问性
    echo ""
    echo "测试API可访问性..."
    sleep 2
    curl -s -I http://localhost:29212 || echo "无法访问API"
    
    echo ""
    echo "等待更多日志..."
    sleep 3
    docker logs wechatrec
else
    echo "启动容器失败。"
fi 