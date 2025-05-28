import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import json
import traceback
from bs4 import BeautifulSoup
from bson import ObjectId  # Import ObjectId from bson

# 导入你的工具函数
from WxartDownloader import DownArtList, SaveFile, get_current_time_string
# 导入MongoDB工具函数
from mongo_utils import save_article_data, save_log, get_articles, get_logs

# Create a custom JSON encoder for MongoDB ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)  # Convert ObjectId to string
        return super().default(obj)

# 配置目录
SaveJsonDir = "/artlist/json"  # 修改为 Linux 路径
LogsDir = "/artlist/logs"      # 日志目录

# 创建目录
os.makedirs(SaveJsonDir, exist_ok=True)
os.makedirs(LogsDir, exist_ok=True)

downArtFlag = True  # 是否下载文章

app = FastAPI()

# 添加日志记录函数
def log_request(request: Request, json_data: dict):
    """记录请求日志"""
    # 获取客户端IP
    client_host = request.client.host if request.client else "unknown"
    
    # 创建日志条目
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "method": request.method,
        "path": str(request.url.path),
        "client": client_host,
        "data": json_data
    }
    
    # 保存到MongoDB
    save_log(log_entry)
    
    # 获取日志文件名（按日期）- 同时保留文件记录
    log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
    log_path = os.path.join(LogsDir, log_filename)
    
    # 写入日志 - 使用自定义encoder
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_entry, ensure_ascii=False, cls=MongoJSONEncoder) + "\n")

# 主接口，保存文章列表
@app.post("/artlist/")
async def artlist(request: Request):
    try:
        # 获取请求数据
        json_data = await request.json()
        
        # 记录日志
        log_request(request, json_data)
        
        # 保存到MongoDB
        save_article_data(json_data)
        
        # 保存发过来的json数据到文件系统
        current_time = get_current_time_string() + ".txt"
        savepath = os.path.join(SaveJsonDir, current_time)
        SaveFile(savepath, json.dumps(json_data, ensure_ascii=False, indent=4, cls=MongoJSONEncoder))
        
        # 下载文章（如果启用）
        if downArtFlag:
            DownArtList(json_data)
        
        return "success"
    except Exception as e:
        print(traceback.format_exc())
        return "error"

# 新增接口，查看日志
@app.get("/logs/")
async def view_logs(date: str = None, limit: int = 100):
    """
    查看日志接口
    参数:
        date: 指定日期（格式：YYYY-MM-DD）
        limit: 返回的最大日志条数
    """
    try:
        # 首先尝试从MongoDB获取
        logs = get_logs(limit=limit, date=date)
        
        # 如果MongoDB没有数据，从文件系统获取
        if not logs:
            # 获取所有日志文件
            log_files = []
            for filename in os.listdir(LogsDir):
                if filename.endswith(".log"):
                    log_files.append(filename)
            
            # 如果指定了日期，只处理该日期的日志
            if date:
                log_filename = f"{date}.log"
                if log_filename not in log_files:
                    return JSONResponse(
                        status_code=404,
                        content={"error": f"日志文件 {log_filename} 不存在"}
                    )
                log_files = [log_filename]
            
            # 读取和整理日志
            logs = []
            for filename in log_files:
                log_path = os.path.join(LogsDir, filename)
                with open(log_path, "r", encoding="utf-8") as log_file:
                    for line in log_file:
                        try:
                            log_entry = json.loads(line.strip())
                            logs.append(log_entry)
                        except json.JSONDecodeError:
                            continue
            
            # 按时间倒序排序并限制数量
            logs.sort(key=lambda x: x["timestamp"], reverse=True)
            if limit > 0:
                logs = logs[:limit]
        
        # 使用自定义encoder处理ObjectId
        return JSONResponse(content=json.loads(json.dumps(logs, cls=MongoJSONEncoder)))
    
    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# 新增接口，从MongoDB获取文章列表
@app.get("/articles/")
async def get_article_list(limit: int = 100, skip: int = 0, biz: str = None):
    """
    从MongoDB获取文章列表
    参数:
        limit: 返回的最大文章数
        skip: 跳过的文章数（用于分页）
        biz: 公众号biz参数（可选，用于筛选）
    """
    try:
        query = {}
        if biz:
            query = {"data.biz": biz}
            
        articles = get_articles(limit=limit, skip=skip, query=query)
        # 使用自定义encoder处理ObjectId
        return JSONResponse(content=json.loads(json.dumps(articles, cls=MongoJSONEncoder)))
    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# 新增接口，查看日志文件列表
@app.get("/logfiles/")
async def list_log_files():
    """查看所有日志文件"""
    try:
        log_files = []
        for filename in os.listdir(LogsDir):
            if filename.endswith(".log"):
                file_path = os.path.join(LogsDir, filename)
                file_info = {
                    "filename": filename,
                    "size": os.path.getsize(file_path),
                    "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                }
                log_files.append(file_info)
        
        # 按日期排序
        log_files.sort(key=lambda x: x["filename"], reverse=True)
        
        return JSONResponse(content=log_files)
    
    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )