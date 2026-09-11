
from datetime import date
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError

from app.core.database import get_session
from app.schemas.contract_schema import ContractList, ContractResponse, ContractSchema
from app.schemas.renewal_summary_schema import RenewalSummary
from app.services.contract_service import (
    create_contract_service,
    delete_contract_service,
    find_contract_by_id,
    get_all_contracts_service,
    get_renewal_summary_service,
    update_contract_service,
)


contracts_router = APIRouter(
    prefix="/api/v1",
    tags=["contracts"]
)

@contracts_router.get("/contracts", status_code=HTTPStatus.OK, response_model=ContractList)
async def get_contract(
    start_date: date | None = None,
    end_date: date | None = None,
    manager_name: str | None = None,
    customer_name: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=25, ge=1, le=100),
    session = Depends(get_session)
):
    if start_date is not None and end_date is not None:
        if end_date < start_date:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail="end_date precisa ser maior ou igual o campo start_date.",
            )

    return get_all_contracts_service(
        session=session,
        start_date=start_date,
        end_date=end_date,
        manager_name=manager_name,
        customer_name=customer_name,
        page=page,
        limit=limit,
    )

@contracts_router.get("/contracts/{contract_id}", status_code=HTTPStatus.OK, response_model=ContractResponse)
async def get_contract_by_id(contract_id: int, session = Depends(get_session)):
    
    contract = find_contract_by_id(session, contract_id)
    
    if not contract:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Contract not found."
        )
    
    return contract


@contracts_router.post("/contracts", status_code=HTTPStatus.CREATED, response_model=ContractResponse)
async def create_contract(
    contract: ContractSchema,
    session = Depends(get_session)
    ):
    
    try:
        return create_contract_service(
            session,
            contract
        )
    except (IntegrityError, ValueError) as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(error),
        )

@contracts_router.put("/contracts/{contract_id}", status_code=HTTPStatus.OK, response_model=ContractResponse)
async def update_contract(contract_id: int, contract: ContractSchema, session = Depends(get_session)):
    
    try:
        contract = update_contract_service(
            session,
            contract_id,
            contract,
        )

        if contract is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Contract not found.",
            )

        return contract

    except ValueError as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(error),
        )

@contracts_router.delete("/contracts/{contract_id}", status_code=HTTPStatus.OK)
async def delete_contract(contract_id: int, session = Depends(get_session)):
    deleted = delete_contract_service(session, contract_id)

    if not deleted:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Contract not found.",
        )

    return {"message": "Contract deleted successfully."}

@contracts_router.get("/renewals/upcoming/summary", status_code=HTTPStatus.OK, response_model=RenewalSummary)
async def resume_upcoming(
    end_date: date | None = None,
    manager_name: str | None = None,
    customer_name: str | None = None,
    session = Depends(get_session)
):
    return get_renewal_summary_service(
        session=session,
        end_date=end_date,
        manager_name=manager_name,
        customer_name=customer_name,
    )
    
    
    