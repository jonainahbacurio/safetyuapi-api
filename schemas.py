from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class EmergencyCreate(BaseModel):
    category: str = Field(min_length=1, max_length=80)
    location: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=1500)


class EmergencyUpdate(BaseModel):
    status: str
    responder: str | None = Field(default=None, max_length=120)


class EmergencyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    reference: str
    category: str
    location: str
    description: str
    status: str
    responder: str | None = None
    createdAt: datetime
    updatedAt: datetime
    queuePosition: int | None = None
