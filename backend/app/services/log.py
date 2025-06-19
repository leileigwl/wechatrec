 """日志服务"""
import logging
from typing import Dict, List, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.log import Log

logger = logging.getLogger(__name__)

def save_log(db: Session, log_data: Dict[str, Any]) -> bool:
    """保存日志到数据库"""
    try:
        # 准备日志数据
        new_log = Log(
            timestamp=datetime.now(),
            method=log_data.get("method"),
            path=log_data.get("path"),
            client=log_data.get("client"),
            data=log_data.get("data")
        )
        
        db.add(new_log)
        db.commit()
        
        return True
    except Exception as e:
        logger.error(f"保存日志时发生错误: {e}")
        db.rollback()
        return False

def get_logs(
    db: Session, 
    start_time: datetime = None, 
    end_time: datetime = None,
    page: int = 1, 
    size: int = 50
) -> Dict[str, Any]:
    """获取日志"""
    try:
        # 基本查询
        query = db.query(Log)
        
        # 应用时间过滤
        if start_time:
            query = query.filter(Log.timestamp >= start_time)
        if end_time:
            query = query.filter(Log.timestamp <= end_time)
        
        # 计算总数
        total = query.count()
        
        # 分页
        skip = (page - 1) * size
        logs = query.order_by(desc(Log.timestamp)).offset(skip).limit(size).all()
        
        # 转换为字典列表
        result = [log.to_dict() for log in logs]
        
        return {
            "page": page,
            "size": size,
            "total": total,
            "logs": result
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