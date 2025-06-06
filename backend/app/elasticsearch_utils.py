"""
Elasticsearch utilities for WeChat article search system.
"""
import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import NotFoundError, ConnectionError

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 从环境变量获取Elasticsearch配置
ES_HOST = os.environ.get("ES_HOST", "localhost")
ES_PORT = os.environ.get("ES_PORT", "9200")
ES_ARTICLES_INDEX = os.environ.get("ES_ARTICLES_INDEX", "wechat_articles")
ES_LOGS_INDEX = os.environ.get("ES_LOGS_INDEX", "wechat_logs")

# 创建Elasticsearch客户端
es_client = Elasticsearch(f"http://{ES_HOST}:{ES_PORT}")

# 文章索引映射
ARTICLES_MAPPING = {
    "mappings": {
        "properties": {
            "url": {"type": "keyword"},
            "title": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
            "digest": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
            "pub_time": {"type": "long"},
            "pub_time_iso": {"type": "date"},
            "cover": {"type": "keyword"},
            "bizname": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
            "biz": {"type": "keyword"},
            "unique_id": {"type": "keyword"},
            "created_at": {"type": "date"}
        }
    },
    "settings": {
        "analysis": {
            "analyzer": {
                "ik_max_word": {
                    "type": "custom",
                    "tokenizer": "ik_max_word",
                    "filter": ["lowercase"]
                },
                "ik_smart": {
                    "type": "custom",
                    "tokenizer": "ik_smart",
                    "filter": ["lowercase"]
                }
            }
        }
    }
}

# 日志索引映射
LOGS_MAPPING = {
    "mappings": {
        "properties": {
            "timestamp": {"type": "date"},
            "method": {"type": "keyword"},
            "path": {"type": "keyword"},
            "client": {"type": "keyword"},
            "data": {"type": "object", "enabled": False},
            "created_at": {"type": "date"}
        }
    }
}

def initialize_indices():
    """
    初始化Elasticsearch索引
    """
    try:
        # 检查Elasticsearch连接
        if not es_client.ping():
            logger.error("无法连接到Elasticsearch")
            return False
        
        # 创建文章索引（如果不存在）
        if not es_client.indices.exists(index=ES_ARTICLES_INDEX):
            es_client.indices.create(
                index=ES_ARTICLES_INDEX,
                body=ARTICLES_MAPPING
            )
            logger.info(f"创建索引: {ES_ARTICLES_INDEX}")
        
        # 创建日志索引（如果不存在）
        if not es_client.indices.exists(index=ES_LOGS_INDEX):
            es_client.indices.create(
                index=ES_LOGS_INDEX,
                body=LOGS_MAPPING
            )
            logger.info(f"创建索引: {ES_LOGS_INDEX}")
        
        return True
    except ConnectionError as e:
        logger.error(f"Elasticsearch连接错误: {e}")
        return False
    except Exception as e:
        logger.error(f"初始化索引时发生错误: {e}")
        return False

def save_log(log_data: Dict[str, Any]) -> bool:
    """
    保存请求日志到Elasticsearch
    
    Args:
        log_data: 包含timestamp, method, path, client, data的字典
    
    Returns:
        bool: 保存成功返回True，否则返回False
    """
    try:
        # 添加创建时间
        log_data["created_at"] = datetime.now().isoformat()
        
        # 保存到Elasticsearch
        es_client.index(
            index=ES_LOGS_INDEX,
            document=log_data
        )
        return True
    except Exception as e:
        logger.error(f"保存日志时发生错误: {e}")
        return False

