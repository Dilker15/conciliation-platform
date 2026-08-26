from shared_layer.repositories.conciliation_repository import RepositoryConciliation



class ConciliationFileService:


    def __init__(self,conciliation_file:RepositoryConciliation):
        self._conciliation_file_repository = conciliation_file



    def updated_processed_records(self,file_hash:str,errors:int,success:int,total_proccessed:int)->None:
        self._conciliation_file_repository.update_processed_records(file_hash=file_hash,success_amount=success,errors_amount=errors,total_processed=total_proccessed)