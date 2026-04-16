FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for rtree
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libspatialindex-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Default CMD for API server (can be overridden by docker-compose for worker)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
