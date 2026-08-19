
from repositories.settlement_bank_error_repository import SettlementErrorRespository
from models.settlement_errors import SettlementError


class SettlementErrorService:


    def __init__(self,repository:SettlementErrorRespository):
        self._repository = repository

    def create_settlement_error_batch(self,settlements:list[SettlementError])->None:
        self._repository.create_settlement_error_batch(settlements=settlements)