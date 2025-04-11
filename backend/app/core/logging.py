import logging
import sys
from typing import Any

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def get_logger(name: str) -> Any:
    """
    获取指定名称的日志记录器
    """
    return logging.getLogger(name)

# 创建默认日志记录器
logger = get_logger("app") 