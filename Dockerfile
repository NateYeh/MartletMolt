FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴 (git, curl)
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# 先複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 不需要 COPY 代碼，因為我們會用 Volumes 掛載實體路徑

EXPOSE 8001

CMD ["python", "-m", "martlet_molt.main"]
