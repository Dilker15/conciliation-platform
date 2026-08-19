import boto3
from models.settlement import Settlement


class SettlementRepository:

    def __init__(self):
        self._client = boto3.client("dynamodb")

    def create_settlement(self, settlement: Settlement):

        self._client.put_item(
            TableName="settlements",
            Item={
                "settlement_id": {
                    "S": settlement.settlement_id
                },
                "transaction_reference": {
                    "S": settlement.transaction_reference
                },
                "file_id": {
                    "S": settlement.file_id
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
        )

        print(
            f"[DYNAMODB] Settlement created: "
            f"{settlement.settlement_id}"
        )