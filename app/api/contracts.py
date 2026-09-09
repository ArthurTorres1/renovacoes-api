
from datetime import date
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import get_session
from app.models.contract import Contract

from app.schemas.contract_schema import ContractList, ContractResponse, ContractSchema


contracts_router = APIRouter(
    prefix="/api/v1/contracts",
    tags=["contracts"]
)

@contracts_router.get("/health",status_code=HTTPStatus.OK, response_model=list[Contract])
async def get_contracts():
    return {'ok'}

@contracts_router.get("/", status_code=HTTPStatus.OK, response_model=ContractList)
async def get_contract(
    start_date: date | None = None,
    end_date: date | None = None,
    manager_name: str | None = None,
    customer_name: str | None = None,
    offset: int = 0,
    limit: int=10,
    session = Depends(get_session)
):
    
    filters = []
    if start_date is not None and end_date is not None:
        if end_date < start_date:
            raise HTTPException (
                status_code= HTTPStatus.UNPROCESSABLE_ENTITY,
                detail=f"O campo end_date deve ser maior ou igual a start_date."
            )
    
    if start_date:
        filters.append(Contract.coverage_end_date >= start_date)
    if end_date:
        filters.append(Contract.coverage_end_date <= end_date)
    if manager_name:
        filters.append(Contract.manager_name.ilike(f"%{manager_name}%"))
    if customer_name:
        filters.append(Contract.customer_name.ilike(f"%{customer_name}%"))
    
    query = (
        select(Contract)
        .where(*filters)
        .order_by(
            Contract.coverage_end_date.asc(),
            Contract.customer_name.asc(),
            Contract.id_.asc()
            )
        .offset(offset)
        .limit(limit)
    )
    
    contracts = session.scalars(query).all()
    return {'contracts': contracts}

@contracts_router.get("/{contract_id}", status_code=HTTPStatus.OK, response_model=ContractResponse)
async def get_contract_by_id(contract_id: int, session = Depends(get_session)):
    
    contract = session.scalar(select(Contract).where(Contract.id_ == contract_id))
    
    if not contract:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Contract not found."
        )
    
    return contract


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

@contracts_router.put("/{contract_id}", status_code=HTTPStatus.OK, response_model=ContractResponse)
async def update_contract(contract_id: int, contract: ContractSchema, session = Depends(get_session)):
    
    contract_db = session.scalar(select(Contract).where(Contract.id_ == contract_id))
    
    if not contract_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Contract not found."
        )
        
    try:
    
        contract_db.customer_name = contract.customer_name
        contract_db.manager_name = contract.manager_name
        contract_db.vendor_contract_id = contract.vendor_contract_id
        contract_db.product_description = contract.product_description
        contract_db.coverage_end_date = contract.coverage_end_date
        contract_db.quantity = contract.quantity
        contract_db.total_value = contract.total_value
        
        session.commit()
        session.refresh(contract_db)

        return contract_db
    
    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Contract with vendor_contract_id already exists."
        )



@contracts_router.delete("/{contract_id}", status_code=HTTPStatus.OK)
async def delete_contract(contract_id: int, session = Depends(get_session)):
    
    contract_db = session.scalar(select(Contract).where(Contract.id_ == contract_id))
    
    if not contract_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Contract not found."
        )
    
    session.delete(contract_db)
    session.commit()
    
    return {"message": "Contract deleted successfully."}