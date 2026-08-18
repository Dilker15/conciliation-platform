import json
from services.worker_service import Worker
from services.s3_service import S3Service
from services.csv_reader_service import CSVReader
from services.decompressor_service import Decompressor

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