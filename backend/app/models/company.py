from app import db

class Company(db.Model):
    __tablename__ = 'company'

    company_id = db.Column(db.String, primary_key=True)
    company_name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Company {self.company_id} | Name {self.company_name}>"