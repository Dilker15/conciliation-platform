from services.s3_service import S3Service
from services.decompressor_service import Decompressor
from services.csv_reader_service import CSVReader
import time
from shared_layer.models.settlement import Settlement
from shared_layer.models.settlement_errors import SettlementError
from services.settlement_parser_service import SettlementParser
from services.settlement_service import SettlementService
from services.settlement_error_service import SettlementErrorService
from services.conciliation_file_service import ConciliationFileService
from services.chunk_service import ChunkService
from shared_layer.services.publish_event import PublishEventService


class Worker:



    def __init__(self,s3_service:S3Service,
                 decompressor:Decompressor,
                 csv_reader:CSVReader,
                 parser:SettlementParser,
                 settlement_serv:SettlementService,
                 settlement_error_serv:SettlementErrorService,
                 chunk_service:ChunkService,
                 event_service:PublishEventService
                 ):
        
        self._s3_service= s3_service
        self._decompressor = decompressor
        self._csv_reader = csv_reader
        self._parse = parser
        self._settlement_service = settlement_serv
        self._settlement_error_service = settlement_error_serv
        self._chunk_service= chunk_service
        self._event_service = event_service



    def process(self, bucket_name: str, key: str, file_id: str):
        start = time.perf_counter()
        id_chunk = key.removesuffix(".csv.gz")


        registered = self._chunk_service.register_chunk(file_id=file_id,chunk_id=id_chunk,bucket_name=bucket_name,bucket_key=key)
        if not registered:
            print("Chunk ya completado o en proceso activo:", key)
            return

        try:
            stream = self._s3_service.read_stream(bucket_name=bucket_name, key=key)
            decompressed_stream = self._decompressor.decompress(stream=stream)

            total_processed = 0
            total_invalid = 0
            batch_parsed: list[Settlement] = []
            batch_errors: list[SettlementError] = []

            for row in self._csv_reader.read(decompressed_stream):
                total_processed += 1
                result = self._parse.parse(row=row, file_id=file_id, row_number=total_processed)

                if isinstance(result, SettlementError):
                    total_invalid += 1
                    batch_errors.append(result)
                else:
                    batch_parsed.append(result)

                if len(batch_parsed) == 25:
                    self._settlement_service.create_settlement_batch(settlements=batch_parsed)
                    batch_parsed.clear()

                if len(batch_errors) == 25:
                    self._settlement_error_service.create_settlement_error_batch(settlements=batch_errors)
                    batch_errors.clear()

            if batch_parsed:
                self._settlement_service.create_settlement_batch(settlements=batch_parsed)
            if batch_errors:
                self._settlement_error_service.create_settlement_error_batch(batch_errors)

            completed = self._chunk_service.complete_chunk_and_update_totals(
                file_id=file_id,
                chunk_id=id_chunk,
                success_amount=total_processed - total_invalid,
                errors_amount=total_invalid,
                total_processed=total_processed,
            )
            if completed:
                file_finalized = self._chunk_service.try_finalize_file(file_id=file_id)
                if file_finalized:
                    print(f"Archivo {file_id} completó todos sus chunks — disparando conciliación")
                    self._event_service.file_parser_completed(file_id=file_id,key_file=id_chunk)
                    print("after call publish event")
                else:
                    print(f"Chunk {id_chunk} completado, archivo {file_id} aún tiene chunks pendientes")

        except Exception as e:
            self._chunk_service.mark_failed(file_id=file_id,chunk_id=id_chunk,error=str(e))
            print(f"Error processing chunk: {key}")
            raise

        elapsed = time.perf_counter() - start
        print(
            f"Processed: {total_processed}, Invalid: {total_invalid}, "
            f"Time: {elapsed:.4f}s Chunk Processed: {key}"
        )

        



        
