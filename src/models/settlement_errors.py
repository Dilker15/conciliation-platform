from dataclasses import dataclass


@dataclass
class SettlementParseError:
    file_id: str
    row_number: int
    error: str
    raw_data: dict