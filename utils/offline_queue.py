import json
import os
from utils.logger import logger

QUEUE_FILE = "logs/offline_queue.json"

class OfflineQueue:
    def __init__(self):
        # 파일이 없으면 새로 생성
        if not os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, "w") as f:
                json.dump([], f)

    def add(self, record):
        """Cloud 업로드 실패 시 로컬 큐에 저장"""
        with open(QUEUE_FILE, "r") as f:
            data = json.load(f)

        data.append(record)

        with open(QUEUE_FILE, "w") as f:
            json.dump(data, f)

        logger.warning(f"[OFFLINE] 저장됨 → {record}")

    def flush(self, uploader):
        """인터넷 연결 복구 시 큐 비우고 업로드"""
        with open(QUEUE_FILE, "r") as f:
            data = json.load(f)

        if not data:
            return

        new_queue = []
        for item in data:
            success = uploader(item)
            if not success:
                new_queue.append(item)

        with open(QUEUE_FILE, "w") as f:
            json.dump(new_queue, f)

        logger.info(f"[OFFLINE] Flush 완료. 남은 개수: {len(new_queue)}")
