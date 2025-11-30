
---

# ✅ **README.md — 최종 완성본 (그대로 복붙하면 됨)**

아래 전체를 통째로 복사해서 `README.md` 파일에 넣어주세요.

---

````md
# 🚀 Edge Exporter  
Lightweight Edge Metrics Exporter with Full Logging System, Offline Mode, and Systemd Auto-Restart

---

## 📌 Overview

이 프로젝트는 Edge 디바이스(예: OrangePi, RaspberryPi 등)에서  
**CPU / RAM / Disk / Temperature / Heartbeat** 메트릭을 실시간 수집하고  
Cloud로 업로드하는 Exporter입니다.

네트워크가 끊겨도 메트릭은 **오프라인 큐(JSON)에 저장되며**,  
연결이 복구되면 자동으로 Cloud에 업로드됩니다.

또한 Systemd로 **자동 실행 / 자동 재시작 / 로그 관리**까지 구성되어  
Edge 단독 환경에서도 안정적으로 동작합니다.

---

# ✔ Features

### ✅ Metrics Export
- CPU Usage
- RAM Usage
- Disk Usage
- Temperature
- Heartbeat

### ✅ Full Logging System
- Info 및 Error 로그 분리
- 로그 파일을 자동 생성하여 로컬에 기록
- Cloud 업로드 실패 시 자동 큐잉

### ✅ Offline Mode
네트워크가 끊기면:

> Cloud 업로드 → 실패 → `offline_queue.json`에 자동 저장  

네트워크 복구 시:

> queue.flush()를 통해 누적된 데이터를 Cloud에 자동 업로드

### ✅ Systemd Auto-Restart
- 부팅 시 자동 실행  
- crash 시 자동 재시작  
- stdout/stderr → systemd log로 통합

---

# 📁 Project Structure

```txt
edge-exporter/
├── app.py
├── requirements.txt
├── run.sh
├── Dockerfile
├── utils/
│   ├── logger.py
│   └── offline_queue.py
└── logs/
    ├── edge.log
    ├── error.log
    └── offline_queue.json
````

---

# 📁 Logging Folder Structure

```txt
logs/
├── edge.log            # Info logs
├── error.log           # Error logs
└── offline_queue.json  # Offline queued entries
```

---

# ⚙ utils/logger.py

```python
import logging
import os

log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger("edge")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(os.path.join(log_dir, "edge.log"))
file_handler.setLevel(logging.INFO)

error_handler = logging.FileHandler(os.path.join(log_dir, "error.log"))
error_handler.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(error_handler)
```

---

# ⚙ utils/offline_queue.py

```python
import json
import os

QUEUE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "offline_queue.json")

class OfflineQueue:
    def __init__(self):
        if not os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, "w") as f:
                json.dump([], f)

    def add(self, data):
        with open(QUEUE_FILE, "r") as f:
            q = json.load(f)

        q.append(data)

        with open(QUEUE_FILE, "w") as f:
            json.dump(q, f, indent=2)

    def flush(self, upload_fn):
        with open(QUEUE_FILE, "r") as f:
            q = json.load(f)

        new_q = []
        for item in q:
            if not upload_fn(item):
                new_q.append(item)

        with open(QUEUE_FILE, "w") as f:
            json.dump(new_q, f, indent=2)
```

---

# ⚙ app.py

```python
from fastapi import FastAPI
import psutil
import time
import requests
from utils.logger import logger
from utils.offline_queue import OfflineQueue

app = FastAPI()
queue = OfflineQueue()

CLOUD_LOG_ENDPOINT = "http://127.0.0.1:9999/log"   # Cloud API endpoint

def upload_to_cloud(payload):
    try:
        r = requests.post(CLOUD_LOG_ENDPOINT, json=payload, timeout=3)
        return r.status_code == 200
    except:
        return False

@app.get("/metrics")
def metrics():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp = float(f.read()) / 1000.0
    except:
        temp = -1

    heartbeat = int(time.time())

    data = {
        "edge_cpu_usage": cpu,
        "edge_ram_usage": ram,
        "edge_disk_usage": disk,
        "edge_temperature": temp,
        "edge_heartbeat_total": heartbeat
    }

    logger.info(f"Metrics sent: {data}")

    success = upload_to_cloud(data)
    if not success:
        queue.add(data)

    queue.flush(upload_to_cloud)

    return data
```

---

# 🔧 Systemd service

`/etc/systemd/system/edge-exporter.service`

```ini
[Unit]
Description=Edge Metrics Exporter
After=network.target

[Service]
ExecStart=/usr/bin/python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
WorkingDirectory=/home/orangepi/edge-exporter
Restart=always
RestartSec=2
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

---

# ▶ Systemd Commands

```bash
sudo systemctl daemon-reload
sudo systemctl enable edge-exporter
sudo systemctl restart edge-exporter
sudo systemctl status edge-exporter
```

---

# 🧪 Local Test

```bash
curl http://localhost:8000/metrics
cat logs/offline_queue.json
```

---

# 📡 Next Steps (Cloud 팀 연동 필요)

* Cloud에서 `/log` API 열어주면 즉시 연동 가능
* Cloud → K8s → Prometheus → Grafana까지 확장 가능
* Edge → Cloud 실시간 로그 스트리밍 구성 가능

---

# 🏁 Done

Edge Exporter는 아래 기능을 모두 제공하며 Cloud 연동 준비가 완료되었습니다:

* Full metrics
* Full logging
* Offline queue
* Auto restart (systemd)
* Lightweight & stable

Cloud 팀 환경만 준비되면 실시간 로그 업로드가 바로 연결됩니다.

```

---

