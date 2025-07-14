 """搜索引擎服务"""
import os
import logging
from typing import Dict, List, Any
from datetime import datetime
from elasticsearch import Elasticsearch, helpers

# 配置
ES_HOST = os.environ.get("ES_HOST", "localhost")
ES_PORT = os.environ.get("ES_PORT", "9200")
ES_INDEX = os.environ.get("ES_INDEX", "wechat_articles")

# 创建Elasticsearch客户端
try:
    es_client = Elasticsearch(f"http://{ES_HOST}:{ES_PORT}")
    if es_client.ping():
        logging.info(f"Elasticsearch连接成功: {ES_HOST}:{ES_PORT}")
    else:
        logging.warning(f"Elasticsearch连接失败: {ES_HOST}:{ES_PORT}")
except Exception as e:
    logging.error(f"Elasticsearch连接错误: {e}")
    # 创建一个空的客户端，避免程序崩溃
    es_client = None

# 配置日志
logger = logging.getLogger(__name__)

# 索引映射（简化版，仅用于搜索）
INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "unique_id": {"type": "keyword"},
            "title": {"type": "text", "analyzer": "standard"},
            "digest": {"type": "text", "analyzer": "standard"},
            "bizname": {"type": "text", "analyzer": "standard"},
            "pub_time_iso": {"type": "date"},
            "created_at": {"type": "date"}
        }
    }
}

def init_search_index():
    """初始化搜索索引"""
    if not es_client:
        logger.error("Elasticsearch客户端未初始化，无法创建索引")
        return False
        
    try:
        if not es_client.indices.exists(index=ES_INDEX):
            es_client.indices.create(index=ES_INDEX, body=INDEX_MAPPING)
            logger.info(f"创建搜索索引: {ES_INDEX}")
        return True
    except Exception as e:
        logger.error(f"初始化搜索索引时发生错误: {e}")
        return False

def index_article(article: Dict[str, Any]) -> bool:
    """将文章索引到Elasticsearch"""
    if not es_client:
        logger.error("Elasticsearch客户端未初始化，无法索引文章")
        return False
        
    try:
        # 准备索引文档（只包含搜索需要的字段）
        doc = {
            "unique_id": article["unique_id"],
            "title": article["title"],
            "digest": article["digest"] or "",
            "bizname": article["bizname"] or "",
            "pub_time_iso": article["pub_time_iso"],
            "created_at": datetime.now().isoformat()
        }
        
        # 索引文档
        es_client.index(
            index=ES_INDEX,
            id=article["unique_id"],
            document=doc,
            refresh=True
        )
        return True
    except Exception as e:
        logger.error(f"索引文章时发生错误: {e}")
        return False

def delete_article_from_index(article_id: str) -> bool:
    """从索引中删除文章"""
    if not es_client:
        logger.error("Elasticsearch客户端未初始化，无法删除文章")
        return False
        
    try:
        es_client.delete(index=ES_INDEX, id=article_id, refresh=True)
        return True
    except Exception as e:
        logger.error(f"从索引中删除文章时发生错误: {e}")
        return False

def clear_index() -> Dict[str, Any]:
    """清空索引"""
    if not es_client:
        logger.error("Elasticsearch客户端未初始化，无法清空索引")
        return {"success": False, "message": "Elasticsearch客户端未初始化"}
        
    try:
        if es_client.indices.exists(index=ES_INDEX):
            es_client.indices.delete(index=ES_INDEX)
            es_client.indices.create(index=ES_INDEX, body=INDEX_MAPPING)
            return {"success": True, "message": "索引已重建"}
        else:
            es_client.indices.create(index=ES_INDEX, body=INDEX_MAPPING)
            return {"success": True, "message": "索引已创建"}
    except Exception as e:
        logger.error(f"清空索引时发生错误: {e}")
        return {"success": False, "message": f"清空索引时发生错误: {str(e)}"}

def search_articles(query: str, page: int = 1, size: int = 10) -> Dict[str, Any]:
    """搜索文章"""
    if not es_client:
        logger.error("Elasticsearch客户端未初始化，无法搜索文章")
        return {
            "query": query,
            "page": page,
            "size": size,
            "total": 0,
            "took": 0,
            "results": [],
            "error": "Elasticsearch未连接"
        }
        
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
                "post_tags": ["</em>"]
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
        response = es_client.search(index=ES_INDEX, body=search_query)
        end_time = datetime.now()
        took_ms = (end_time - start_time).total_seconds() * 1000
        
        # 获取匹配的文档ID列表
        unique_ids = [hit["_id"] for hit in response["hits"]["hits"]]
        
        # 返回搜索结果和高亮信息
        total = response["hits"]["total"]["value"] if "hits" in response and "total" in response["hits"] else 0
        results = []
        
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            highlight = hit.get("highlight", {})
            
            # 从ES返回唯一ID，实际数据需要从MySQL获取
            doc = {
                "unique_id": source["unique_id"],
                "title": highlight["title"][0] if "title" in highlight else source["title"],
                "digest": "...".join(highlight["digest"]) if "digest" in highlight and highlight["digest"] else source.get("digest", ""),
                "bizname": source.get("bizname", ""),
                "pub_time_iso": source.get("pub_time_iso")
            }
            results.append(doc)
        
        return {
            "query": query,
            "page": page,
            "size": size,
            "total": total,
            "took": took_ms,
            "results": results,
            "unique_ids": unique_ids  # 用于从MySQL获取完整数据
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

def reindex_all_articles(articles: List[Dict]) -> Dict[str, Any]:
    """重建所有文章的搜索索引"""
    if not es_client:
        logger.error("Elasticsearch客户端未初始化，无法重建索引")
        return {"success": False, "message": "Elasticsearch未连接", "indexed": 0}
        
    try:
        # 清空现有索引
        clear_result = clear_index()
        if not clear_result["success"]:
            return clear_result
            
        # 批量索引文章
        success_count = 0
        failed_count = 0
        
        for article in articles:
            if index_article(article):
                success_count += 1
            else:
                failed_count += 1
                
        return {
            "success": True,
            "message": f"成功索引 {success_count} 篇文章，失败 {failed_count} 篇",
            "indexed": success_count,
            "failed": failed_count
        }
    except Exception as e:
        logger.error(f"重建索引时发生错误: {e}")
        return {"success": False, "message": f"重建索引时发生错误: {str(e)}", "indexed": 0}