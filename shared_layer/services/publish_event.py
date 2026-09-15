import json
import boto3


class PublishEventService:

    def __init__(self, event_bus: str):
        self._event = boto3.client("events")
        self._event_bus = event_bus


    def file_parser_completed(self, file_id: str,key_file:str) -> None:
        print("inside publish event start file_id : ",file_id,"key_file : ",key_file)
        detail = {
            "file_id": file_id,
            "date":key_file
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

        print("event publised to eventBridge ")
        print(response)
        print("event publised to eventBridge ")

