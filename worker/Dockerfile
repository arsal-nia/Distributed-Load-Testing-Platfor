FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Run the worker in consumer mode (no CLI args)
CMD ["python", "-m", "app.main"]