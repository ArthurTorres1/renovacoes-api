from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.core.database import get_session
from app.models.contract import Contract
from datetime import date, datetime

from app.schemas.contract_schema import ContractList, ContractResponse, ContractSchema


contracts_router = APIRouter(
    prefix="/api/v1/contracts",
    tags=["contracts"]
)

CONTRACTS_LIST = [Contract(customer_name="Customer 1", manager_name="Manager 1", vendor_contract_id="VC001", product_description="Product 1", coverage_end_date=date(2023, 12, 31), quantity=10, total_value=1000.0),
                 Contract(customer_name="Customer 2", manager_name="Manager 2", vendor_contract_id="VC002", product_description="Product 2", coverage_end_date=date(2023, 12, 31), quantity=20, total_value=2000.0)
                ]

@contracts_router.get("/health",status_code=HTTPStatus.OK, response_model=list[Contract])
async def get_contracts():
    return CONTRACTS_LIST

@contracts_router.get("/", status_code=HTTPStatus.OK, response_model=ContractList)
async def get_contract(
    offset: int = 0,
    limit: int=10,
    session = Depends(get_session)
):
    contracts = session.scalars(select(Contract).offset(offset).limit(limit)).all()
    return {'contracts': contracts}


@contracts_router.post("/", status_code=HTTPStatus.CREATED, response_model=ContractResponse)
async def create_contract(
    contract: ContractSchema,
    session = Depends(get_session)
    ):
    
    #SELECT * FROM contracts WHERE vendor_contract_id = :vendor_contract_id
    existing_contract = session.scalar(
        select(Contract).where(
            Contract.vendor_contract_id == contract.vendor_contract_id
            )
        )
    
    if existing_contract:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Contract with vendor_contract_id already exists."
        ) 
    
    existing_contract = Contract(
        customer_name=contract.customer_name,
        manager_name=contract.manager_name,
        vendor_contract_id=contract.vendor_contract_id,
        product_description=contract.product_description,
        coverage_end_date=contract.coverage_end_date,
        quantity=contract.quantity,
        total_value=contract.total_value
    )
    
    session.add(existing_contract)
    session.commit()
    session.refresh(existing_contract)
    
    return existing_contract