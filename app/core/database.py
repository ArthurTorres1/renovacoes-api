

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.settings import Settings


engine = create_engine(Settings().DATABASE_URL)

# Fornece uma sessao por requisicao e garante seu fechamento ao final do uso.
def get_session():
    with Session(engine) as session:
        yield session

