from pydantic import BaseModel, Field


class RenewalSummary(BaseModel):
    expired: int
    days_0_30: int = Field(alias="0_30_days")
    days_31_60: int = Field(alias="31_60_days")
    days_61_90: int = Field(alias="61_90_days")
    total: int