 #!/usr/bin/env python
"""
从Elasticsearch迁移数据到MySQL
"""
import os
import sys
import logging
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
from sqlalchemy.orm import Session

# 添加当前目录到路径，确保可以导入app包
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, engine, Base
from app.models.article import Article
import app.services.search as search_service

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ES配置
ES_HOST = os.environ.get("ES_HOST", "localhost")
ES_PORT = os.environ.get("ES_PORT", "9200")
ES_ARTICLES_INDEX = os.environ.get("ES_INDEX", "wechat_articles")

# 创建Elasticsearch客户端
try:
    es_client = Elasticsearch(f"http://{ES_HOST}:{ES_PORT}")
    if es_client.ping():
        logger.info(f"Elasticsearch连接成功: {ES_HOST}:{ES_PORT}")
    else:
        logger.error(f"Elasticsearch连接失败: {ES_HOST}:{ES_PORT}")
        es_client = None
except Exception as e:
    logger.error(f"Elasticsearch连接错误: {e}")
    es_client = None

def migrate_data():
    """迁移数据"""
    try:
        if not es_client:
            logger.error("无法连接到Elasticsearch，迁移终止")
            return
            
        # 创建数据库表（如果不存在）
        Base.metadata.create_all(bind=engine)
        
        # 获取DB会话
        db = SessionLocal()
        
        try:
            # 检查索引是否存在
            if not es_client.indices.exists(index=ES_ARTICLES_INDEX):
                logger.error(f"索引 {ES_ARTICLES_INDEX} 不存在，迁移终止")
                return
                
            # 查询现有的Elasticsearch数据
            logger.info(f"开始从 {ES_ARTICLES_INDEX} 扫描文章...")
            query = {"query": {"match_all": {}}, "size": 1000}
            
            try:
                results = helpers.scan(es_client, query=query, index=ES_ARTICLES_INDEX)
            except Exception as scan_error:
                logger.error(f"扫描Elasticsearch索引时发生错误: {scan_error}")
                return
            
            # 计数器
            migrated_count = 0
            failed_count = 0
            
            logger.info("开始迁移文章...")
            
            for result in results:
                try:
                    source = result["_source"]
                    unique_id = source.get("unique_id") or result["_id"]
                    
                    # 检查文章是否已存在
                    existing = db.query(Article).filter(Article.unique_id == unique_id).first()
                    if existing:
                        logger.debug(f"文章已存在，跳过: {unique_id}")
                        continue
                    
                    # 处理pub_time_iso
                    pub_time = source.get("pub_time")
                    pub_time_iso = None
                    
                    if pub_time:
                        try:
                            pub_time_iso = datetime.fromtimestamp(int(pub_time))
                        except (ValueError, TypeError):
                            # 尝试直接解析iso格式
                            try:
                                pub_time_str = source.get("pub_time_iso")
                                if pub_time_str:
                                    pub_time_iso = datetime.fromisoformat(pub_time_str.replace('Z', '+00:00'))
                            except (ValueError, TypeError):
                                pass
                    
                    # 尝试从unique_id提取biz, mid, idx
                    biz, mid, idx = "", "", ""
                    if "-" in unique_id:
                        parts = unique_id.split("-")
                        if len(parts) >= 1:
                            biz = parts[0]
                        if len(parts) >= 2:
                            mid = parts[1]
                        if len(parts) >= 3:
                            idx = parts[2]
                    
                    # 创建新文章
                    article = Article(
                        unique_id=unique_id,
                        url=source.get("url", ""),
                        title=source.get("title", ""),
                        digest=source.get("digest", ""),
                        pub_time=pub_time,
                        pub_time_iso=pub_time_iso,
                        cover=source.get("cover", ""),
                        bizname=source.get("bizname", ""),
                        biz=source.get("biz") or biz,
                        mid=source.get("mid") or mid,
                        idx=source.get("idx") or idx
                    )
                    
                    db.add(article)
                    
                    # 每100条提交一次，减少数据库压力
                    migrated_count += 1
                    if migrated_count % 100 == 0:
                        db.commit()
                        logger.info(f"已迁移 {migrated_count} 篇文章")
                    
                except Exception as article_error:
                    failed_count += 1
                    logger.error(f"迁移文章时发生错误: {article_error}")
                    # 不中断整个迁移，继续下一篇
            
            # 最后提交一次
            db.commit()
            
            logger.info(f"迁移完成。成功: {migrated_count}, 失败: {failed_count}")
            
            # 重建搜索索引
            if migrated_count > 0:
                logger.info("开始重建搜索索引...")
                
                # 获取所有文章用于重建索引
                articles = db.query(Article).all()
                articles_dict = [article.to_dict() for article in articles]
                
                # 调用搜索服务重建索引
                reindex_result = search_service.reindex_all_articles(articles_dict)
                logger.info(f"索引重建结果: {reindex_result}")
            
        except Exception as db_error:
            logger.error(f"数据库操作时发生错误: {db_error}")
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"迁移过程中发生错误: {e}")

if __name__ == "__main__":
    logger.info("开始迁移数据从Elasticsearch到MySQL...")
    migrate_data()
    logger.info("迁移过程完成")