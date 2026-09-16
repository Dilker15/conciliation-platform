from services.athena_service import StartAthenaQueries


service_athena = StartAthenaQueries()


def lambda_handler(event, context):

    print("EVENT:", event)

    file_id = event["result"]
    settlement_date = event["settlement_date"]

    print(f"Starting Athena queries for {file_id}")
    print(f"Starting Athena with Date: {settlement_date}")

    result_queries_id = service_athena.handle(
        file_id=file_id
    )

    print("RESULT:", result_queries_id)

    return {
        "file_id": file_id,
        "settlement_date": settlement_date,
        "query_executions": result_queries_id["query_executions"],
        "status": "QUERIES_STARTED"
    }