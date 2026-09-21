from services.athena_service import StartAthenaQueries


service_athena = StartAthenaQueries()


def lambda_handler(event, context):


    file_id = event["file_id"]
    settlement_date = event["settlement_date"]

    result_queries_id = service_athena.handle(file_id=file_id)

    print("RESULT:", result_queries_id)

    return {
        "file_id": file_id,
        "settlement_date": settlement_date,
        "query_executions": result_queries_id["query_executions"],
    }