from dataclasses import dataclass

@dataclass
class UserDTO:
    user_id: str
    first_name: str | None
    last_name: str | None
    email: str
    password: str | None 