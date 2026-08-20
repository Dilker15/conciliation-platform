from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class ConciliationData:
    file_hash: str
    file_key: str
    bucket_name: str
    total_chunks: int
    status: Literal["PROCESSING", "COMPLETED","FAILED","CREATED"]
    created_at: datetime
    completed_at: datetime | None = None