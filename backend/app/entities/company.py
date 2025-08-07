from backend.db import db
from dataclasses import dataclass

@dataclass
class CompanyDTO:
    company_id: str
    company_name: str | None

class Company(db.Model):
    __tablename__ = 'company'

    company_id = db.Column(db.String, primary_key=True)
    company_name = db.Column(db.String, nullable=True)

    def __repr__(self):
        company_name_str = self.company_name if self.company_name is not None else "N/A"
        return f"<Company {self.company_id} | Name {self.company_name}>"
    
    def to_dto(self) -> CompanyDTO:
        return CompanyDTO(
            company_id=self.company_id,
            company_name=self.company_name,
        )