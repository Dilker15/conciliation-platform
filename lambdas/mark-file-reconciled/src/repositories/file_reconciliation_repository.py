import os
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError


class TotalsMismatchError(Exception):
    def __init__(self, expected: int, actual: str | None):
        super().__init__(f"clasificados={expected}, records_successful={actual}")
        self.expected = expected
        self.actual = actual


class FileReconciliationRepository:

    def __init__(self):
        self._client = boto3.client("dynamodb")
        self._table_name = os.environ["CONCILIATION_TABLE_NAME"]

    def mark_reconciled(self, file_id: str, summary: dict, unmatched_fintech: int, expected_total: int) -> dict:
        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            response = self._client.update_item(
                TableName=self._table_name,
                Key={"PK": {"S": f"FILE#{file_id}"}, "SK": {"S": "INFO"}},
                UpdateExpression=(
                    "SET reconciliation_status = :reconciled, "
                    "reconciled_at = if_not_exists(reconciled_at, :now), "
                    "updated_at = :now, "
                    "matched_count = :matched, "
                    "mismatch_count = :mismatch, "
                    "unmatched_bank_count = :bank, "
                    "declined_count = :declined, "
                    "unmatched_fintech_count = :fintech"
                ),
                ConditionExpression="records_successful = :expected_total",
                ExpressionAttributeValues={
                    ":reconciled": {"S": "RECONCILED"},
                    ":now": {"S": now_iso},
                    ":matched": {"N": str(summary.get("MATCHED", 0))},
                    ":mismatch": {"N": str(summary.get("MISMATCH", 0))},
                    ":bank": {"N": str(summary.get("UNMATCHED_BANK_ONLY", 0))},
                    ":declined": {"N": str(summary.get("DECLINED", 0))},
                    ":fintech": {"N": str(unmatched_fintech)},
                    ":expected_total": {"N": str(expected_total)},
                },
                ReturnValues="ALL_NEW",
                ReturnValuesOnConditionCheckFailure="ALL_OLD",
            )
        except ClientError as error:
            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                old = error.response.get("Item", {})
                raise TotalsMismatchError(
                    expected=expected_total,
                    actual=old.get("records_successful", {}).get("N"),
                ) from error
            raise
        return response["Attributes"]