from decimal import Decimal
from datetime import datetime

from models.settlement import Settlement
from models.settlement_errors import SettlementError


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

    def _required(self,row: dict,field: str,errors: list[str]) -> str | None:

        value = row.get(field)

        if value is None:
            errors.append(f"Missing required field: {field}")
            return None

        value = value.strip()

        if not value:
            errors.append(f"Field cannot be empty: {field}")
            return None

        return value

    def _parse_amount(self,value: str | None,errors: list[str]) -> Decimal | None:

        if value is None:
            errors.append("Missing required field: settled_amount")
            return None

        value = value.strip()

        if not value:
            errors.append("Field cannot be empty: settled_amount")
            return None

        try:
            amount = Decimal(value)
        except Exception:
            errors.append(f"Invalid settled_amount: {value}")
            return None

        if amount < 0:
            errors.append(f"settled_amount cannot be negative: {value}")
            return None

        return amount

    def _parse_date(self,value: str | None,errors: list[str]) -> datetime | None:

        if value is None:
            errors.append("Missing required field: settlement_date")
            return None

        value = value.strip()

        if not value:
            errors.append("Field cannot be empty: settlement_date")
            return None

        try:
            return datetime.strptime(value, self.DATE_FORMAT)
        except ValueError:
            errors.append(f"Invalid settlement_date: {value}")
            return None
         




