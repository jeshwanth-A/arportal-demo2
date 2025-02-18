FROM python:3.9-slim

WORKDIR /app

# Install system dependencies required for some Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use environment variable for port (Cloud Run provides $PORT)
ENV PORT=8080
EXPOSE $PORT

# Use exec form for better signal handling
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}"]