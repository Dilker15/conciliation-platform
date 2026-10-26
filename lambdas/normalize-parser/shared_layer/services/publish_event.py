import json
import time                                                                      
import boto3
from shared_layer.services.observability import get_logger                       

logger = get_logger()                                                            


class PublishEventService:

    def __init__(self, event_bus: str):
        self._event = boto3.client("events")
        self._event_bus = event_bus


    def file_parser_completed(self, file_id: str,key_file:str) -> None:
        start = time.perf_counter()                                              
        detail = {
            "file_id": file_id,
            "key_file":key_file
        }
        response = self._event.put_events(
            Entries=[
                {
                    "EventBusName": self._event_bus,
                    "Source": "conciliation",
                    "DetailType": "parserCompleted",
                    "Detail": json.dumps(detail)
                }
            ]
        )

        if response.get("FailedEntryCount", 0) > 0:                              
            logger.error("event_publish_rejected", extra={                       
                "event_bus": self._event_bus,
                "detail_type": "parserCompleted",
                "failed_entries": response.get("Entries"),
            })
        else:                                                                    
            logger.info("event_published", extra={                               
                "event_bus": self._event_bus,
                "source": "conciliation",
                "detail_type": "parserCompleted",
                "event_id": response["Entries"][0].get("EventId"),
                "duration_ms": int((time.perf_counter() - start) * 1000),
            })