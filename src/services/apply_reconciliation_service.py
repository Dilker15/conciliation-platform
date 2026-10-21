import csv
import os
import time                                                                     
from datetime import datetime, timezone
from services.s3_service import S3Service
from config import ATHENA_RESULTS_BUCKET, TMP_DIRECTORY
from repositories.reconciliation_repository import ReconciliationResultRepository
from shared_layer.services.observability import get_logger                      

logger = get_logger()                                                           

class ApplyReconciliationService:

    BATCH_SIZE = 25  # máximo de batch_write_item para dynamoDB

    SUMMARY_QUERY = "summary"                                                   
    SUMMARY_STATUSES = ("MATCHED", "MISMATCH", "UNMATCHED_BANK_ONLY", "DECLINED") 

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
        start = time.perf_counter()                                             
        counts = {}
        summary = None                                                          
        logger.info("reconciliation_started", extra={"queries": list(queries_execution.keys())})   

        for query_type, result_id in queries_execution.items():
            if query_type == self.SUMMARY_QUERY:                                 
                summary = self._read_summary(result_id)                          
                continue                                                        

            rule = self.RULES.get(query_type)
            if rule is None:
                logger.warning("rule_skipped", extra={                           
                    "query_name": query_type,
                    "reason": "no_rule_defined",
                })
                continue

            route_file = self._s3_service.download(
                bucket_name=ATHENA_RESULTS_BUCKET,
                route_key=TMP_DIRECTORY,
                name=f"{result_id}.csv",
            )
            logger.debug("result_file_downloaded", extra={                       
                "query_name": query_type,
                "query_execution_id": result_id,
                "bytes": os.path.getsize(route_file),
            })

            try:
                counts[query_type] = self._process_csv(route_file, file_id, rule)
            finally:
                os.remove(route_file)

            logger.info("rule_applied", extra={                                 
                "query_name": query_type,
                "rule": rule["rule"],
                "rows": counts[query_type],
            })

        if summary is None:                                                     
            logger.warning("summary_missing", extra={"reason": "no_summary_query_in_execution"})  

        logger.info("reconciliation_applied", extra={                          
            "rows_written_total": sum(counts.values()),
            "rows_by_rule": counts,
            "duration_ms": int((time.perf_counter() - start) * 1000),
        })

        return {"counts": counts, "summary": summary}                           

    def _read_summary(self, result_id: str) -> dict:                            
        route_file = self._s3_service.download(
            bucket_name=ATHENA_RESULTS_BUCKET,
            route_key=TMP_DIRECTORY,
            name=f"{result_id}.csv",
        )
        try:
            with open(route_file, newline="", encoding="utf-8") as f:
                found = {row["status"]: int(row["total"]) for row in csv.DictReader(f)}
        finally:
            os.remove(route_file)

      
        summary = {status: found.get(status, 0) for status in self.SUMMARY_STATUSES}
        logger.info("summary_read", extra={"summary": summary, "query_execution_id": result_id})
        return summary

    def _process_csv(self, route_file: str, file_id: str, rule: dict) -> int:
        total = 0
        batch: dict[str, dict] = {}

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