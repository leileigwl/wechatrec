# WeChat Article Downloader

一个用于下载和存储微信公众号文章的工具。

## 功能

- 通过API接收微信公众号文章列表
- 下载文章HTML内容和图片
- 保存到MongoDB数据库
- 支持Docker部署

## 部署说明

### 使用Docker Compose部署

1. 克隆项目
2. 进入项目目录
3. 运行以下命令启动服务

```bash
docker-compose up -d
```

这将启动两个容器:
- `wechat-article-downloader` - FastAPI应用
- `mongodb` - MongoDB数据库

### API接口

- `POST /artlist/` - 接收文章列表数据
- `GET /articles/` - 从MongoDB获取文章列表
- `GET /logs/` - 查看日志
- `GET /logfiles/` - 查看日志文件列表

### 数据发送格式示例

```json
{
    "key": "AEqoeyurxc.98AEWQUcxi",
    "data": [
        {
            "url": "http://mp.weixin.qq.com/s?__biz=MjM5MjAxNDM4MA==&mid=2666944639&idx=1&sn=9bdb8ac2ce9491281cb9106f1c54c672&chksm=bc3b16cbb6c0603ab26e81546c029a064c4eac0f17828a9e605b134c9541912deb6f1dd58787&scene=0&xtrack=1#rd",
            "title": "鸿蒙电脑，正式发布！",
            "digest": "",
            "pub_time": "1747645079",
            "cover": "https://mmbiz.qpic.cn/sz_mmbiz_jpg/xrFYciaHL08CoLHibVQkZOfo86mfz6ymSaJLxGG5E5XrP0EnniakichhfDBpkKW6F6q3JJ99FdSlExiapmlBgTATpibg/640?wxtype=jpeg&wxfrom=0",
            "bizname": "人民日报",
            "biz": "MjM5MjAxNDM4MA=="
        }
    ],
    "stamp": 1747645309,
    "datatype": "article"
}
```

## 文件结构

- `fastapiServer.py` - FastAPI服务器
- `WxartDownloader.py` - 文章下载器
- `mongo_utils.py` - MongoDB工具函数
- `Dockerfile` - Docker配置
- `docker-compose.yml` - Docker Compose配置
- `requirements.txt` - Python依赖 