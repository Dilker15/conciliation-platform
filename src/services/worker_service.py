from services.s3_service import S3Service
from services.decompressor_service import Decompressor
from services.csv_reader_service import CSVReader
import time
from models.settlement import Settlement
from models.settlement_errors import SettlementError
from services.settlement_parser_service import SettlementParser
from services.settlement_service import SettlementService
from services.settlement_error_service import SettlementErrorService


class Worker:



    def __init__(self,s3_service:S3Service,decompressor:Decompressor,csv_reader:CSVReader,parser:SettlementParser,settlement_serv:SettlementService,settlement_error_serv:SettlementErrorService):
        self._s3_service= s3_service
        self._decompressor = decompressor
        self._csv_reader = csv_reader
        self._parse = parser
        self._settlement_service = settlement_serv
        self._settlement_error_service = settlement_error_serv


    def process(self,bucket_name:str,key:str,file_id:str):
        start = time.perf_counter()

        stream = self._s3_service.read_stream(bucket_name=bucket_name,key=key)
        decompressed_stream = self._decompressor.decompress(stream=stream)

        total_processed = 0
        total_invalid  = 0
        batch_parsed:list[Settlement] = []
        batch_errors:list[SettlementError] = []

        for row in self._csv_reader.read(decompressed_stream):
            total_processed+=1
            try:
                settlement = self._parse.parse(row=row,file_id=file_id)
                batch_parsed.append(settlement)
            except ValueError as exc:
                total_invalid += 1
                settlement_error = self._parse.parse_erros(row_data=row,file_id=file_id,settlement_id=row.get("settlement_id"),error=str(exc),row_number=total_processed)
                batch_errors.append(settlement_error)
                continue

            if len(batch_parsed) == 25:
                self._settlement_service.create_settlement_batch(settlements=batch_parsed)
                batch_parsed.clear()
            if len(batch_errors) == 25:
                self._settlement_error_service.create_settlement_error_batch(batch_errors)
                batch_errors.clear()


        if batch_parsed:
            self._settlement_service.create_settlement_batch(settlements=batch_parsed)

        if batch_errors:
            self._settlement_error_service.create_settlement_error_batch(batch_errors)

        elapsed = time.perf_counter() - start
        print(
            f"Processed: {total_processed}, "
            f"Invalid: {total_invalid}, "
            f"Time: {elapsed:.4f}s"
            f"Chunk Processed: {key}"
        )
