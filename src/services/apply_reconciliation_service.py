from services.s3_service import S3Service



class ApplyReconciliationService:


    def __init__(self,s3_serv:S3Service):
        self._s3_service = s3_serv


    def apply_reconciliation(self,queries_execution:dict,file_id:str):
        print("APPY RESULT TO FILE_ID : ",file_id)
        print("APPY RESULT FOR THIS QUERIES : ",queries_execution)