from decimal import Decimal
from datetime import datetime

from shared_layer.models.settlement import Settlement
from shared_layer.models.settlement_errors import SettlementError
from shared_layer.services.observability import get_logger                       

logger = get_logger()                                                            


class SettlementParser:

    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def parse(self,row: dict,file_id: str,row_number: int) -> Settlement | SettlementError:

        errors: list[str] = []
        settlement_id = self._required(row, "settlement_id", errors)

        transaction_id = self._required(row, "transaction_reference", errors)

        provider_name = self._required(row, "provider_name", errors)

        currency = self._required(row, "currency", errors)

        settlement_status = self._required(row, "settlement_status", errors)

        settled_amount = self._parse_amount(row.get("settled_amount"), errors)

        settlement_date = self._parse_date(row.get("settlement_date"), errors)

        if errors:
            logger.debug("row_invalid", extra={"row_number": row_number, "errors": errors})   
            return SettlementError(
                errors=errors,
                file_id=file_id,
                raw_data=row,
                row_number=row_number,
                settlement_id=settlement_id,
            )

        return Settlement(
            file_id=file_id,
            settlement_id=settlement_id,
            transaction_id=transaction_id,
            provider_name=provider_name.upper(),
            settled_amount=settled_amount,
            currency=currency.upper(),
            settlement_status=settlement_status.upper(),
            settlement_date=settlement_date,
        )

   