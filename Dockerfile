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
COPY src/ ./src/
COPY data/ ./data/
COPY assets/ ./assets/
COPY .env ./

# Create a simple web API
COPY app.py .

# Create necessary directories
RUN mkdir -p /app/assets

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]