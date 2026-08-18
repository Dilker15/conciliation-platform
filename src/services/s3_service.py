import boto3
from botocore.response import StreamingBody


class S3Service:


    def __init__(self):
        self._s3_client = boto3.client('s3')



    def read_stream(self,bucket_name:str,key:str)->StreamingBody:
        response= self._s3_client.get_object(Bucket=bucket_name,Key=key)
        stream = response["Body"]
        return stream
    


    

