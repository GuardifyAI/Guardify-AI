from backend.db import db
from backend.app.dtos import UserDTO


class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Text, primary_key=True)
    first_name = db.Column(db.Text, nullable=True)
    last_name = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=True)
    # The lazy='select' parameter loads relationships when accessed, which is more efficient for our use case.
    user_shops = db.relationship('UserShop', back_populates='user', lazy='select')

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
