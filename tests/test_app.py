

from datetime import datetime
from http import HTTPStatus

from app.schemas.contract_schema import ContractResponse



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
    
def test_read_contracts(client):
    response = client.get('/api/v1/contracts/')
    
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'contracts': []}
    
def test_read_contracts_with_data(client, contract):
    #Transormando o Contrato do banco de dados em um schema para validação
    contract_schema = ContractResponse.model_validate(contract).model_dump(mode="json")
    
    response = client.get('/api/v1/contracts/')
    
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'contracts': [contract_schema]}

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
    assert get_response.json() == {'contracts': []}

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
