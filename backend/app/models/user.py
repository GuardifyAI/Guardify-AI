from app import db

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    password = db.Column(db.String)
