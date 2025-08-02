from app import db

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    password = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<User {self.user_id} | Name {self.first_name} {self.last_name}>"