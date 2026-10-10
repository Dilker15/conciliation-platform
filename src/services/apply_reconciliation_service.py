import csv
import os
from datetime import datetime, timezone
from services.s3_service import S3Service
from config import ATHENA_RESULTS_BUCKET, TMP_DIRECTORY
from repositories.reconciliation_repository import ReconciliationResultRepository

class ApplyReconciliationService:

    BATCH_SIZE = 25  # máximo de batch_write_item para dynamoDB

    RULES = {
        "mismatch": {"rule": "MISMATCH", "prefix": "TXN", "id_column": "transaction_id"},
        "unmatched_fintech_only": {"rule": "UNMATCHED_FINTECH_ONLY", "prefix": "TXN", "id_column": "transaction_id"},
        "unmatched_bank_only": {"rule": "UNMATCHED_BANK_ONLY", "prefix": "SETTLEMENT", "id_column": "settlement_id"},
    }

    NUMERIC_COLUMNS = {"settled_amount", "amount", "expected_amount"}

    def __init__(self, s3_serv: S3Service, repository: ReconciliationResultRepository):
        self._s3_service = s3_serv
        self._repository = repository
        

    def apply_reconciliation(self, queries_execution: dict, file_id: str) -> dict:
        counts = {}

        for query_type, result_id in queries_execution.items():
            rule = self.RULES.get(query_type)
            if rule is None:
                print(f"Regla no exist: {query_type}")
                continue

            route_file = self._s3_service.download(
                bucket_name=ATHENA_RESULTS_BUCKET,
                route_key=TMP_DIRECTORY,
                name=f"{result_id}.csv",
            )

            try:
                counts[query_type] = self._process_csv(route_file, file_id, rule)
            finally:
                os.remove(route_file)

        return counts

    def _process_csv(self, route_file: str, file_id: str, rule: dict) -> int:
        total = 0
        batch: dict[str, dict] = {}  # indexado por SK para evitar duplicados

        with open(route_file, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                item = self._build_item(file_id, rule, row)
                batch[item["SK"]["S"]] = item

                if len(batch) == self.BATCH_SIZE:
                    self._repository.batch_put(list(batch.values()))
                    total += len(batch)
                    batch.clear()

        if batch:
            self._repository.batch_put(list(batch.values()))
            total += len(batch)

        return total



    def _build_item(self, file_id: str, rule: dict, row: dict) -> dict:
        entity_id = row[rule["id_column"]]

        item = {
            "PK": {"S": f"FILE#{file_id}"},
            "SK": {"S": f"RECONCILIATION#{rule['rule']}#{rule['prefix']}#{entity_id}"},
            "rule": {"S": rule["rule"]},
            "reconciled_at": {"S": datetime.now(timezone.utc).isoformat()},
        }

        for column, value in row.items():
            if value is None or value == "":
                continue
            if column in self.NUMERIC_COLUMNS:
                item[column] = {"N": value}
            else:
                item[column] = {"S": value}

        return item