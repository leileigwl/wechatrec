 """文章数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base

class Article(Base):
    """文章表模型"""
    __tablename__ = "articles"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    unique_id = Column(String(100), unique=True, nullable=False)
    url = Column(String(500), nullable=False)
    title = Column(String(200), nullable=False)
    digest = Column(Text)
    pub_time = Column(BigInteger)
    pub_time_iso = Column(DateTime)
    cover = Column(String(500))
    bizname = Column(String(100))
    biz = Column(String(100))
    mid = Column(String(100))
    idx = Column(String(10))
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "unique_id": self.unique_id,
            "url": self.url,
            "title": self.title,
            "digest": self.digest,
            "pub_time": self.pub_time,
            "pub_time_iso": self.pub_time_iso.isoformat() if self.pub_time_iso else None,
            "cover": self.cover,
            "bizname": self.bizname,
            "biz": self.biz,
            "mid": self.mid,
            "idx": self.idx,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }