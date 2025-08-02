from app import db

class Shop(db.Model):
    __tablename__ = 'shop'

    shop_id = db.Column(db.String, primary_key=True)
    company_id = db.Column(db.String, db.ForeignKey('company.company_id'))
    name = db.Column(db.String)
    address = db.Column(db.String)
    creation_date = db.Column(db.Date)

    company = db.relationship('Company', backref='shops')
