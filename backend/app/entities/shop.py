from backend.app import db
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ShopDTO:
    shop_id: str
    company_id: str
    name: str | None
    address: str | None
    creation_date: datetime | None


class Shop(db.Model):
    __tablename__ = 'shop'

    shop_id = db.Column(db.String, primary_key=True)
    company_id = db.Column(db.String, db.ForeignKey('company.company_id'))
    name = db.Column(db.String, nullable=True)
    address = db.Column(db.String, nullable=True)
    creation_date = db.Column(db.Date, nullable=True)

    company = db.relationship('Company', backref='shops')

    def __repr__(self):
        name_str = self.name if self.name is not None else "N/A"
        return f"<Shop {self.shop_id} | Company {self.company_id} | Name {name_str}>"
    
    def to_dto(self) -> ShopDTO:
        return ShopDTO(
            shop_id=self.shop_id,
            company_id=self.company_id,
            name=self.name,
            address=self.address,
            creation_date=self.creation_date,
        )