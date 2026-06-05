# Start with the exact image you were already using
FROM jupyter/pyspark-notebook:latest

# Install your required Python packages permanently
RUN pip install --no-cache-dir delta-spark python-dotenv mlflow boto3
