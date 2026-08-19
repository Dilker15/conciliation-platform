
from repositories.settlement_bank_repository import SettlementRepository
from models.settlement import Settlement


class SettlementService:


    def __init__(self,repository:SettlementRepository):
        self._repository = repository

    def create_settlement_batch(self,settlements:list[Settlement])->None:
        self._repository.create_settlement_batch(settlements=settlements)