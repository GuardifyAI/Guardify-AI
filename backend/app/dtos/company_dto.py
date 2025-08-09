from dataclasses import dataclass

@dataclass
class CompanyDTO:
    company_id: str
    company_name: str | None 