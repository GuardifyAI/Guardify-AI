from app import db

class Shop(db.Model):
    __tablename__ = 'shop'

    shop_id = db.Column(db.String, primary_key=True)
    company_id = db.Column(db.String, db.ForeignKey('company.company_id'))
    name = db.Column(db.String, nullable=True)
    address = db.Column(db.String, nullable=True)
    creation_date = db.Column(db.Date, nullable=True)

    company = db.relationship('Company', backref='shops')

    def __repr__(self):
        return f"<Shop {self.shop_id} | Company {self.company_id} | Name {self.name}>"