from shared_layer.repositories.chunk_counter_repository import (ChunkCounterRepository)




class ChunkCounterService:


    def __init__(self,chunk_counter_repository:ChunkCounterRepository):
        self._chunk_counter_repository = chunk_counter_repository
        


    def register_chunk_processed(self,file_id:str,chunk_received:int)->None:
        self._chunk_counter_repository.register_chunk_processed(file_id=file_id,chunk_index=chunk_received) 
