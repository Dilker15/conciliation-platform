import boto3
from shared_layer.models.settlement import Settlement


class SettlementRepository:

    def __init__(self):
        self._client = boto3.client("dynamodb")

    def create_settlement_batch(self, settlements: list[Settlement]):
        requests = []

        for settlement in settlements:
            requests.append({
                "PutRequest": {
                    "Item": {
                        "PK": {
                            "S": f"FILE#{settlement.file_id}"
                        },
                        "SK":{
                            "S":f"SETTLEMENT#{settlement.settlement_id}"
                        },
                        "transaction_id": {
                            "S": settlement.transaction_id
                        },
                        "provider_name": {
                            "S": settlement.provider_name
                        },
                        "settled_amount": {
                            "N": str(settlement.settled_amount)
                        },
                        "currency": {
                            "S": settlement.currency
                        },
                        "settlement_status": {
                            "S": settlement.settlement_status
                        },
                        "settlement_date": {
                            "S": settlement.settlement_date.isoformat()
                        }
                    }
                }
            })

        response = self._client.batch_write_item(
            RequestItems={
                "files_conciliation": requests
            }
        )
