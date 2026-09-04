
from datetime import date

from pydantic import BaseModel, Field


class ContractSchema(BaseModel):
    customer_name: str
    manager_name: str
    vendor_contract_id: str
    product_description: str
    coverage_end_date: date
    quantity: int = Field(gt=0)
    total_value: float = Field(ge=0)