
from datetime import date, datetime
from pydantic import BaseModel

class Contract(BaseModel):
    id_: int
    customer_name: str
    manager_name: str
    vendor_contract_id: str
    product_description: str
    coverage_end_date: date
    quantity: int
    total_value: float
    created_at: datetime
    updated_at: datetime