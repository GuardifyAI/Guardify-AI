from backend.app import db
from dataclasses import dataclass

@dataclass
class UserDTO:
    user_id: str
    first_name: str | None
    last_name: str | None
    email: str
    password: str | None

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Text, primary_key=True)
    first_name = db.Column(db.Text, nullable=True)
    last_name = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=True)

    def __repr__(self):
        first_name_str = self.first_name if self.first_name is not None else "N/A"
        last_name_str = self.last_name if self.last_name is not None else "N/A"
        return f"<User {self.user_id} | Name {first_name_str} {last_name_str} | Email {self.email}>"
    
    def to_dto(self) -> UserDTO:
        return UserDTO(
            user_id=self.user_id,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            password=self.password,
        )