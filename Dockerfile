FROM python:3.10-slim

WORKDIR /app

# 1) 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) 앱 코드 복사
COPY . .

# 3) uvicorn으로 FastAPI 실행 (app.py 안에 app = FastAPI() 라고 되어 있다고 가정)
ENV PORT=8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
