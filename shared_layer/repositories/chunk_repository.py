import boto3
from botocore.exceptions import ClientError
from shared_layer.models.chunk import Chunk
from datetime import datetime, timedelta, timezone
import logging
import os


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ChunkRepository:
    LEASE_TTL_SECONDS = 300  # TIMEUOUT DE LA LAMBDA PRA CONSIDERA ABANDONADO EL PROCESS DEL CHUNK

    def __init__(self):
        self._client = boto3.client("dynamodb")
        self._table_name = os.environ["CONCILIATION_TABLE_NAME"]

    def register_chunk_conciliation(self, data: Chunk) -> bool:
        now = datetime.now(timezone.utc)
        stale_before_iso = (now - timedelta(seconds=self.LEASE_TTL_SECONDS)).isoformat()

        try:
            self._client.update_item(
                TableName=self._table_name,
                Key={
                    "PK": {"S": f"FILE#{data.file_id}"},
                    "SK": {"S": f"CHUNK#{data.chunk_id}"},
                },
                UpdateExpression=(
                    "SET #status = :processing, "
                    "bucket_name = :bucket_name, "
                    "bucket_key = :bucket_key, "
                    "updated_at = :now, "
                    "created_at = if_not_exists(created_at, :now) "
                    "ADD attempts :one"
                ),
                ConditionExpression=(
                    "attribute_not_exists(PK) "
                    "OR #status = :failed "
                    "OR (#status = :processing AND updated_at < :stale_before)"
                ),
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":processing": {"S": "PROCESSING"},
                    ":failed": {"S": "FAILED"},
                    ":bucket_name": {"S": data.bucket_name},
                    ":bucket_key": {"S": data.bucket_key},
                    ":now": {"S": data.created_at.isoformat()},
                    ":stale_before": {"S": stale_before_iso},
                    ":one": {"N": "1"},
                },
            )
            return True
        except ClientError as error:
            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.warning(
                    "El chunk ya fue completado o está siendo procesado activamente: file_id=%s chunk_id=%s",
                    data.file_id, data.chunk_id,
                )
                return False
            raise

    def mark_completed(self, file_id: str, chunk_id: str) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        self._client.update_item(
            TableName=self._table_name,
            Key={"PK": {"S": f"FILE#{file_id}"}, "SK": {"S": f"CHUNK#{chunk_id}"}},
            UpdateExpression="SET #status = :completed, finished_at = :finished_at, updated_at = :finished_at",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":completed": {"S": "COMPLETED"},
                ":processing": {"S": "PROCESSING"},
                ":finished_at": {"S": now_iso},
            },
            ConditionExpression="#status = :processing",
        )


    def mark_failed(self, file_id: str, chunk_id: str, error_message: str = "") -> None:
        self._client.update_item(
            TableName=self._table_name,
            Key={"PK": {"S": f"FILE#{file_id}"}, "SK": {"S": f"CHUNK#{chunk_id}"}},
            UpdateExpression="SET #status = :failed, updated_at = :now, last_error = :err",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":failed": {"S": "FAILED"},
                ":now": {"S": datetime.now(timezone.utc).isoformat()},
                ":err": {"S": error_message[:1000]},
            },
        )