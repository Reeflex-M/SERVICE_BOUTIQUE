FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN mkdir -p data

EXPOSE 8003

ENV MQTT_BROKER=localhost
ENV MQTT_PORT=1883

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]