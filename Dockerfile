FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY handlers.py .
COPY database.py .
COPY templates/ ./templates/
COPY static/ ./static/

# Expose port
EXPOSE 8888

# Set environment variables
ENV TORNADO_AUTORELOAD=false
ENV TORNADO_DEBUG=false
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

# Run the application
CMD ["python", "main.py"]

