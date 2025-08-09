from dataclasses import dataclass

@dataclass
class UserShopDTO:
    user_id: str
    shop_id: str
    shop_name: str | None 