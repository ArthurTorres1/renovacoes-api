

from datetime import datetime
from http import HTTPStatus

from app.schemas.contract_schema import ContractResponse



def test_create_contract(client):
    response = client.post(
        "/api/v1/contracts/",
        json={
            "customer_name": "Tech Solutions Brasil S.A.",
            "manager_name": "Rafael Oliveira",
            "vendor_contract_id": "VC-2026-004",
            "product_description": "Consultoria e suporte tecnico",
            "coverage_end_date": "2027-09-20",
            "quantity": 8,
            "total_value": 12600.00
        }
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "customer_name": "Tech Solutions Brasil S.A.",
        "manager_name": "Rafael Oliveira",
        "vendor_contract_id": "VC-2026-004",
        "product_description": "Consultoria e suporte tecnico",
        "coverage_end_date": "2027-09-20",
        "quantity": 8,
        "total_value": 12600,
        "id_": 1
    }
    
def test_read_contracts(client):
    response = client.get('/api/v1/contracts/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'contracts': []}