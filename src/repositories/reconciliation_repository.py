import os
import time
import boto3


class ReconciliationResultRepository:

    MAX_RETRIES = 5

    def __init__(self):
        self._client = boto3.client("dynamodb")
        self._table_name = os.environ["CONCILIATION_TABLE_NAME"]

    def batch_put(self, items: list[dict]) -> None:
        request_items = {
            self._table_name: [{"PutRequest": {"Item": item}} for item in items]
        }

        attempt = 0
        while request_items:
            response = self._client.batch_write_item(RequestItems=request_items)
            request_items = response.get("UnprocessedItems") or {}

            if request_items:
                attempt += 1
                if attempt > self.MAX_RETRIES:
                    raise RuntimeError("batch_write_item: quedaron items sin procesar")
                time.sleep(min(0.1 * 2 ** attempt, 2))