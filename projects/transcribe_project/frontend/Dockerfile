FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# RUN mkdir -p /app/fonts
# COPY fonts/NotoSansJP-VariableFont_wght.ttf /app/fonts/

EXPOSE 8501

# Streamlit アプリを起動する（ポート番号とバインドアドレスを指定）
CMD ["streamlit", "run", "frontend_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
