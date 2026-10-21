from services.apply_reconciliation_service import ApplyReconciliationService
from services.s3_service import S3Service
from repositories.reconciliation_repository import ReconciliationResultRepository
from shared_layer.services.observability import get_logger                       
import json

logger = get_logger()                                                            

service = ApplyReconciliationService(S3Service(),repository=ReconciliationResultRepository())


@logger.inject_lambda_context(log_event=False, clear_state=True)                 
def lambda_handler(event, context):
    queries_id = event["query_executions"]
    file_id = event["file_id"]
    logger.append_keys(file_id=file_id)                                          

    try:                                                                         
        result = service.apply_reconciliation(queries_execution=queries_id,file_id=file_id)  
    except Exception:                                                            
        logger.exception("reconciliation_apply_failed")                          
        raise                                                                    

    return {
        'statusCode': 200,
        'body': json.dumps({
            "queries":queries_id
        }),
        "file_id": file_id,                                                     
        "query_executions": queries_id,                                          
        "results_count": result["counts"],                                       
        "summary": result["summary"],                                            
    }