from services.athena_service import StartAthenaQueries
from shared_layer.services.observability import get_logger                       

logger = get_logger()                                                           

service_athena = StartAthenaQueries()


@logger.inject_lambda_context(log_event=False, clear_state=True)                
def lambda_handler(event, context):


    file_id = event["file_id"]
    settlement_date = event["settlement_date"]
    logger.append_keys(file_id=file_id)                                         

    result_queries_id = service_athena.handle(file_id=file_id,settlement_date=settlement_date)

    return {
        "file_id": file_id,
        "settlement_date": settlement_date,
        "query_executions": result_queries_id["query_executions"],
    }