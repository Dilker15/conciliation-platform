from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Settlement:
    settlement_id: str
    transaction_reference: str
    provider_name: str
    settled_amount: Decimal
    currency: str
    settlement_status: str
    settlement_date: datetime
    file_id: str