FROM python:3.9-slim

WORKDIR /app

# FFmpegを含む必要パッケージをインストール
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# gcc と libc-dev をインストール
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install torch==2.5.1 --timeout=600
RUN pip install -U asteroid  
run pip install -U openai-whisper

# 必要なパッケージをインストール
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "backend_app.py"]