# WeChat Article Search Backend

这是微信文章搜索系统的后端部分，使用FastAPI和Elasticsearch实现。

## 功能特点

- 使用Elasticsearch存储和检索微信公众号文章
- 提供RESTful API接口
- 支持全文搜索，包括中文分词
- 日志记录和查询功能
- 支持Docker部署

## 文件结构

```
backend/
├── app/
│   ├── fastapiServer.py      # FastAPI应用主文件
│   └── elasticsearch_utils.py # Elasticsearch工具函数
├── Dockerfile                # Docker配置文件
└── requirements.txt          # Python依赖
```

## API接口

### 保存文章

```
POST /artlist/
```

保存微信文章到Elasticsearch。

请求体示例：

```json
{
  "data": {
    "key": "AEqoeyurxc.98AEWQUcxi",
    "data": [
      {
        "url": "http://mp.weixin.qq.com/s?__biz=MzI2Mjg2ODk4OA==&mid=2247515798&idx=1&sn=e37408dfc4e7945808a8d87a04caa722",
        "title": "构网型技术/虚拟电厂等七个方向，国家能源局开展新型电力系统建设第一批试点工作",
        "digest": "",
        "pub_time": "1749030723",
        "cover": "https://mmbiz.qpic.cn/mmbiz_jpg/VjeqDTAdu7oiaWPM5LzAxRn3NmnWFzR3L3Mic3DSxe1G78IVBtHDAF0Ck8azLt6QDtcQGRSfk5gxr9TcibR7ZWaWQ/640?wxtype=jpeg&wxfrom=0",
        "bizname": "储能之音",
        "biz": "MzI2Mjg2ODk4OA=="
      }
    ],
    "stamp": 1749030921,
    "datatype": "article"
  }
}
```

### 搜索文章

```
GET /search/?q={query}&page={page}&size={size}
```

参数：
- `q`: 搜索关键词
- `page`: 页码（默认1）
- `size`: 每页结果数（默认10，最大50）

### 获取日志

```
GET /logs/?start={start_time}&end={end_time}&page={page}&size={size}
```

参数：
- `start`: 开始时间（ISO格式，可选）
- `end`: 结束时间（ISO格式，可选）
- `page`: 页码（默认1）
- `size`: 每页结果数（默认50，最大100）

## Elasticsearch索引

### wechat_articles

存储微信文章的索引，包含以下字段：

- `url`: 文章链接
- `title`: 文章标题
- `digest`: 文章摘要
- `pub_time`: 发布时间戳
- `pub_time_iso`: 发布时间（ISO格式）
- `cover`: 封面图片链接
- `bizname`: 公众号名称
- `biz`: 公众号biz参数
- `unique_id`: 文章唯一标识
- `created_at`: 记录创建时间

### wechat_logs

存储请求日志的索引，包含以下字段：

- `timestamp`: 请求时间
- `method`: 请求方法
- `path`: 请求路径
- `client`: 客户端IP
- `data`: 请求数据
- `created_at`: 记录创建时间

## 部署说明

### 使用Docker Compose

在项目根目录运行：

```bash
docker-compose up -d
```

### 单独运行

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 设置环境变量：

```bash
export ES_HOST=localhost
export ES_PORT=9200
export ES_ARTICLES_INDEX=wechat_articles
export ES_LOGS_INDEX=wechat_logs
```

3. 运行应用：

```bash
cd app
uvicorn fastapiServer:app --host 0.0.0.0 --port 8000
```

## 中文分词

本系统使用Elasticsearch的IK分词器进行中文分词，支持两种模式：

- `ik_max_word`: 最细粒度分词，适合索引
- `ik_smart`: 智能分词，适合搜索 