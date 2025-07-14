 """日志数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, JSON
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base

class Log(Base):
    """日志表模型"""
    __tablename__ = "logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    method = Column(String(10))
    path = Column(String(200))
    client = Column(String(50))
    data = Column(JSON)
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "method": self.method,
            "path": self.path,
            "client": self.client,
            "data": self.data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }