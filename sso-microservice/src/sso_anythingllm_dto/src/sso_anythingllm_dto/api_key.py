from pydantic import BaseModel, Field


class ApiKeyDto(BaseModel):
    value: str = Field(description="Unique API key value")
