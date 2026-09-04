from dataclasses import asdict
from sqlalchemy import select
from app.models.contract import Contract
from datetime import date, datetime

def test_create_contract(session):
    new_contract = Contract(customer_name="Customer 1", manager_name="Manager 1", vendor_contract_id="VC001", product_description="Product 1", coverage_end_date=date(2023, 12, 31), quantity=10, total_value=1000.0)
    
    session.add(new_contract)
    session.commit()
    
    contract = session.scalar(
        select(Contract).where(Contract.customer_name == "Customer 1")
    )
        
    assert asdict(contract) == {
    "id_": contract.id_,
    "customer_name": "Customer 1",
    "manager_name": "Manager 1",
    "vendor_contract_id": "VC001",
    "product_description": "Product 1",
    "coverage_end_date": date(2023, 12, 31),
    "quantity": 10,
    "total_value": 1000.0,
    "created_at": contract.created_at,
    "updated_at": contract.updated_at,
}
    
    