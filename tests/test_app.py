

from datetime import date, datetime, timedelta
from http import HTTPStatus

from app.models.contract import Contract
from app.schemas.contract_schema import ContractResponse



def test_health_check(client):
    response = client.get(
        "/health",
    )
    
    assert response.status_code == HTTPStatus.OK
    
    assert response.json() == {'status': 'ok'}

def test_create_contract(client):
    payload = {
        "customer_name": "Tech Solutions Brasil S.A.",
        "manager_name": "Rafael Oliveira",
        "vendor_contract_id": "VC-2026-004",
        "product_description": "Consultoria e suporte tecnico",
        "coverage_end_date": "2027-09-20",
        "quantity": 8,
        "total_value": 12600.00,
    }
    
    response = client.post(
        "/api/v1/contracts/",
        json=payload
    )
    
    assert response.status_code == HTTPStatus.CREATED
    
    response_data = response.json()
    
    # Valida se a resposta está de acordo com o schema
    ContractResponse.model_validate(response_data)  
    
    expected = {
        **payload,
        "id_": response_data["id_"],
        "created_at": response_data["created_at"],
        "updated_at": response_data["updated_at"]
    }
    
    assert response_data == expected
    
    response_2 = client.post(
        "/api/v1/contracts/",
        json=payload
    )
    
    assert response_2.status_code == HTTPStatus.CONFLICT

def test_invalid_contract_values(client):
    response = client.post(
        "/api/v1/contracts/",
        json={
            "customer_name": "Customer",
            "manager_name": "Manager",
            "vendor_contract_id": "VC-INVALID",
            "product_description": "Product",
            "coverage_end_date": "2027-09-20",
            "quantity": 0,
            "total_value": -10,
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    
def test_read_contracts(client):
    response = client.get('/api/v1/contracts/')
    
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'total': 0,
        'page': 1,
        'limit': 25,
        'rows': []
    }
    
def test_read_contracts_with_data(client, contract):
    #Transormando o Contrato do banco de dados em um schema para validação
    contract_schema = ContractResponse.model_validate(contract).model_dump(mode="json")
    
    response = client.get('/api/v1/contracts')
    
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'total': 1,
        'page': 1,
        'limit': 25,
        'rows': [contract_schema]
    }

def test_read_contract_with_filters(client, contract):
    response = client.get(
        "api/v1/contracts/",
        params={
            "customer_name": contract.customer_name[:4],
            "manager_name": contract.manager_name[:4],
            "start_date": date(2024, 1, 1).isoformat(),
            "end_date": date(2026, 12, 31).isoformat(),
        }
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'total': 1,
        'page': 1,
        'limit': 25,
        'rows': [
            {
                "id_": contract.id_,
                "customer_name": contract.customer_name,
                "manager_name": contract.manager_name,
                "vendor_contract_id": contract.vendor_contract_id,
                "product_description": contract.product_description,
                "coverage_end_date": contract.coverage_end_date.isoformat(),
                "quantity": contract.quantity,
                "total_value": float(contract.total_value),
                "created_at": contract.created_at.isoformat(),
                "updated_at": contract.updated_at.isoformat(),
            }
        ]
    }

def test_failed_of_invalid_date_range(client):
    response = client.get(
        "api/v1/contracts/",
        params={
            "start_date": date(2026, 1, 1).isoformat(),
            "end_date": date(2024, 12, 31).isoformat(),
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        "detail": "end_date precisa ser maior ou igual o campo start_date."
    }

def test_read_contract_nonexistent(client, session):
    last_id = session.query(Contract.id_).order_by(Contract.id_.desc()).first()
    nonexistent_id = (last_id[0] if last_id else 0) + 1
    response = client.get(f"/api/v1/contracts/{nonexistent_id}")
    
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_contract(client, contract):
    
    payload = {
        "customer_name": "Updated Customer",
        "manager_name": "Updated Manager",
        "vendor_contract_id": "VC-2026-004",
        "product_description": "Updated Product Description",
        "coverage_end_date": "2027-09-20",
        "quantity": 15,
        "total_value": 15000.00
    }
                
    response = client.put(
        f"/api/v1/contracts/{contract.id_}",
        json=payload
    )
    
    assert response.status_code == HTTPStatus.OK
    
    response_data = response.json()
    
    ContractResponse.model_validate(response_data)
    
    expected = {
        **payload,
        "id_": contract.id_,
        "created_at": response_data["created_at"],
        "updated_at": response_data["updated_at"]
    }
    
    assert response.json() == expected

def test_delete_contract(client, contract):
    response = client.delete(f"/api/v1/contracts/{contract.id_}")
    
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Contract deleted successfully."}
    
    # Bate no endpoint de GET e verifica se o contrato foi realmente removido
    get_response = client.get('/api/v1/contracts/')
    assert get_response.status_code == HTTPStatus.OK
    assert get_response.json() == {
        'total': 0,
        'page': 1,
        'limit': 25,
        'rows': []
    }

def test_update_integrity_error(client, contract):
    # Inserindo um contrato
    client.post(
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
    
    response = client.put(
        f'/api/v1/contracts/{contract.id_}',
        json={
            "customer_name": "Updated Customer",
            "manager_name": "Updated Manager",
            "vendor_contract_id": "VC-2026-004",  # Mesmo vendor_contract_id do contrato inserido acima
            "product_description": "Updated Product Description",
            "coverage_end_date": "2027-09-20",
            "quantity": 15,
            "total_value": 15000.00
        }
    )
    
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": "Contract with vendor_contract_id already exists."}
    
def test_renewal_summary_expired(client, session):
    expired_contract = Contract(
        customer_name="Customer Expired",
        manager_name="Manager",
        vendor_contract_id="EXPIRED-001",
        product_description="Product",
        coverage_end_date=date.today() - timedelta(days=1),
        quantity=1,
        total_value=100,
    )
    
    active_contract = Contract(
        customer_name="Customer Active",
        manager_name="Manager",
        vendor_contract_id="ACTIVE-001",
        product_description="Product",
        coverage_end_date=date.today() + timedelta(days=10),
        quantity=1,
        total_value=100,
    )
    
    session.add_all([expired_contract, active_contract])
    session.commit()
    
    response = client.get(
        "/api/v1/renewals/upcoming/summary"
    )
    
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "expired": 1,
        "0_30_days": 1,
        "31_60_days": 0,
        "61_90_days": 0,
        "total": 2,
    }
    
    
