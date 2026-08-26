import boto3
from boto3.dynamodb.types import TypeSerializer

from models.settlement_errors import SettlementError


class SettlementErrorRespository:

    def __init__(self):
        self._client = boto3.client("dynamodb")
        self._serializer = TypeSerializer()

    def create_settlement_error_batch(self,settlement_errors: list[SettlementError]):
        requests = []

        for settlement_error in settlement_errors:
            requests.append({
                "PutRequest": {
                    "Item": {
                        "PK": {
                            "S": f"FILE#{settlement_error.file_id}"
                        },
                        "SK": {
                            "S": f"ERROR#{settlement_error.settlement_id}"
                        },
                        "row_number": {
                            "N": str(settlement_error.row_number)
                        },
                        "error": {
                            "S": settlement_error.error
                        },
                        "raw_data": self._serializer.serialize(
                            settlement_error.raw_data
                        )
                    }
                }
            })

        response = self._client.batch_write_item(
            RequestItems={
                "files_conciliation": requests
            }
        )

