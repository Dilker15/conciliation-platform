
import boto3
from models.settlement_errors import SettlementError

class SettlementErrorRespository:


    def __init__(self):
        self._client = boto3.client("dynamodb")


    
    def create_settlement_error(self,settlement_error:SettlementError):
        pass

