from services.reconciled_file_service import ReconciledFileService
from repositories.file_reconciliation_repository import FileReconciliationRepository
from shared_layer.services.observability import get_logger

logger = get_logger()

service = ReconciledFileService(repository=FileReconciliationRepository())


@logger.inject_lambda_context(log_event=False, clear_state=True)
def lambda_handler(event, context):
    file_id = event["file_id"]
    logger.append_keys(file_id=file_id)

    try:
        result = service.reconcile(
            file_id=file_id,
            summary=event["summary"],
            unmatched_fintech=event["results_count"].get("unmatched_fintech_only", 0),
        )
    except Exception:
        logger.exception("file_reconcile_failed")
        raise

    return {"file_id": file_id, **result}