
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ContractSchema(BaseModel):
    customer_name: str
    manager_name: str
    vendor_contract_id: str
    product_description: str
    coverage_end_date: date
    quantity: int = Field(gt=0)
    total_value: float = Field(ge=0)


class ContractResponse(ContractSchema):
    id_: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
class ContractList(BaseModel):
    contracts: list[ContractResponse]