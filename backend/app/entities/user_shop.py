from backend.app import db
from dataclasses import dataclass


@dataclass
class UserShopDTO:
    user_id: str
    shop_id: str
    shop_name: str | None


class UserShop(db.Model):
    __tablename__ = 'user_shop'

    user_id = db.Column(db.Text, db.ForeignKey('user.user_id'), primary_key=True)
    shop_id = db.Column(db.Text, db.ForeignKey('shop.shop_id'), primary_key=True)

    # Relationships
    user = db.relationship('User', back_populates='user_shops', lazy='select')
    shop = db.relationship('Shop', backref='user_shops', lazy='select')

    def __repr__(self):
        return f"<UserShop user_id={self.user_id} shop_id={self.shop_id}>"

    def to_dto(self) -> UserShopDTO:
        return UserShopDTO(
            user_id=self.user_id,
            shop_id=self.shop_id,
            shop_name=self.shop.name if self.shop else None,
        )