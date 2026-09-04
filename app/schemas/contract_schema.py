
from datetime import date

from pydantic.v1 import BaseModel


class ContractSchema(BaseModel):
    customer_name: str
    manager_name: str
    vendor_contract_id: str
    product_description: str
    coverage_end_date: date
    quantity: int
    total_value: float