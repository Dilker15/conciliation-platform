import json
from src.services.worker_service import Worker
from src.services.s3_service import S3Service
from src.services.csv_reader_service import CSVReader
from src.services.decompressor_service import Decompressor

worker = Worker(
    csv_reader= CSVReader(),
    decompressor=Decompressor(),
    s3_service=S3Service()
)

def lambda_handler(event, context):
    print("This lambda was executed with a Docker Image")

    for record in event["Records"]:
        body = json.loads(record["body"])
        worker.process(bucket_name=body["bucket"],key=body["key"])