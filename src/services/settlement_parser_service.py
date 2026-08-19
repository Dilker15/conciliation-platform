
from models.settlement import Settlement
from models.settlement_errors import SettlementError
from decimal import Decimal
from datetime import datetime


class SettlementParser:

    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def parse(self, row: dict, file_id: str) -> Settlement:

        return Settlement(
            file_id=file_id,
            settlement_id=self._required(row, "settlement_id"),
            transaction_reference=self._required(row,"transaction_reference"),
            provider_name=self._required(row,"provider_name").upper(),
            settled_amount=self._parse_amount(row["settled_amount"]),
            currency=self._required(row, "currency").upper(),
            settlement_status=self._required(row,"settlement_status").upper(),
            settlement_date=self._parse_date(row["settlement_date"]),
        )
    
    def parse_erros(self,row_data:dict,file_id:str,settlement_id:str,error:str,row_number:int)->SettlementError:
        return SettlementError(
            error=error,
            file_id=file_id,
            raw_data=row_data,
            row_number=row_number,
            settlement_id=settlement_id,
        )
    
    
    def _required(self, row: dict, field: str) -> str:

        value = row.get(field)

        if value is None:
            raise ValueError(f"Missing required field: {field}")
        
        value = value.strip()

        if not value:
            raise ValueError(f"Field cannot be empty: {field}")

        return value
    


    def _parse_amount(self, value: str) -> Decimal:

        value = value.strip()
        try:
            amount = Decimal(value)
        except Exception as exc:
            raise ValueError(f"Invalid settled_amount: {value}") from exc

        if amount < 0:
            raise ValueError(f"settled_amount cannot be negative: {value}")

        return amount
    


    def _parse_date(self, value: str) -> datetime:

        value = value.strip()

        try:
            return datetime.strptime(value,self.DATE_FORMAT)
        except ValueError as exc:
            raise ValueError(f"Invalid settlement_date: {value}") from exc


         




