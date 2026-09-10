import pytest
from datetime import date

from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_session
from app.models.contract import Contract, table_registry
from app.core.settings import Settings


@pytest.fixture
def client(session):
    def get_test_session():
        return session
    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_test_session
        yield client
        
    app.dependency_overrides.clear()
    
@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
        )
    #Cria tabela no banco de dados
    table_registry.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
    
    table_registry.metadata.drop_all(engine)
    
@pytest.fixture
def contract(session):
    contract = Contract(
        manager_name="John Doe",
        customer_name="Jane Smith",
        coverage_end_date=date(2024, 12, 31),
        product_description="Sample Product",
        vendor_contract_id="VENDOR123",
        quantity=10,
        total_value=1000.0
    )
    session.add(contract)
    session.commit()
    session.refresh(contract)
    
    return contract