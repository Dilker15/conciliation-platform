
from shared_layer.repositories.settlement_errors_repository import SettlementErrorRespository
from shared_layer.models.settlement_errors import SettlementError


class SettlementErrorService:


    def __init__(self,repository:SettlementErrorRespository):
        self._repository = repository

    def create_settlement_error_batch(self,settlements:list[SettlementError])->None:
        self._repository.create_settlement_error_batch(settlement_errors=settlements)