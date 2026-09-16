import boto3
import os


class StartAthenaQueries:

    '''  QUERY_TEMPLATES_RULES = {
        "unmatched_bank_only": """
            SELECT s.transaction_id, s.settlement_id, s.settled_amount
            FROM settlements s
            LEFT JOIN transactions t ON s.transaction_id = t.transaction_id
            WHERE s.file_id = '{file_id}' AND t.transaction_id IS NULL
        """,
        "unmatched_fintech_only": """
            SELECT t.transaction_id, t.amount
            FROM transactions t
            LEFT JOIN settlements s
                ON t.transaction_id = s.transaction_id AND s.file_id = '{file_id}'
            WHERE t.status = 'PENDING' AND s.transaction_id IS NULL
        """,
        "mismatch": """
            SELECT s.transaction_id, s.settled_amount, t.amount AS expected_amount
            FROM settlements s
            INNER JOIN transactions t ON s.transaction_id = t.transaction_id
            WHERE s.file_id = '{file_id}' AND s.settled_amount <> t.amount
        """,
    }   '''
    QUERY_TEMPLATES_RULES = {
         "select_all": """
            SELECT *
            FROM settlements s
            WHERE s.file_id = '{file_id}'
        """,
    }



    def __init__(self):
        self._athena = boto3.client("athena")
        self._database = os.environ["ATHENA_DATABASE"]         
        self._output_location = os.environ["ATHENA_OUTPUT_LOCATION"]  # "s3://conciliation-parquet-files/athena-results/"

    def _sanitize(self, value: str) -> str:
        return value.replace("'", "''")
    


    def handle(self, file_id: str) -> dict:
        safe_file_id = self._sanitize(file_id)
        query_executions = {}

        for query_name, template in self.QUERY_TEMPLATES_RULES.items():
            query_string = template.format(file_id=safe_file_id)

            response = self._athena.start_query_execution(
                QueryString=query_string,
                QueryExecutionContext={"Database": self._database},
                ResultConfiguration={"OutputLocation": self._output_location},
            )
            query_executions[query_name] = response["QueryExecutionId"]
        

        print("QUERY EXECUTIONS : ",query_executions)
        return {"file_id": file_id, "query_executions": query_executions}