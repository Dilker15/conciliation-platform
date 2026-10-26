
from shared_layer.repositories.settlement_repository import SettlementRepository
from shared_layer.models.settlement import Settlement


class SettlementService:


    def __init__(self,repository:SettlementRepository):
        self._repository = repository

    def create_settlement_batch(self,settlements:list[Settlement])->None:
        self._repository.create_settlement_batch(settlements=settlements)
    