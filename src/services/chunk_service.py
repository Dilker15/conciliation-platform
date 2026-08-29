from datetime import datetime, timezone

from shared_layer.models.chunk import Chunk
from shared_layer.repositories.chunk_repository import ChunkRepository


class ChunkService:

    def __init__(self, repository: ChunkRepository):
        self._chunk_repository = repository

    def register_chunk(self,file_id: str,chunk_id: str,bucket_name: str,bucket_key: str)-> bool:
        chunk_data = Chunk(
            file_id=file_id,
            chunk_id=chunk_id,
            bucket_name=bucket_name,
            bucket_key=bucket_key,
            created_at=datetime.now(timezone.utc),
        )

        return self._chunk_repository.register_chunk_conciliation(data=chunk_data)
    

    def mark_completed(self,file_id:str,chunk_id:str)->None:
        self._chunk_repository.mark_completed(file_id=file_id,chunk_id=chunk_id)


    def mark_failed(self,file_id:str,chunk_id:str,error:str)->None:
        self._chunk_repository.mark_failed(file_id=file_id,chunk_id=chunk_id,error_message=error)


    def complete_chunk_and_update_totals(self,file_id: str,chunk_id: str,success_amount: int,errors_amount: int,total_processed: int) -> bool:
        return self._chunk_repository.complete_chunk_and_update_totals(
            file_id=file_id,
            chunk_id=chunk_id,
            success_amount=success_amount,
            errors_amount=errors_amount,
            total_processed=total_processed,
        )
    
    def try_finalize_file(self, file_id: str) -> bool:
        return self._chunk_repository.try_finalize_file(file_id=file_id)