from sqlalchemy import CheckConstraint,func
from sqlalchemy.orm import Mapped, mapped_column, registry
from datetime import date, datetime


table_registry = registry()

@table_registry.mapped_as_dataclass
class Contract:
    __tablename__ = "contracts"
    
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_contract_quantity_positive"),
        CheckConstraint("total_value >= 0", name="ck_contract_total_value_positive"),
    )

    id_: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    customer_name: Mapped[str]
    manager_name: Mapped[str]
    vendor_contract_id: Mapped[str] = mapped_column(unique=True)
    product_description: Mapped[str]
    coverage_end_date: Mapped[date]
    quantity: Mapped[int]
    total_value: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now(),
                                                  onupdate=func.now())