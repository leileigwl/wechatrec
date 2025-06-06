"""
FastAPI server for WeChat article search system.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, Request, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from fastapi.concurrency import iterate_in_threadpool

from elasticsearch_utils import (
    save_article_data, 
    save_log, 
    search_articles, 
    get_logs,
    initialize_indices,  # 添加初始化索引函数
    delete_article,      # 添加删除文章函数
    clear_articles,      # 添加清空索引函数
    add_single_article,  # 添加单篇文章函数
    get_all_articles     # 添加获取所有文章函数
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="WeChat Article Search API",
    description="API for searching WeChat articles stored in Elasticsearch",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自定义响应中间件，确保高亮标签不被转义
@app.middleware("http")
async def prevent_html_escaping(request: Request, call_next):
    # 处理请求
    response = await call_next(request)
    
    # 检查是否是JSON响应
    if response.headers.get("content-type") == "application/json":
        # 读取响应内容
        body = [chunk async for chunk in response.body_iterator]
        # 使用iter()函数创建一个迭代器，而不是调用__iter__方法
        response.body_iterator = iterate_in_threadpool(iter(body))
    
    return response

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # 记录请求开始时间
    start_time = datetime.now()
    
    # 获取客户端IP
    client_host = request.client.host if request.client else "unknown"
    
    # 处理请求
    response = await call_next(request)
    
    # 计算请求处理时间
    process_time = (datetime.now() - start_time).total_seconds()
    
    # 记录请求信息
    logger.info(
        f"{request.method} {request.url.path} from {client_host} "
        f"completed in {process_time:.4f}s with status {response.status_code}"
    )
    
    return response

# 启动事件：初始化索引
@app.on_event("startup")
async def startup_event():
    logger.info("正在初始化Elasticsearch索引...")
    initialize_indices()
    logger.info("Elasticsearch索引初始化完成")

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# 保存文章数据
@app.post("/artlist/")
async def save_articles(request: Request):
    # 获取请求数据
    try:
        request_data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # 记录请求日志
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "path": request.url.path,
        "client": request.client.host if request.client else "unknown",
        "data": request_data
    }
    save_log(log_data)
    
    # 保存文章数据
    result = save_article_data(request_data)
    
    if not result.get("success", False):
        return JSONResponse(
            status_code=400,
            content=result
        )
    
    return result

# 搜索文章
@app.get("/search/")
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=50, description="Results per page")
):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    # 执行搜索
    results = search_articles(q, page, size)
    
    # 记录搜索请求
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "method": "GET",
        "path": "/search/",
        "client": "internal",
        "data": {"query": q, "page": page, "size": size}
    }
    save_log(log_data)
    
    return results

# 获取日志
@app.get("/logs/")
async def logs(
    start: Optional[str] = Query(None, description="Start time (ISO format)"),
    end: Optional[str] = Query(None, description="End time (ISO format)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Results per page")
):
    return get_logs(start, end, page, size)

# 数据管理端点

# 删除单篇文章
@app.delete("/article/{article_id}")
async def remove_article(article_id: str):
    """删除指定ID的文章"""
    result = delete_article(article_id)
    
    if not result.get("success", False):
        return JSONResponse(
            status_code=404 if "未找到" in result.get("message", "") else 400,
            content=result
        )
    
    return result

# 清空所有文章
@app.delete("/articles/all")
async def remove_all_articles():
    """清空所有文章（删除并重建索引）"""
    result = clear_articles()
    
    if not result.get("success", False):
        return JSONResponse(
            status_code=400,
            content=result
        )
    
    return result

# 添加单篇文章
@app.post("/article/")
async def add_article(request: Request):
    """添加单篇文章"""
    try:
        article_data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="无效的JSON格式")
    
    # 记录请求日志
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "path": request.url.path,
        "client": request.client.host if request.client else "unknown",
        "data": article_data
    }
    save_log(log_data)
    
    # 添加文章
    result = add_single_article(article_data)
    
    if not result.get("success", False):
        return JSONResponse(
            status_code=400,
            content=result
        )
    
    return result

# 获取所有文章
@app.get("/articles/")
async def get_articles(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页结果数"),
    sort_by: str = Query("pub_time_iso", description="排序字段"),
    sort_order: str = Query("desc", description="排序顺序")
):
    """获取所有文章，支持分页和排序"""
    return get_all_articles(page, size, sort_by, sort_order)

# 挂载静态文件（前端）
try:
    # 尝试多种可能的路径
    frontend_paths = ["../frontend", "../../frontend", "../../../frontend"]
    frontend_mounted = False
    
    for path in frontend_paths:
        if os.path.exists(path):
            try:
                # 单独挂载CSS、JS和图像目录
                if os.path.exists(os.path.join(path, "css")):
                    app.mount("/css", StaticFiles(directory=os.path.join(path, "css")), name="css")
                    logger.info(f"CSS文件已挂载，路径: {os.path.join(path, 'css')}")
                
                if os.path.exists(os.path.join(path, "js")):
                    app.mount("/js", StaticFiles(directory=os.path.join(path, "js")), name="js")
                    logger.info(f"JS文件已挂载，路径: {os.path.join(path, 'js')}")
                
                if os.path.exists(os.path.join(path, "img")):
                    app.mount("/img", StaticFiles(directory=os.path.join(path, "img")), name="img")
                    logger.info(f"图像文件已挂载，路径: {os.path.join(path, 'img')}")
                
                # 挂载整个前端目录
                app.mount("/", StaticFiles(directory=path, html=True), name="frontend")
                logger.info(f"前端静态文件已挂载，路径: {path}")
                frontend_mounted = True
                break
            except Exception as mount_error:
                logger.warning(f"尝试挂载 {path} 失败: {mount_error}")
    
    if not frontend_mounted:
        logger.warning("未找到前端静态文件目录")
except Exception as e:
    logger.warning(f"挂载前端静态文件失败: {e}")

# 主页
@app.get("/", include_in_schema=False)
async def root():
    # 尝试多种可能的路径
    frontend_paths = ["../frontend/index.html", "../../frontend/index.html", "../../../frontend/index.html"]
    
    for path in frontend_paths:
        if os.path.exists(path):
            return FileResponse(path)
    
    # 如果找不到前端文件，返回API信息
    return {"message": "WeChat Article Search API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapiServer:app", host="0.0.0.0", port=8000, reload=True) 