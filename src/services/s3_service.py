import os
import boto3


class S3Service:

    def __init__(self) -> None:
        self._client = boto3.client("s3")

    def download(self,bucket_name: str,route_key: str,name: str) -> str:

        os.makedirs(route_key, exist_ok=True)
        local_path = os.path.join(route_key, name)

        self._client.download_file(Bucket=bucket_name,Key=f"athena-results/{name}",Filename=local_path)
        return local_path