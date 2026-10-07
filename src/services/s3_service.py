import boto3



class S3Service:


    def __init__(self)->None:
        self._client = boto3.client("s3")
  


    def download(self,bucket_name:str,route_key:str,name:str):
        self._client.download_file(
                                    Bucket=bucket_name,
                                    Key=f"athena_results/{name}",
                                    Filename=route_key
                                )


