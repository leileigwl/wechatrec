# WechatRec - 微信公众号文章下载工具

一个用于下载、存储和管理微信公众号文章的API服务。

## 功能特点

- 接收并存储微信公众号文章数据
- 自动下载文章内容
- MongoDB数据持久化
- 完整的日志记录和查询功能
- RESTful API接口

## 部署方式

### Docker部署(推荐)

使用提供的Docker脚本一键部署:

```bash
bash run_docker.sh
```

服务将在 http://localhost:29212 上运行。

### 环境变量

- `MONGO_URI`: MongoDB连接URI (默认: mongodb://host.docker.internal:27017/)
- `MONGO_DB`: MongoDB数据库名称 (默认: wechat_articles)

## API接口

### 保存文章列表

- **URL**: `/artlist/`
- **方法**: `POST`
- **功能**: 接收文章数据，保存到MongoDB和文件系统，并下载文章内容
- **请求体**: JSON格式的文章数据

### 查看日志

- **URL**: `/logs/`
- **方法**: `GET`
- **参数**:
  - `date`: 可选，指定日期（格式：YYYY-MM-DD）
  - `limit`: 可选，返回的最大日志条数（默认：100）
- **功能**: 查看系统日志记录

### 获取文章列表

- **URL**: `/articles/`
- **方法**: `GET`
- **参数**:
  - `limit`: 可选，返回的最大文章数（默认：100）
  - `skip`: 可选，跳过的文章数，用于分页（默认：0）
  - `biz`: 可选，公众号biz参数，用于筛选特定公众号的文章
- **功能**: 从MongoDB获取文章列表

### 查看日志文件列表

- **URL**: `/logfiles/`
- **方法**: `GET`
- **功能**: 查看所有日志文件信息，包括文件名、大小和最后修改时间

## 数据存储

- 文章JSON数据: `/artlist/json`
- 日志文件: `/artlist/logs`
- MongoDB数据库: 文章和日志数据

## 故障排除

### MongoDB连接问题

如果遇到以下错误：
```
Error retrieving logs from MongoDB: [Errno 111] Connection refused
```

请检查：
1. 确保MongoDB服务已启动并运行在27017端口
2. 修改`run_docker.sh`中的`MONGO_URI`环境变量:
   - Windows/Mac: 使用`mongodb://host.docker.internal:27017/`
   - Linux: 使用`mongodb://172.17.0.1:27017/`或特定的主机IP

## 开发说明

本项目使用FastAPI框架构建，主要依赖包括:

- FastAPI: Web框架
- BeautifulSoup: HTML解析
- MongoDB: 数据存储

## 文件结构

- `fastapiServer.py`: 主服务器文件
- `WxartDownloader.py`: 文章下载工具
- `mongo_utils.py`: MongoDB工具函数
- `run_docker.sh`: Docker部署脚本 