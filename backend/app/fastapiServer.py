"""
FastAPI server for WeChat article search system.
"""
import os
import logging
from fastapi import FastAPI, Request, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# 导入数据库依赖
from app.models.database import get_db, engine, Base
import app.models.article
import app.models.log

# 导入业务逻辑
from app.services import article as article_service
from app.services import search as search_service
from app.services import log as log_service

# 初始化数据库表
Base.metadata.create_all(bind=engine)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="WeChat Article Search API",
    description="API for searching WeChat articles using MySQL + Elasticsearch",
    version="2.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化搜索索引
search_service.init_search_index()

# API端点定义（保持兼容现有API）
@app.post("/artlist/")
async def save_articles(request: Request, db: Session = Depends(get_db)):
    """保存文章列表"""
    try:
        data = await request.json()
        result = article_service.save_article_data(db, data)
        
        # 记录日志
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host,
            "data": {
                "request": data,
                "response": result
            }
        }
        log_service.save_log(db, log_data)
        
        return result
    except Exception as e:
        logger.error(f"处理请求时发生错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/")
async def search(
    q: str = Query(..., description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=50, description="每页结果数"),
    db: Session = Depends(get_db)
):
    """搜索文章"""
    try:
        # 首先用ES搜索
        search_result = search_service.search_articles(q, page, size)
        
        # 如果有匹配结果，从MySQL获取完整数据
        if search_result["total"] > 0 and "unique_ids" in search_result:
            unique_ids = search_result["unique_ids"]
            # 从MySQL获取完整的文章数据
            # 这个功能需要在article_service中实现
            
            # 将完整数据与高亮结果合并
            # ...
        
        return search_result
    except Exception as e:
        logger.error(f"搜索文章时发生错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/articles/")
async def get_articles(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页结果数"),
    sort_by: str = Query("pub_time_iso", description="排序字段"),
    sort_order: str = Query("desc", description="排序顺序"),
    db: Session = Depends(get_db)
):
    """获取所有文章"""
    return article_service.get_all_articles(db, page, size, sort_by, sort_order)

@app.delete("/article/{article_id}")
async def delete_article(article_id: str, db: Session = Depends(get_db)):
    """删除指定ID的文章"""
    return article_service.delete_article_by_id(db, article_id)

@app.delete("/articles/all")
async def clear_all_articles(db: Session = Depends(get_db)):
    """清空所有文章"""
    return article_service.clear_articles(db)

# [其他API端点保持不变]