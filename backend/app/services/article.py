 """文章业务逻辑处理"""
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func

from ..models.article import Article
from ..services.search import index_article, delete_article_from_index, clear_index, reindex_all_articles

logger = logging.getLogger(__name__)

def find_articles_recursively(data: Any, max_depth: int = 5, current_depth: int = 0) -> List[Dict[str, Any]]:
    """
    递归查找数据结构中的文章列表
    
    Args:
        data: 要搜索的数据
        max_depth: 最大递归深度
        current_depth: 当前递归深度
    
    Returns:
        List: 找到的文章列表
    """
    # 防止过深递归
    if current_depth >= max_depth:
        return []
    
    # 如果是列表，检查是否为文章列表
    if isinstance(data, list) and len(data) > 0:
        # 检查第一个元素是否像文章
        if isinstance(data[0], dict) and any(k in data[0] for k in ['title', 'url', 'bizname']):
            return data
    
    # 如果是字典，递归检查所有值
    if isinstance(data, dict):
        for key, value in data.items():
            # 特别检查名为"data"的键
            if key == "data":
                if isinstance(value, list):
                    # 检查是否为文章列表
                    if len(value) > 0 and isinstance(value[0], dict) and any(k in value[0] for k in ['title', 'url', 'bizname']):
                        return value
                
                # 递归检查
                result = find_articles_recursively(value, max_depth, current_depth + 1)
                if result:
                    return result
            
            # 递归检查其他键
            result = find_articles_recursively(value, max_depth, current_depth + 1)
            if result:
                return result
    
    return []

