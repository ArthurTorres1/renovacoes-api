
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.schemas.contract_schema import ContractSchema


def get_all_contracts_service(
    session: Session,
    start_date: date | None,
    end_date: date | None,
    manager_name: str | None,
    customer_name: str | None,
    page: int,
    limit: int,
) -> dict:
    filters = []

    if start_date:
        filters.append(Contract.coverage_end_date >= start_date)

    if end_date:
        filters.append(Contract.coverage_end_date <= end_date)

    if manager_name:
        filters.append(Contract.manager_name.ilike(f"%{manager_name}%"))

    if customer_name:
        filters.append(Contract.customer_name.ilike(f"%{customer_name}%"))
    
    offset = (page - 1) * limit
    
    total = session.scalar(
        select(func.count()).select_from(Contract).where(*filters)
    )
    
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
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "rows": contracts,
    }

def find_contract_by_id(
    session: Session,
    contract_id: int,
) -> Contract | None:
    
    return session.scalar(select(Contract).where(Contract.id_ == contract_id))

def create_contract_service(
    session: Session,
    contract_data: ContractSchema,
) -> Contract:
      #SELECT * FROM contracts WHERE vendor_contract_id = :vendor_contract_id
    existing_contract = session.scalar(
        select(Contract).where(
            Contract.vendor_contract_id
            == contract_data.vendor_contract_id
        )
    )

    if existing_contract:
        raise ValueError(
            "Contract with vendor_contract_id already exists."
        )

    contract = Contract(
        **contract_data.model_dump()
    )

    session.add(contract)
    try:
        session.commit()
        session.refresh(contract)
    except IntegrityError:
        session.rollback()
        raise ValueError(
            "Contract with vendor_contract_id already exists."
        )

    return contract

def update_contract_service(
    session: Session,
    contract_id: int,
    contract: ContractSchema,
) -> Contract | None:
    
    contract_db = session.scalar(
        select(Contract).where(Contract.id_ == contract_id)
    )

    if contract_db is None:
        return None
    
    contract_db.customer_name = contract.customer_name
    contract_db.manager_name = contract.manager_name
    contract_db.vendor_contract_id = contract.vendor_contract_id
    contract_db.product_description = contract.product_description
    contract_db.coverage_end_date = contract.coverage_end_date
    contract_db.quantity = contract.quantity
    contract_db.total_value = contract.total_value
    
    try:
        
        session.commit()
        session.refresh(contract_db)

        return contract_db
    except IntegrityError:
        session.rollback()
        raise ValueError(
            "Contract with vendor_contract_id already exists."
        )


def delete_contract_service(
    session: Session,
    contract_id: int,
) -> bool:
    contract = session.scalar(
        select(Contract).where(Contract.id_ == contract_id)
    )

    if contract is None:
        return False

    session.delete(contract)
    session.commit()
    return True


def get_renewal_summary_service(
    session: Session,
    end_date: date | None,
    manager_name: str | None,
    customer_name: str | None,
) -> dict[str, int]:
    if end_date is None:
        end_date = date.today() + timedelta(days=90)

    filters = [Contract.coverage_end_date <= end_date]

    if manager_name:
        filters.append(Contract.manager_name.ilike(f"%{manager_name}%"))

    if customer_name:
        filters.append(Contract.customer_name.ilike(f"%{customer_name}%"))

    contracts = session.scalars(
        select(Contract).where(*filters)
    ).all()

    expired = 0
    days_0_30 = 0
    days_31_60 = 0
    days_61_90 = 0
    today = date.today()

    for contract in contracts:
        days_until_expiration = (contract.coverage_end_date - today).days

        if days_until_expiration < 0:
            expired += 1
        elif days_until_expiration <= 30:
            days_0_30 += 1
        elif days_until_expiration <= 60:
            days_31_60 += 1
        elif days_until_expiration <= 90:
            days_61_90 += 1

    return {
        "expired": expired,
        "0_30_days": days_0_30,
        "31_60_days": days_31_60,
        "61_90_days": days_61_90,
        "total": expired + days_0_30 + days_31_60 + days_61_90,
    }
        
    