#!/usr/bin/env python
"""
从Elasticsearch迁移数据到MySQL
"""
import logging
from elasticsearch import Elasticsearch, helpers
from sqlalchemy.orm import Session

from app.models.database import SessionLocal, engine, Base
from app.models.article import Article
import app.services.search as search_service

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ES配置
ES_HOST = "localhost"
ES_PORT = "9200"
ES_ARTICLES_INDEX = "wechat_articles"

# 创建Elasticsearch客户端
es_client = Elasticsearch(f"http://{ES_HOST}:{ES_PORT}")

def migrate_data():
    """迁移数据"""
    try:
        # 创建数据库表（如果不存在）
        Base.metadata.create_all(bind=engine)
        
        # 获取DB会话
        db = SessionLocal()
        
        # 查询现有的Elasticsearch数据
        query = {"query": {"match_all": {}}, "size": 1000}
        results = helpers.scan(es_client, query=query, index=ES_ARTICLES_INDEX)
        
        # 计数器
        migrated_count = 0
        failed_count = 0
        
        for result in results:
            try:
                source = result["_source"]
                unique_id = source.get("unique_id") or result["_id"]
                
                # 检查文章是否已存在
                existing = db.query(Article).filter(Article.unique_id == unique_id).first()
                if existing:
                    logger.info(f"文章已存在，跳过: {unique_id}")
                    continue
                
                # 创建新文章
                article = Article(
                    unique_id=unique_id,
                    url=source.get("url", ""),
                    title=source.get("title", ""),
                    digest=source.get("digest", ""),
                    pub_time=source.get("pub_time"),
                    pub_time_iso=source.get("pub_time_iso"),
                    cover=source.get("cover", ""),
                    bizname=source.get("bizname", ""),
                    biz=source.get("biz", ""),
                    # 尽可能提取mid和idx
                    mid=unique_id.split("-")[1] if "-" in unique_id else None,
                    idx=unique_id.split("-")[2] if len(unique_id.split("-")) > 2 else None
                )
                
                db.add(article)
                db.commit()
                
                # 确保搜索索引也是最新的
                search_service.index_article(article.to_dict())
                
                migrated_count += 1
                logger.info(f"已迁移文章 {migrated_count}: {unique_id}")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"迁移文章失败: {e}")
                db.rollback()
        
        logger.info(f"迁移完成。成功: {migrated_count}, 失败: {failed_count}")
        
    except Exception as e:
        logger.error(f"迁移过程中发生错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("开始迁移数据从Elasticsearch到MySQL...")
    migrate_data()