def save_article_data(db: Session, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    保存文章数据
    
    Args:
        db: 数据库会话
        request_data: 包含文章数据的请求
    
    Returns:
        Dict: 包含保存结果的字典
    """
    try:
        logger.info(f"接收到的数据结构: {type(request_data)}")
        logger.info(f"数据顶层键: {list(request_data.keys()) if isinstance(request_data, dict) else '非字典'}")
        
        # 适应多种可能的数据结构
        articles = []
        
        # 检查是否有多层嵌套结构
        if isinstance(request_data, dict):
            logger.info("处理字典类型数据")
            
            # 情况1: 直接包含文章列表的数据结构 {"data": [...]}
            if "data" in request_data and isinstance(request_data["data"], list):
                logger.info("情况1: 数据直接包含文章列表")
                articles = request_data["data"]
                
            # 情况2: 更深层嵌套 {"data": {"data": {"data": [...]}}}
            elif "data" in request_data:
                data_level1 = request_data["data"]
                logger.info(f"数据第一层: {type(data_level1)}")
                
                if isinstance(data_level1, dict):
                    # 检查第二层
                    if "data" in data_level1:
                        data_level2 = data_level1["data"]
                        logger.info(f"数据第二层: {type(data_level2)}")
                        
                        # 可能是直接的文章列表
                        if isinstance(data_level2, list):
                            logger.info("情况2.1: 二层嵌套文章列表")
                            articles = data_level2
                            
                        # 可能还有第三层
                        elif isinstance(data_level2, dict):
                            if "data" in data_level2:
                                data_level3 = data_level2["data"]
                                logger.info(f"数据第三层: {type(data_level3)}")
                                
                                if isinstance(data_level3, list):
                                    logger.info("情况2.2: 三层嵌套文章列表")
                                    articles = data_level3
            
            # 如果仍未找到文章，尝试递归查找文章列表
            if not articles:
                logger.info("尝试递归查找文章列表")
                articles = find_articles_recursively(request_data)
        else:
            return {"success": False, "message": "请求数据格式不正确", "saved": 0}
        
        logger.info(f"找到 {len(articles)} 篇文章")
        
        if not articles:
            return {"success": False, "message": "没有找到文章数据", "saved": 0}
        
        saved_count = 0
        failed_count = 0
        
        for article_data in articles:
            try:
                # 生成唯一ID
                biz = article_data.get('biz', '')
                mid = article_data.get('mid', '')
                idx = article_data.get('idx', '')
                
                unique_id = f"{biz}-{mid}-{idx}"
                # 检查是否所有部分都存在
                parts = unique_id.split('-')
                if len(parts) != 3 or not all(parts) or unique_id == "--":
                    # 如果缺少任何部分，生成随机ID
                    logger.warning(f"文章缺少完整标识信息，使用随机ID: biz={biz}, mid={mid}, idx={idx}")
                    unique_id = str(uuid.uuid4())
                else:
                    logger.info(f"为文章生成唯一ID: {unique_id}")
                
                # 转换发布时间
                pub_time = article_data.get("pub_time", "")
                pub_time_iso = None
                if pub_time:
                    try:
                        pub_time_iso = datetime.fromtimestamp(int(pub_time))
                    except (ValueError, TypeError):
                        pub_time_iso = None
                
                # 检查文章是否已存在
                existing_article = db.query(Article).filter(Article.unique_id == unique_id).first()
                
                if existing_article:
                    # 更新现有文章
                    existing_article.url = article_data.get("url", existing_article.url)
                    existing_article.title = article_data.get("title", existing_article.title)
                    existing_article.digest = article_data.get("digest", existing_article.digest)
                    existing_article.pub_time = pub_time or existing_article.pub_time
                    existing_article.pub_time_iso = pub_time_iso or existing_article.pub_time_iso
                    existing_article.cover = article_data.get("cover", existing_article.cover)
                    existing_article.bizname = article_data.get("bizname", existing_article.bizname)
                    
                    article_obj = existing_article
                else:
                    # 创建新文章
                    article_obj = Article(
                        unique_id=unique_id,
                        url=article_data.get("url", ""),
                        title=article_data.get("title", ""),
                        digest=article_data.get("digest", ""),
                        pub_time=pub_time,
                        pub_time_iso=pub_time_iso,
                        cover=article_data.get("cover", ""),
                        bizname=article_data.get("bizname", ""),
                        biz=biz,
                        mid=mid,
                        idx=idx
                    )
                    db.add(article_obj)
                
                db.commit()
                
                # 同步到Elasticsearch
                index_result = index_article(article_obj.to_dict())
                if not index_result:
                    logger.warning(f"文章添加到MySQL成功，但索引到Elasticsearch失败: {unique_id}")
                
                saved_count += 1
                
            except Exception as item_error:
                logger.error(f"保存单篇文章时发生错误: {item_error}")
                failed_count += 1
                db.rollback()
        
        return {
            "success": True,
            "message": f"成功保存 {saved_count} 篇文章，失败 {failed_count} 篇",
            "saved": saved_count,
            "failed": failed_count
        }
        
    except Exception as e:
        logger.error(f"保存文章数据时发生错误: {e}")
        return {"success": False, "message": f"保存文章数据时发生错误: {str(e)}", "saved": 0}

def get_all_articles(
    db: Session, page: int = 1, size: int = 20, 
    sort_by: str = "pub_time_iso", sort_order: str = "desc"
) -> Dict[str, Any]:
    """获取所有文章"""
    try:
        # 计算偏移量
        skip = (page - 1) * size
        
        # 确定排序方式
        if hasattr(Article, sort_by):
            order_column = getattr(Article, sort_by)
            if sort_order.lower() == "desc":
                order_column = desc(order_column)
            else:
                order_column = asc(order_column)
        else:
            order_column = desc(Article.pub_time_iso)
        
        # 查询总数
        total = db.query(Article).count()
        
        # 查询数据
        articles = db.query(Article).order_by(order_column).offset(skip).limit(size).all()
        
        # 转换为字典列表
        result = [article.to_dict() for article in articles]
        
        return {
            "page": page,
            "size": size,
            "total": total,
            "articles": result
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

def get_articles_by_ids(db: Session, unique_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """根据ID列表获取文章"""
    try:
        if not unique_ids:
            return {}
            
        articles = db.query(Article).filter(Article.unique_id.in_(unique_ids)).all()
        
        # 转换为以ID为键的字典
        result = {article.unique_id: article.to_dict() for article in articles}
        
        return result
        
    except Exception as e:
        logger.error(f"根据ID获取文章时发生错误: {e}")
        return {}

def delete_article_by_id(db: Session, article_id: str) -> Dict[str, Any]:
    """删除指定ID的文章"""
    try:
        article = db.query(Article).filter(Article.unique_id == article_id).first()
        
        if not article:
            return {
                "success": False,
                "message": f"未找到文章 ID: {article_id}",
                "deleted": False
            }
        
        # 从MySQL删除
        db.delete(article)
        db.commit()
        
        # 从Elasticsearch删除
        delete_result = delete_article_from_index(article_id)
        if not delete_result:
            logger.warning(f"从MySQL删除文章成功，但从Elasticsearch删除失败: {article_id}")
        
        return {
            "success": True,
            "message": f"成功删除文章 ID: {article_id}",
            "deleted": True
        }
        
    except Exception as e:
        logger.error(f"删除文章时发生错误: {e}")
        db.rollback()
        return {
            "success": False,
            "message": f"删除文章时发生错误: {str(e)}",
            "deleted": False
        }

def clear_articles(db: Session) -> Dict[str, Any]:
    """清空所有文章"""
    try:
        # 从MySQL删除所有文章
        db.query(Article).delete()
        db.commit()
        
        # 从Elasticsearch清空索引
        clear_result = clear_index()
        
        if clear_result["success"]:
            return {
                "success": True,
                "message": "所有文章已清空"
            }
        else:
            return {
                "success": True,
                "message": f"MySQL文章已清空，但ES索引操作状态: {clear_result['message']}"
            }
            
    except Exception as e:
        logger.error(f"清空文章时发生错误: {e}")
        db.rollback()
        return {
            "success": False,
            "message": f"清空文章时发生错误: {str(e)}"
        }

def add_single_article(db: Session, article_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    添加单篇文章
    
    Args:
        db: 数据库会话
        article_data: 文章数据
    
    Returns:
        Dict: 包含操作结果的字典
    """
    try:
        if not article_data:
            return {"success": False, "message": "文章数据为空", "saved": 0}
            
        # 生成唯一ID
        biz = article_data.get('biz', '')
        mid = article_data.get('mid', '')
        idx = article_data.get('idx', '')
        
        unique_id = f"{biz}-{mid}-{idx}"
        # 检查是否所有部分都存在
        parts = unique_id.split('-')
        if len(parts) != 3 or not all(parts) or unique_id == "--":
            # 如果缺少任何部分，生成随机ID
            logger.warning(f"文章缺少完整标识信息，使用随机ID: biz={biz}, mid={mid}, idx={idx}")
            unique_id = str(uuid.uuid4())
        
        # 转换发布时间
        pub_time = article_data.get("pub_time", "")
        pub_time_iso = None
        if pub_time:
            try:
                pub_time_iso = datetime.fromtimestamp(int(pub_time))
            except (ValueError, TypeError):
                pub_time_iso = None
        
        # 检查文章是否已存在
        existing_article = db.query(Article).filter(Article.unique_id == unique_id).first()
        
        if existing_article:
            # 更新现有文章
            existing_article.url = article_data.get("url", existing_article.url)
            existing_article.title = article_data.get("title", existing_article.title)
            existing_article.digest = article_data.get("digest", existing_article.digest)
            existing_article.pub_time = pub_time or existing_article.pub_time
            existing_article.pub_time_iso = pub_time_iso or existing_article.pub_time_iso
            existing_article.cover = article_data.get("cover", existing_article.cover)
            existing_article.bizname = article_data.get("bizname", existing_article.bizname)
            
            db.commit()
            
            # 同步到Elasticsearch
            index_article(existing_article.to_dict())
            
            return {
                "success": True,
                "message": f"成功更新文章: {existing_article.title}",
                "id": unique_id,
                "article": existing_article.to_dict()
            }
        else:
            # 创建新文章
            article = Article(
                unique_id=unique_id,
                url=article_data.get("url", ""),
                title=article_data.get("title", ""),
                digest=article_data.get("digest", ""),
                pub_time=pub_time,
                pub_time_iso=pub_time_iso,
                cover=article_data.get("cover", ""),
                bizname=article_data.get("bizname", ""),
                biz=biz,
                mid=mid,
                idx=idx
            )
            
            db.add(article)
            db.commit()
            db.refresh(article)
            
            # 同步到Elasticsearch
            index_article(article.to_dict())
            
            return {
                "success": True,
                "message": f"成功添加文章: {article.title}",
                "id": unique_id,
                "article": article.to_dict()
            }
            
    except Exception as e:
        logger.error(f"添加文章时发生错误: {e}")
        db.rollback()
        return {
            "success": False,
            "message": f"添加文章时发生错误: {str(e)}",
            "saved": 0
        }

def rebuild_search_index(db: Session) -> Dict[str, Any]:
    """重建搜索索引"""
    try:
        # 从MySQL获取所有文章
        articles = db.query(Article).all()
        
        # 转换为字典列表
        articles_dict = [article.to_dict() for article in articles]
        
        # 重建索引
        result = reindex_all_articles(articles_dict)
        
        return result
        
    except Exception as e:
        logger.error(f"重建搜索索引时发生错误: {e}")
        return {
            "success": False,
            "message": f"重建搜索索引时发生错误: {str(e)}",
            "indexed": 0
        }