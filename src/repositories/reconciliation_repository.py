import os
import time
import boto3
from shared_layer.services.observability import get_logger                       

logger = get_logger()                                                           


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
                pending = len(request_items.get(self._table_name, []))          
                if attempt > self.MAX_RETRIES:
                    logger.error("batch_put_gave_up", extra={                    
                        "pending": pending,
                        "attempts": attempt - 1,
                    })
                    raise RuntimeError("batch_write_item: quedaron items sin procesar")
                logger.warning("batch_put_retry", extra={                        
                    "attempt": attempt,
                    "pending": pending,
                })
                time.sleep(min(0.1 * 2 ** attempt, 2))