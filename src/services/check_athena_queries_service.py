import boto3


class CheckAthenaQueryService:

    def __init__(self):
        self._client = boto3.client("athena")

    def check_queries(self, id_queries: dict) -> dict:

        queries_status = {}

        for name, query_id in id_queries.items():

            response = self._client.get_query_execution(
                QueryExecutionId=query_id
            )

            state = response["QueryExecution"]["Status"]["State"]

            queries_status[name] = state

        if any(
            state in ("FAILED", "CANCELLED")
            for state in queries_status.values()
        ):
            status = "FAILED"

        elif all(
            state == "SUCCEEDED"
            for state in queries_status.values()
        ):
            status = "SUCCEEDED"

        else:
            status = "RUNNING"

        return {
            "status": status,
            "query_status": queries_status
        }