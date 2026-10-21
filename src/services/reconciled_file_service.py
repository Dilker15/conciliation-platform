from datetime import datetime, timezone
from repositories.file_reconciliation_repository import (FileReconciliationRepository,TotalsMismatchError)
from shared_layer.services.observability import get_logger

logger = get_logger()


class ReconciledFileService:

    def __init__(self, repository: FileReconciliationRepository):
        self._repository = repository

    def reconcile(self, file_id: str, summary: dict, unmatched_fintech: int) -> dict:
        if not summary:
            raise ValueError("summary ausente: no se puede marcar el archivo como conciliado")

        classified = sum(summary.values())

        try:
            info = self._repository.mark_reconciled(
                file_id=file_id,
                summary=summary,
                unmatched_fintech=unmatched_fintech,
                expected_total=classified,
            )
        except TotalsMismatchError as error:
            logger.error("reconciliation_totals_mismatch", extra={
                "classified": classified,
                "records_successful": error.actual,
                "summary": summary,
            })
            raise

        duration_ms = self._total_duration_ms(info.get("created_at", {}).get("S"))

        logger.info("file_reconciled", extra={
            "matched": summary.get("MATCHED", 0),
            "mismatch": summary.get("MISMATCH", 0),
            "unmatched_bank_only": summary.get("UNMATCHED_BANK_ONLY", 0),
            "declined": summary.get("DECLINED", 0),
            "unmatched_fintech_only": unmatched_fintech,
            "records_classified": classified,
            "duration_total_ms": duration_ms,
        })

        return {
            "reconciliation_status": "RECONCILED",
            "summary": summary,
            "unmatched_fintech_only": unmatched_fintech,
        }

    @staticmethod
    def _total_duration_ms(created_at_iso: str | None) -> int | None:
        if not created_at_iso:
            return None
        created = datetime.fromisoformat(created_at_iso)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return int((datetime.now(timezone.utc) - created).total_seconds() * 1000)