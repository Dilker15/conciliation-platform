import json
from services.check_athena_queries_service import CheckAthenaQueryService


athenaService = CheckAthenaQueryService()

def lambda_handler(event, context):

    file_id = event["file_id"]
    queries_id = event["query_executions"]

    result = athenaService.check_queries(queries_id)

    return {
        "file_id": file_id,
        "query_executions": queries_id,
        **result
    }
