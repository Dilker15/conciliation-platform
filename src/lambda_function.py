import json
from services.check_athena_queries_service import CheckAthenaQueryService


athenaService = CheckAthenaQueryService()

def lambda_handler(event, context):
    
    file_id = event["file_id"]
    queries_id = event["query_executions"]
    
    status = athenaService.check_queries(queries_id)
    print("ALL STATUS QUERIES : ",status)


    return {
        'statusCode': 200,
        'body': json.dumps({
            "queries":queries_id,
            "file_id":file_id,
            "status":status
        })
    }
