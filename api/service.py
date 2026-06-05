import bentoml
import os
import mlflow
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler

@bentoml.service(
    resources={"cpu": "1"},
    traffic={"timeout": 10},
)
class ThreatDetector:
    def __init__(self):
        # 1. Connect to MLflow and MinIO
        os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"
        os.environ["AWS_ACCESS_KEY_ID"] = os.environ.get("MINIO_ROOT_USER", "admin")
        os.environ["AWS_SECRET_ACCESS_KEY"] = os.environ.get("MINIO_ROOT_PASSWORD", "password")
        mlflow.set_tracking_uri("http://mlflow:5000")
        
        # 2. Start a tiny, local Spark session just for inference
        self.spark = SparkSession.builder.appName("BentoInference").master("local[1]").getOrCreate()
        
        # 3. Download the winning model
        run_id = os.environ.get("MLFLOW_RUN_ID")
        print(f"Loading Model from Run: {run_id}...")
        self.model = mlflow.spark.load_model(f"runs:/{run_id}/random_forest_model")

    @bentoml.api
    def predict(self, source_port: int, dest_port: int, bytes: int) -> dict:
        """Accepts a POST request with network log data and returns a threat prediction."""
        # Convert incoming JSON request into a Spark DataFrame
        pdf = pd.DataFrame([{"source_port": source_port, "dest_port": dest_port, "bytes": bytes}])
        df = self.spark.createDataFrame(pdf)
        
        # Assemble the features exactly like we did during training
        assembler = VectorAssembler(inputCols=["source_port", "dest_port", "bytes"], outputCol="features")
        assembled_df = assembler.transform(df)
        
        # Make the prediction
        preds = self.model.transform(assembled_df)
        result = preds.select("prediction").collect()[0][0]
        
        return {"is_attack": int(result)}