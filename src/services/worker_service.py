from services.s3_service import S3Service
from services.decompressor_service import Decompressor
from services.csv_reader_service import CSVReader


class Worker:



    def __init__(self,s3_service:S3Service,decompressor:Decompressor,csv_reader:CSVReader):
        self._s3_service= s3_service
        self._decompressor = decompressor
        self._csv_reader = csv_reader


    def process(self,bucket_name:str,key:str):
        stream = self._s3_service.read_stream(bucket_name=bucket_name,key=key)
        decompressed_stream = self._decompressor.decompress(stream=stream)
        i=0
        for row in self._csv_reader.read(decompressed_stream):
            print("ROW DECOMMPRESSED IN CHUNK : ",row)
            i+=1

        print("RECORDS IN CHUNK PROCESSED DECOMPRESSED : ",i)
