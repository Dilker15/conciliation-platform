from services.apply_reconciliation_service import ApplyReconciliationService
from services.s3_service import S3Service
from repositories.reconciliation_repository import ReconciliationResultRepository
import json



service = ApplyReconciliationService(S3Service(),repository=ReconciliationResultRepository())



def lambda_handler(event, context):
    queries_id = event["query_executions"]
    file_id = event["file_id"]
    service.apply_reconciliation(queries_execution=queries_id,file_id=file_id)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            "queries":queries_id
        })
    }
