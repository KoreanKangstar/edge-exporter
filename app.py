from fastapi import FastAPI, Response
from prometheus_client import Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
import psutil
import time
import requests

from utils.logger import logger
from utils.offline_queue import OfflineQueue

app = FastAPI()
queue = OfflineQueue()

CLOUD_LOG_ENDPOINT = "http://your-cloud-address/log"

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

    payload = {
        "edge_cpu_usage": cpu,
        "edge_ram_usage": ram,
        "edge_disk_usage": disk,
        "edge_temperature": temp,
        "edge_heartbeat_total": heartbeat,
    }

    # 로컬 로그 남김
    logger.info(f"Metrics: {payload}")

    # Cloud 업로드 시도
    success = upload_to_cloud(payload)
    if not success:
        queue.add(payload)
    queue.flush(upload_to_cloud)

    # Prometheus 포맷 생성
    reg = CollectorRegistry()

    g1 = Gauge("edge_cpu_usage", "CPU Usage (%)", registry=reg)
    g2 = Gauge("edge_ram_usage", "RAM Usage (%)", registry=reg)
    g3 = Gauge("edge_disk_usage", "Disk Usage (%)", registry=reg)
    g4 = Gauge("edge_temperature", "Device Temperature (°C)", registry=reg)
    g5 = Gauge("edge_heartbeat_total", "Heartbeat Counter", registry=reg)

    g1.set(cpu)
    g2.set(ram)
    g3.set(disk)
    g4.set(temp)
    g5.set(heartbeat)

    metrics_data = generate_latest(reg)
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
