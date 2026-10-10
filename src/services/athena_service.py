import boto3
import os
from datetime import datetime, timedelta


class StartAthenaQueries:

    LOOKBACK_DAYS = 7  # suposicion de tiempo : ventana entre que se crea la transacción y el banco la liquida
    QUERY_TEMPLATES_RULES = {
        "unmatched_bank_only": """
            SELECT s.transaction_id,
                   s.settlement_id,
                   s.amount AS settled_amount
            FROM settlements s
            LEFT JOIN transactions t
                ON s.transaction_id = t.transaction_id
                AND ({partition_filter})
            WHERE s.file_id = '{file_id}'
              AND t.transaction_id IS NULL
        """,
        "unmatched_fintech_only": """
            SELECT t.transaction_id,
                   t.amount
            FROM transactions t
            LEFT JOIN settlements s
                ON t.transaction_id = s.transaction_id
            WHERE ({overdue_filter})
              AND t.transaction_status = 'PENDING'
              AND s.transaction_id IS NULL
        """,
        "mismatch": """
            SELECT s.transaction_id,
                    s.amount AS settled_amount,
                    t.amount AS expected_amount,
                    s.currency AS settled_currency,
                    t.currency AS expected_currency,
                    s.provider AS settled_provider,
                    t.payment_provider AS expected_provider,
                    concat_ws(',',
                        IF(ABS(s.amount - t.amount) > 0.005, 'AMOUNT'),
                        IF(s.currency != t.currency, 'CURRENCY'),
                        IF(s.provider != t.payment_provider, 'PROVIDER')
                    ) AS mismatch_reason
                FROM settlements s
                INNER JOIN transactions t
                    ON s.transaction_id = t.transaction_id
                    AND ({partition_filter})
                WHERE s.file_id = '{file_id}'
                AND s.status = 'SETTLED'
                AND (ABS(s.amount - t.amount) > 0.005
                    OR s.provider != t.payment_provider
                    OR s.currency != t.currency)
        """,
    }

    '''QUERY_TEMPLATES_RULES = {      # Example to test Qeries on athena
         "select_all": """
            select *
            from settlements
        """,
    }'''
 


    def __init__(self):
        self._athena = boto3.client("athena")
        self._database = os.environ["ATHENA_DATABASE"]
        self._output_location = os.environ["ATHENA_OUTPUT_LOCATION"]

    def _sanitize(self, value: str) -> str:
        return value.replace("'", "''")

    def _partition_condition(self, day: datetime) -> str:
        return (
            f"(t.year='{day.year}' AND t.month='{day.month:02d}' "
            f"AND t.day='{day.day:02d}')"
        )

    def _build_partition_filter(self, settlement_date: datetime) -> str:
        """Fecha del archivo y los 7 días anteriores"""
        return " OR ".join(
            self._partition_condition(settlement_date - timedelta(days=offset))
            for offset in range(self.LOOKBACK_DAYS + 1)
        )

    def _build_filter(self, settlement_date: datetime) -> str:
        """Solo el día que acaba de salir de la ventana: fecha - 7."""
        return self._partition_condition(
            settlement_date - timedelta(days=self.LOOKBACK_DAYS)
        )

    def handle(self, file_id: str, settlement_date: str) -> dict:
        safe_file_id = self._sanitize(file_id)
        date = datetime.fromisoformat(settlement_date)

        partition_filter = self._build_partition_filter(date)
        overdue_filter = self._build_filter(date)

        query_executions = {}

        for query_name, template in self.QUERY_TEMPLATES_RULES.items():
            query_string = template.format(
                file_id=safe_file_id,
                partition_filter=partition_filter,
                overdue_filter=overdue_filter,
            )

            response = self._athena.start_query_execution(
                QueryString=query_string,
                QueryExecutionContext={"Database": self._database},
                ResultConfiguration={"OutputLocation": self._output_location},
            )
            query_executions[query_name] = response["QueryExecutionId"]

        return {"file_id": file_id, "query_executions": query_executions}