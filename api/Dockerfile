FROM python:3.10-slim

# Install Java (Required for PySpark inference)
RUN apt-get update && apt-get install -y default-jre && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the BentoML service code
COPY service.py .

EXPOSE 3000

# Start the BentoML server
CMD ["bentoml", "serve", "service:ThreatDetector", "--host", "0.0.0.0", "--port", "3000"]