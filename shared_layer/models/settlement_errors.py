from dataclasses import dataclass


@dataclass
class SettlementError:
    settlement_id:str
    file_id: str
    row_number: int
    error: str
    raw_data: dict