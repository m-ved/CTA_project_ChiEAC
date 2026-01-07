FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy the rest of the application (including data files)
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Expose port (Cloud Run will set PORT env var dynamically)
EXPOSE 8050

# Command to run the application using Gunicorn
# Cloud Run sets PORT env var automatically, use it with fallback to 8050
# Using 1 worker and threads for Dash/Plotly
CMD gunicorn --bind 0.0.0.0:${PORT:-8050} --workers 1 --threads 8 --timeout 300 src.visualization.dashboard:server
