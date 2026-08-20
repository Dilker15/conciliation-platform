import json
from services.worker_service import Worker
from services.s3_service import S3Service
from services.csv_reader_service import CSVReader
from services.decompressor_service import Decompressor
from services.settlement_parser_service import SettlementParser
from services.settlement_service import SettlementService
from repositories.settlement_bank_repository import SettlementRepository
from services.settlement_error_service import SettlementErrorService
from services.chunk_counter_service import ChunkCounterService
from repositories.settlement_bank_error_repository import SettlementErrorRespository
from shared_layer.repositories.chunk_counter_repository import (ChunkCounterRepository)

worker = Worker(
    csv_reader= CSVReader(),
    decompressor=Decompressor(),
    s3_service=S3Service(),
    parser= SettlementParser(),
    settlement_serv=SettlementService(SettlementRepository()),
    settlement_error_serv=SettlementErrorService(SettlementErrorRespository()),
    chunk_counter_serv=ChunkCounterService(chunk_counter_repository=ChunkCounterRepository())
)

def lambda_handler(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        bucket_key = body["key"]
        bucket_name=body["bucket"]
        hash_file = body["file_id"]
        chunk_index=body["chunk_index"]
        worker.process(bucket_name=bucket_name,key=bucket_key,file_id=hash_file,chunk_received=chunk_index)