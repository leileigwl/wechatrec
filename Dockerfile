FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create directories
RUN mkdir -p /artlist/html/images /artlist/json /artlist/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 29212

# Command to run the application
CMD ["uvicorn", "fastapiServer:app", "--host", "0.0.0.0", "--port", "8000"] 