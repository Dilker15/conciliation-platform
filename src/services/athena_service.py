import boto3
import os
from datetime import datetime, timedelta


class StartAthenaQueries:

    LOOKBACK_DAYS = 7            # windows of 7 days

    '''QUERY_TEMPLATES_RULES = {
        "unmatched_bank_only": """
            SELECT s.transaction_id, s.settlement_id, s.settled_amount
            FROM settlements s
            LEFT JOIN transactions t
                ON s.transaction_id = t.transaction_id
                AND ({partition_filter})
            WHERE s.file_id = '{file_id}' AND t.transaction_id IS NULL
        """,
        "unmatched_fintech_only": """
            SELECT t.transaction_id, t.amount
            FROM transactions t
            LEFT JOIN settlements s
                ON t.transaction_id = s.transaction_id AND s.file_id = '{file_id}'
            WHERE ({partition_filter})
              AND t.status = 'PENDING'
              AND s.transaction_id IS NULL
        """,
        "mismatch": """
            SELECT s.transaction_id, s.settled_amount, t.amount AS expected_amount
            FROM settlements s
            INNER JOIN transactions t
                ON s.transaction_id = t.transaction_id
                AND ({partition_filter})
            WHERE s.file_id = '{file_id}'
              AND (s.settled_amount <> t.amount OR s.provider != t.provider)
        """,
    }'''

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
        self._output_location = os.environ["ATHENA_OUTPUT_LOCATION"]

    def _sanitize(self, value: str) -> str:
        return value.replace("'", "''")


    def _build_partition_filter(self, settlement_date: datetime) -> str:
        conditions = []
        for offset in range(self.LOOKBACK_DAYS + 1):
            day = settlement_date - timedelta(days=offset)
            conditions.append(
                f"(t.year='{day.year}' AND t.month='{day.month:02d}' AND t.day='{day.day:02d}')"
            )
        return " OR ".join(conditions)
    

    def handle(self, file_id: str, settlement_date: str) -> dict:
        safe_file_id = self._sanitize(file_id)
        date = datetime.fromisoformat(settlement_date)
        partition_filter = self._build_partition_filter(date)

        query_executions = {}

        for query_name, template in self.QUERY_TEMPLATES_RULES.items():
            query_string = template.format(
                file_id=safe_file_id,
                partition_filter=partition_filter,
            )

            response = self._athena.start_query_execution(
                QueryString=query_string,
                QueryExecutionContext={"Database": self._database},
                ResultConfiguration={"OutputLocation": self._output_location},
            )
            query_executions[query_name] = response["QueryExecutionId"]

        return {"file_id": file_id, "query_executions": query_executions}
    