def save_article_data(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    保存文章数据到Elasticsearch
    
    Args:
        request_data: 包含文章数据的请求
    
    Returns:
        Dict: 包含保存结果的字典
    """
    try:
        # 适应多种可能的数据结构
        # 检查是否有多层嵌套结构
        if isinstance(request_data, dict):
            # 情况1: 直接包含文章列表的数据结构 {"data": [...]}
            if "data" in request_data and isinstance(request_data["data"], list):
                articles = request_data["data"]
            # 情况2: test_data.py 中的嵌套数据结构
            elif "data" in request_data and isinstance(request_data["data"], dict):
                data = request_data["data"]
                if "data" in data and isinstance(data["data"], dict):
                    nested_data = data["data"]
                    if "data" in nested_data and isinstance(nested_data["data"], list):
                        articles = nested_data["data"]
                    else:
                        articles = []
                else:
                    articles = []
            else:
                articles = []
        else:
            return {"success": False, "message": "请求数据格式不正确", "saved": 0}
        
        if not articles:
            return {"success": False, "message": "没有找到文章数据", "saved": 0}
        
        # 准备批量操作
        bulk_data = []
        now = datetime.now().isoformat()
        
        for article in articles:
            # 生成唯一ID
            unique_id = f"{article.get('biz', '')}-{article.get('mid', '')}-{article.get('idx', '')}"
            if not unique_id or unique_id == "--":
                unique_id = str(uuid.uuid4())
            
            # 转换发布时间
            pub_time = article.get("pub_time", "")
            pub_time_iso = None
            if pub_time:
                try:
                    pub_time_iso = datetime.fromtimestamp(int(pub_time)).isoformat()
                except (ValueError, TypeError):
                    pub_time_iso = None
            
            # 准备文档
            doc = {
                "url": article.get("url", ""),
                "title": article.get("title", ""),
                "digest": article.get("digest", ""),
                "pub_time": pub_time,
                "pub_time_iso": pub_time_iso,
                "cover": article.get("cover", ""),
                "bizname": article.get("bizname", ""),
                "biz": article.get("biz", ""),
                "unique_id": unique_id,
                "created_at": now
            }
            
            # 添加到批量操作
            bulk_data.append({
                "_index": ES_ARTICLES_INDEX,
                "_id": unique_id,
                "_source": doc
            })
        
        # 执行批量操作
        if bulk_data:
            success, failed = helpers.bulk(
                es_client,
                bulk_data,
                stats_only=True
            )
            return {
                "success": True,
                "message": f"成功保存 {success} 篇文章，失败 {failed} 篇",
                "saved": success,
                "failed": failed
            }
        else:
            return {"success": False, "message": "没有有效的文章数据", "saved": 0}
    
    except Exception as e:
        logger.error(f"保存文章数据时发生错误: {e}")
        return {"success": False, "message": f"保存文章数据时发生错误: {str(e)}", "saved": 0}

def search_articles(query: str, page: int = 1, size: int = 10) -> Dict[str, Any]:
    """
    搜索文章
    
    Args:
        query: 搜索关键词
        page: 页码，从1开始
        size: 每页结果数
    
    Returns:
        Dict: 包含搜索结果的字典
    """
    try:
        # 计算偏移量
        from_val = (page - 1) * size
        
        # 构建查询
        search_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "digest^2", "bizname"],
                    "type": "best_fields",
                    "operator": "or",
                    "minimum_should_match": "70%"
                }
            },
            "highlight": {
                "fields": {
                    "title": {"number_of_fragments": 0},
                    "digest": {"number_of_fragments": 2, "fragment_size": 150}
                },
                "pre_tags": ["<em>"],
                "post_tags": ["</em>"],
                "encoder": "html"  # 确保HTML标签不被转义
            },
            "sort": [
                "_score",
                {"pub_time_iso": {"order": "desc"}}
            ],
            "from": from_val,
            "size": size
        }
        
        # 执行搜索
        start_time = datetime.now()
        response = es_client.search(
            index=ES_ARTICLES_INDEX,
            body=search_query
        )
        end_time = datetime.now()
        took_ms = (end_time - start_time).total_seconds() * 1000
        
        # 处理结果
        hits = response["hits"]["hits"]
        total = response["hits"]["total"]["value"]
        
        results = []
        for hit in hits:
            source = hit["_source"]
            highlight = hit.get("highlight", {})
            
            # 应用高亮
            if "title" in highlight:
                source["title"] = highlight["title"][0]
            if "digest" in highlight:
                source["digest"] = "...".join(highlight["digest"])
            
            results.append(source)
        
        return {
            "query": query,
            "page": page,
            "size": size,
            "total": total,
            "took": took_ms,
            "results": results
        }
    
    except Exception as e:
        logger.error(f"搜索文章时发生错误: {e}")
        return {
            "query": query,
            "page": page,
            "size": size,
            "total": 0,
            "took": 0,
            "results": [],
            "error": str(e)
        }

def get_logs(start_time: Optional[str] = None, end_time: Optional[str] = None, 
             page: int = 1, size: int = 50) -> Dict[str, Any]:
    """
    获取日志
    
    Args:
        start_time: 开始时间（ISO格式）
        end_time: 结束时间（ISO格式）
        page: 页码，从1开始
        size: 每页结果数
    
    Returns:
        Dict: 包含日志结果的字典
    """
    try:
        # 计算偏移量
        from_val = (page - 1) * size
        
        # 构建查询
        query_parts = []
        if start_time:
            query_parts.append({"range": {"timestamp": {"gte": start_time}}})
        if end_time:
            query_parts.append({"range": {"timestamp": {"lte": end_time}}})
        
        query = {"match_all": {}}
        if query_parts:
            query = {"bool": {"must": query_parts}}
        
        search_query = {
            "query": query,
            "sort": [{"timestamp": {"order": "desc"}}],
            "from": from_val,
            "size": size
        }
        
        # 执行搜索
        response = es_client.search(
            index=ES_LOGS_INDEX,
            body=search_query
        )
        
        # 处理结果
        hits = response["hits"]["hits"]
        total = response["hits"]["total"]["value"]
        
        logs = [hit["_source"] for hit in hits]
        
        return {
            "page": page,
            "size": size,
            "total": total,
            "logs": logs
        }
    
    except Exception as e:
        logger.error(f"获取日志时发生错误: {e}")
        return {
            "page": page,
            "size": size,
            "total": 0,
            "logs": [],
            "error": str(e)
        }

def delete_article(article_id: str) -> Dict[str, Any]:
    """
    删除指定ID的文章
    
    Args:
        article_id: 文章唯一ID
    
    Returns:
        Dict: 包含删除结果的字典
    """
    try:
        response = es_client.delete(
            index=ES_ARTICLES_INDEX,
            id=article_id,
            refresh=True
        )
        
        return {
            "success": True,
            "message": f"成功删除文章 ID: {article_id}",
            "deleted": True
        }
    except NotFoundError:
        return {
            "success": False,
            "message": f"未找到文章 ID: {article_id}",
            "deleted": False
        }
    except Exception as e:
        logger.error(f"删除文章时发生错误: {e}")
        return {
            "success": False,
            "message": f"删除文章时发生错误: {str(e)}",
            "deleted": False
        }

def clear_articles() -> Dict[str, Any]:
    """
    清空所有文章（删除并重建索引）
    
    Returns:
        Dict: 包含操作结果的字典
    """
    try:
        # 检查索引是否存在
        if es_client.indices.exists(index=ES_ARTICLES_INDEX):
            # 删除索引
            es_client.indices.delete(index=ES_ARTICLES_INDEX)
            logger.info(f"已删除索引: {ES_ARTICLES_INDEX}")
            
            # 重建索引
            es_client.indices.create(
                index=ES_ARTICLES_INDEX,
                body=ARTICLES_MAPPING
            )
            logger.info(f"已重建索引: {ES_ARTICLES_INDEX}")
            
            return {
                "success": True,
                "message": "所有文章已清空，索引已重建"
            }
        else:
            return {
                "success": False,
                "message": f"索引 {ES_ARTICLES_INDEX} 不存在"
            }
    except Exception as e:
        logger.error(f"清空文章时发生错误: {e}")
        return {
            "success": False,
            "message": f"清空文章时发生错误: {str(e)}"
        }

def add_single_article(article_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    添加单篇文章
    
    Args:
        article_data: 包含文章数据的字典
    
    Returns:
        Dict: 包含添加结果的字典
    """
    try:
        if not article_data:
            return {"success": False, "message": "文章数据为空", "saved": 0}
        
        # 生成唯一ID
        unique_id = f"{article_data.get('biz', '')}-{article_data.get('mid', '')}-{article_data.get('idx', '')}"
        if not unique_id or unique_id == "--":
            unique_id = str(uuid.uuid4())
        
        # 转换发布时间
        pub_time = article_data.get("pub_time", "")
        pub_time_iso = None
        if pub_time:
            try:
                pub_time_iso = datetime.fromtimestamp(int(pub_time)).isoformat()
            except (ValueError, TypeError):
                pub_time_iso = None
        
        # 准备文档
        doc = {
            "url": article_data.get("url", ""),
            "title": article_data.get("title", ""),
            "digest": article_data.get("digest", ""),
            "pub_time": pub_time,
            "pub_time_iso": pub_time_iso,
            "cover": article_data.get("cover", ""),
            "bizname": article_data.get("bizname", ""),
            "biz": article_data.get("biz", ""),
            "unique_id": unique_id,
            "created_at": datetime.now().isoformat()
        }
        
        # 保存到Elasticsearch
        response = es_client.index(
            index=ES_ARTICLES_INDEX,
            id=unique_id,
            document=doc,
            refresh=True
        )
        
        return {
            "success": True,
            "message": f"成功添加文章: {doc['title']}",
            "id": unique_id,
            "article": doc
        }
    
    except Exception as e:
        logger.error(f"添加文章时发生错误: {e}")
        return {"success": False, "message": f"添加文章时发生错误: {str(e)}", "saved": 0}

def get_all_articles(page: int = 1, size: int = 20, sort_by: str = "pub_time_iso", sort_order: str = "desc") -> Dict[str, Any]:
    """
    获取所有文章
    
    Args:
        page: 页码，从1开始
        size: 每页结果数
        sort_by: 排序字段，默认为发布时间
        sort_order: 排序顺序，默认为降序
    
    Returns:
        Dict: 包含文章列表的字典
    """
    try:
        # 计算偏移量
        from_val = (page - 1) * size
        
        # 构建查询，匹配所有文档
        search_query = {
            "query": {
                "match_all": {}
            },
            "sort": [
                {sort_by: {"order": sort_order}}
            ],
            "from": from_val,
            "size": size
        }
        
        # 执行搜索
        response = es_client.search(
            index=ES_ARTICLES_INDEX,
            body=search_query
        )
        
        # 处理结果
        hits = response["hits"]["hits"]
        total = response["hits"]["total"]["value"]
        
        # 提取文章数据
        articles = [hit["_source"] for hit in hits]
        
        return {
            "page": page,
            "size": size,
            "total": total,
            "articles": articles
        }
    
    except Exception as e:
        logger.error(f"获取所有文章时发生错误: {e}")
        return {
            "page": page,
            "size": size,
            "total": 0,
            "articles": [],
            "error": str(e)
        }

# 初始化索引
if __name__ != "__main__":
    initialize_indices() 