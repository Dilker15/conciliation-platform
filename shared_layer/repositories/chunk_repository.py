import boto3
from botocore.exceptions import ClientError
from shared_layer.models.chunk import Chunk
from datetime import datetime,timezone
import logging
import os




logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



class ChunkRepository:

    def __init__(self):
        self._client = boto3.client("dynamodb")
        self._table_name = os.environ["CONCILIATION_TABLE_NAME"]

    def register_chunk_conciliation(self,data:Chunk):
        try:
           item = {
                "PK":{
                    "S":f"FILE#{data.file_id}"
                },
                "SK":{
                    "S":f"CHUNK#{data.chunk_id}"
                },
                "bucket_name":{
                    "S":data.bucket_name
                },
                "bucket_key":{
                    "S":data.bucket_key
                },
                "status":{
                    "S":data.status
                },
                "created_at":{
                    "S":data.created_at.isoformat(),
                },
                "fisished_at":{
                    "S":None
                }
           }
           self._client.put_item(
                TableName=self._table_name,
                Item=item,
                ConditionExpression="attribute_not_exists(PK) AND  attribute_not_exists(SK)",
            )
           return True

        except ClientError as error:
            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.warning(
                    "El chunk fue procesado o esta en procesamiento ",
                    data.file_id,
                    data.chunk_id
                )
                return False
            raise


    def mark_completed(self, file_id: str, chunk_id: str) -> None:
        self._client.update_item(
            TableName=self._table_name,
            Key={
                "PK": {"S": f"FILE#{file_id}"},
                "SK": {"S": f"CHUNK#{chunk_id}"}
            },
            UpdateExpression="""
                SET #status = :completed,
                    finished_at = :finished_at
            """,
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":completed": {"S": "COMPLETED"},
                ":processing": {"S": "PROCESSING"},
                ":finished_at": {
                    "S": datetime.now(timezone.utc).isoformat()
                }
            },
            ConditionExpression="#status = :processing"
        )
