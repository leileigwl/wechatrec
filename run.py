 #!/usr/bin/env python
"""
启动WeChat文章搜索系统
"""
import os
import sys
import logging
import uvicorn
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def main():
    """主函数"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 启动FastAPI应用
    uvicorn.run(
        "backend.app.fastapiServer:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()