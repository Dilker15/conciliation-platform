from services.s3_service import S3Service
from config import ATHENA_RESULTS_BUCKET,TMP_DIRECTORY

class ApplyReconciliationService:


    def __init__(self,s3_serv:S3Service):
        self._s3_service = s3_serv
        


    def apply_reconciliation(self,queries_execution:dict,file_id:str):

        for query_type,result_id in queries_execution.items():
            route_file = self._s3_service.download(bucket_name=ATHENA_RESULTS_BUCKET,route_key=TMP_DIRECTORY,name=f"{result_id}.csv")
            print("FILE DOWNLOADED TO:", route_file)
