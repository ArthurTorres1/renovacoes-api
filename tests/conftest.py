import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models.contract import Contract, table_registry
from app.core.settings import Settings


@pytest.fixture
def session():
    engine = create_engine(Settings().DATABASE_URL, echo=True)
    #Cria tabela no banco de dados
    table_registry.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
    
    table_registry.metadata.drop_all(engine)