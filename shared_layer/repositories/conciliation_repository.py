import boto3
from botocore.exceptions import ClientError
from datetime import datetime,timezone
from shared_layer.models.conciliation import ConciliationData
import logging
import os



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RepositoryConciliation:

    
    def __init__(self):
        self._db_client = boto3.client("dynamodb")
        self._table_name = os.environ["CONCILIATION_TABLE_NAME"]

    def create_conciliation(self,data: ConciliationData) -> bool:
        try:   
            item = {
                "file_hash": {
                    "S": data.file_hash,
                },
                "file_key": {
                    "S": data.file_key,
                },
                "bucket_name": {
                    "S": data.bucket_name,
                },
                "total_chunks": {
                    "N": str(data.total_chunks),
                },
                "status": {
                    "S": data.status,
                },
                "created_at": {
                    "S": data.created_at.isoformat(),
                },
            }

            if data.completed_at is not None:
                item["completed_at"] = {
                    "S": data.completed_at.isoformat(),
                }
                
            self._db_client.put_item(
                TableName=self._table_name,
                Item=item,
                ConditionExpression="attribute_not_exists(file_hash)",
            )

            return True

        except ClientError as error:

            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False

            raise



    def mark_failed(self, file_hash: str) -> None:
        try:
            self._db_client.update_item(
                TableName=self._table_name,
                Key={
                    "file_hash": {"S": file_hash}
                },
                UpdateExpression="SET #status = :failed, updated_at = :now",
                ConditionExpression="#status = :created",
                ExpressionAttributeNames={
                    "#status": "status"
                },
                ExpressionAttributeValues={
                    ":failed": {"S": "FAILED"},
                    ":created": {"S": "CREATED"},
                    ":now": {"S": datetime.now(timezone.utc).isoformat()}
                }
            )
            logger.info("Conciliation marked as FAILED: %s", file_hash)

        except ClientError as error:
            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.warning(
                    "No se marcó FAILED para %s: el estado ya no era PROCESSING",
                    file_hash
                )
                return
            raise