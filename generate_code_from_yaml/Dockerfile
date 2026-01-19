FROM python:3.11-slim

RUN apt-get update && apt-get install -y docker.io

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "python generate_fastapi.py && python migrate_with_cursor_automated.py"]

