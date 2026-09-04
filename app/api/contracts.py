from http import HTTPStatus

from fastapi import APIRouter

from app.models.contract import Contract
from datetime import date, datetime

from app.schemas.contract_schema import ContractSchema


contracts_router = APIRouter(
    prefix="/api/v1/contracts",
    tags=["contracts"]
)

CONTRACTS_LIST = [Contract(customer_name="Customer 1", manager_name="Manager 1", vendor_contract_id="VC001", product_description="Product 1", coverage_end_date=date(2023, 12, 31), quantity=10, total_value=1000.0),
                 Contract(customer_name="Customer 2", manager_name="Manager 2", vendor_contract_id="VC002", product_description="Product 2", coverage_end_date=date(2023, 12, 31), quantity=20, total_value=2000.0)
                ]

@contracts_router.get("/",status_code=HTTPStatus.OK, response_model=list[Contract])
async def get_contracts():
    return CONTRACTS_LIST

@contracts_router.get("/{contract_id}", status_code=HTTPStatus.OK, response_model=Contract | None)
async def get_contract(contract_id: int):
    
    for contract in CONTRACTS_LIST:
        if(contract.id_ == contract_id):
            return contract
    
    return {"error": "Contract not found"}, 404


@contracts_router.post("/", status_code=HTTPStatus.CREATED, response_model=Contract)
async def create_contract(contract: ContractSchema):
    return contract