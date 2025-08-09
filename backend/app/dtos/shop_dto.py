from dataclasses import dataclass
from datetime import datetime

@dataclass
class ShopDTO:
    shop_id: str
    company_id: str
    name: str | None
    address: str | None
    creation_date: datetime | None 