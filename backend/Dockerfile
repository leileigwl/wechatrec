FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ .

# 创建目录
RUN mkdir -p /app/logs

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV ES_HOST=elasticsearch
ENV ES_PORT=9200
ENV ES_ARTICLES_INDEX=wechat_articles
ENV ES_LOGS_INDEX=wechat_logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "fastapiServer:app", "--host", "0.0.0.0", "--port", "8000"] 