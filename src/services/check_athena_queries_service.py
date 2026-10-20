import boto3
from shared_layer.services.observability import get_logger                       # LOG

logger = get_logger()                                                            # LOG


class CheckAthenaQueryService:

    def __init__(self):
        self._client = boto3.client("athena")

    def check_queries(self, id_queries: dict) -> dict:

        queries_status = {}
        executions = {}                                                          # LOG

        for name, query_id in id_queries.items():

            response = self._client.get_query_execution(
                QueryExecutionId=query_id
            )

            state = response["QueryExecution"]["Status"]["State"]

            queries_status[name] = state
            executions[name] = response["QueryExecution"]                        
            logger.debug("athena_query_state", extra={                           
                "query_name": name,
                "query_execution_id": query_id,
                "state": state,
            })

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

        logger.info("athena_status_checked", extra={                            
            "status": status,
            "query_status": queries_status,
        })
        if status == "SUCCEEDED":                                                
            self._log_succeeded(executions)                                      
        elif status == "FAILED":                                                 
            self._log_failed(executions)                                        

        return {
            "status": status,
            "query_status": queries_status
        }

    def _log_succeeded(self, executions: dict) -> None:                         
        total_scanned = 0
        slowest_ms = 0
        for name, execution in executions.items():
            stats = execution.get("Statistics", {})
            scanned = stats.get("DataScannedInBytes", 0)
            total_ms = stats.get("TotalExecutionTimeInMillis", 0)
            total_scanned += scanned
            slowest_ms = max(slowest_ms, total_ms)
            logger.info("athena_query_succeeded", extra={
                "query_name": name,
                "query_execution_id": execution["QueryExecutionId"],
                "data_scanned_bytes": scanned,
                "engine_ms": stats.get("EngineExecutionTimeInMillis", 0),
                "total_ms": total_ms,
            })
        logger.info("athena_queries_succeeded", extra={
            "queries": len(executions),
            "data_scanned_bytes_total": total_scanned,
            "slowest_query_ms": slowest_ms,
        })

    def _log_failed(self, executions: dict) -> None:                             
        for name, execution in executions.items():
            state = execution["Status"]["State"]
            if state in ("FAILED", "CANCELLED"):
                logger.error("athena_query_failed", extra={
                    "query_name": name,
                    "query_execution_id": execution["QueryExecutionId"],
                    "state": state,
                    "reason": execution["Status"].get("StateChangeReason"),
                })