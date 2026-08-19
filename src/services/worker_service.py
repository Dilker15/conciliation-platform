from services.s3_service import S3Service
from services.decompressor_service import Decompressor
from services.csv_reader_service import CSVReader
import time
from models.settlement import Settlement
from services.settlement_parser_service import SettlementParser


class Worker:



    def __init__(self,s3_service:S3Service,decompressor:Decompressor,csv_reader:CSVReader,parser:SettlementParser):
        self._s3_service= s3_service
        self._decompressor = decompressor
        self._csv_reader = csv_reader
        self._parse = parser


    def process(self,bucket_name:str,key:str,file_id:str):
        start = time.perf_counter()

        stream = self._s3_service.read_stream(bucket_name=bucket_name,key=key)
        decompressed_stream = self._decompressor.decompress(stream=stream)

        total_processed = 0
        total_invalid  = 0
        batch_parsed:list[Settlement] = []

        for row in self._csv_reader.read(decompressed_stream):
            try:
                settlement = self._parse.parse(row=row,file_id=file_id)
                batch_parsed.append(settlement)
            except ValueError as exc:
                total_invalid += 1
                print(f"[PARSER] Invalid row : {exc}")
                continue

            if len(batch_parsed) == 25:  # maximun batch size to write in DynamoDB 25
                # insertar en dynamo de a 25
                batch_parsed.clear()
            total_processed+=1
            

        elapsed = time.perf_counter() - start
        print(
            f"Processed: {total_processed}, "
            f"Invalid: {total_invalid}, "
            f"Time: {elapsed:.4f}s"
        )
