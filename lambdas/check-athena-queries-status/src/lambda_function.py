import json
from services.check_athena_queries_service import CheckAthenaQueryService
from shared_layer.services.observability import get_logger                       # LOG

logger = get_logger()                                                            # LOG

athenaService = CheckAthenaQueryService()


@logger.inject_lambda_context(log_event=False, clear_state=True)                 # LOG
def lambda_handler(event, context):

    file_id = event["file_id"]
    queries_id = event["query_executions"]
    logger.append_keys(file_id=file_id)                                          # LOG

    try:                                                                         # LOG
        result = athenaService.check_queries(queries_id)
    except Exception:                                                            # LOG
        logger.exception("athena_status_check_failed")                           # LOG
        raise                                                                    # LOG

    return {
        "file_id": file_id,
        "query_executions": queries_id,
        **result
    }