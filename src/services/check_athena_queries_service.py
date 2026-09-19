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

        all_succeeded = all(
            state == "SUCCEEDED"
            for state in queries_status.values()
        )

        return {
            "all_succeeded": all_succeeded,
            "queries": queries_status
        }