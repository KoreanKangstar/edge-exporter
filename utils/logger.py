import logging
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "edge.log")
ERROR_FILE = os.path.join(LOG_DIR, "error.log")

os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("edge")
logger.setLevel(logging.INFO)

# Info log
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)

# Error log
error_handler = logging.FileHandler(ERROR_FILE)
error_handler.setLevel(logging.ERROR)

# 로그 형태 지정
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

# 핸들러 등록
logger.addHandler(file_handler)
logger.addHandler(error_handler)
