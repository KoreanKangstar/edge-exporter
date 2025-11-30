# 🛰️ Edge Exporter (FastAPI + Prometheus + Offline Queue)

이 프로젝트는 **Edge 디바이스(Orange Pi 5 등)** 에서  
CPU/RAM/DISK/TEMP/Heartbeat 정보를 수집하고,  
**Cloud로 로그를 업로드하는 Exporter 서비스**입니다.

Cloud 연결이 끊어져도 로그가 유실되지 않도록  
**Offline Queue (local JSON stack)** 를 구현해  
네트워크 복원 시 자동 업로드가 가능합니다.

또한 systemd 등록으로 **재부팅 자동 시작 + 장애 시 자동 복구** 기능도 탑재됩니다.

---

## 📌 Features

### ✔ Real-time Edge Metrics  
- CPU Usage  
- RAM Usage  
- Disk Usage  
- Temperature  
- Heartbeat(timestamp)

Prometheus 형식으로 `/metrics` 제공

---

### ✔ Offline Mode (Queue)  
Cloud로 업로드 실패 시:

logs/offline_queue.json

yaml
코드 복사

에 자동 저장 →  
이후 Cloud 응답 성공 시 **자동 flush 후 업로드**

---

### ✔ Full Logging System  
로그는 아래 구조로 기록됩니다:

/logs
├── edge.log (info 로그)
├── error.log (에러 로그)
└── offline_queue.json (오프라인 큐)

yaml
코드 복사

---

### ✔ Systemd 서비스 자동화  
- 부팅 시 자동 실행  
- crash 시 자동 재시작  
- stdout/stderr 로깅

---

## 📁 Project Structure

edge-exporter/
├── app.py
├── utils/
│ ├── logger.py
│ └── offline_queue.py
├── logs/
│ ├── edge.log
│ ├── error.log
│ └── offline_queue.json
└── requirements.txt

yaml
코드 복사

---

# 🚀 Installation Guide

### 1) 의존성 설치

```bash
sudo apt update
sudo apt install python3-pip -y
pip3 install -r requirements.txt
🎯 Run Manually (테스트용)
bash
코드 복사
python3 app.py
🔥 Systemd 등록 (자동 실행)
1) 서비스 파일 생성
bash
코드 복사
sudo nano /etc/systemd/system/edge-exporter.service
내용 붙여넣기:

ini
코드 복사
[Unit]
Description=Edge Metrics Exporter
After=network.target

[Service]
ExecStart=/usr/bin/python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
WorkingDirectory=/home/orangepi/edge-exporter
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
2) systemd 적용
bash
코드 복사
sudo systemctl daemon-reload
sudo systemctl enable edge-exporter
sudo systemctl start edge-exporter
3) 상태 확인
bash
코드 복사
systemctl status edge-exporter
🌐 Cloud Integration
Edge는 다음 주소로 JSON 로그를 업로드합니다:

perl
코드 복사
POST http://<CLOUD-ENDPOINT>/log
Cloud 팀이 준비해야 하는 API:

json
코드 복사
{
  "edge_cpu_usage": 12.3,
  "edge_ram_usage": 45.0,
  "edge_disk_usage": 26.2,
  "edge_temperature": 41.5,
  "edge_heartbeat_total": 1764464110
}
Cloud에서 200 OK 반환하면 queue flush 실행됩니다.
