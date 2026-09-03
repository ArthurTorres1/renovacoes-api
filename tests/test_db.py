from app.models.contract import Contract
from datetime import date

def test_create_contract():
    contract = Contract(customer_name="Customer 1", manager_name="Manager 1", vendor_contract_id="VC001", product_description="Product 1", coverage_end_date=date(2023, 12, 31), quantity=10, total_value=1000.0)
    assert contract.customer_name == "Customer 1"
    assert contract.manager_name == "Manager 1"
    assert contract.vendor_contract_id == "VC001"
    assert contract.product_description == "Product 1"
    assert contract.coverage_end_date == date(2023, 12, 31)
    assert contract.quantity == 10
    assert contract.total_value == 1000.0