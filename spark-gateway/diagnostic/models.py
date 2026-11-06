import re
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator

class Intake(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    company: str = Field(min_length=2, max_length=160)
    industry: str = Field(min_length=2, max_length=160)
    company_size: str = Field(default='', max_length=80)
    process: str = Field(min_length=40, max_length=4000)
    goal: str = Field(min_length=10, max_length=1500)
    pitch: str = Field(min_length=80, max_length=5000)
    constraints: str = Field(default='', max_length=2000)
    email: str = Field(default='', max_length=254)
    consent: Literal[True]
    website: str = Field(default='', max_length=0)  # honeypot

    @field_validator('email')
    @classmethod
    def email_valid(cls, value):
        if value and not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,63}", value):
            raise ValueError('Correo no válido')
        return value

class ToolChoice(BaseModel):
    id: str = Field(max_length=40)
    why: str = Field(min_length=15, max_length=1000)
    validation: str = Field(min_length=15, max_length=1000)

class Report(BaseModel):
    summary: str = Field(min_length=30, max_length=2000)
    improved_pitch: str = Field(min_length=40, max_length=2500)
    corrections: list[str] = Field(min_length=1, max_length=8)
    missing_information: list[str] = Field(min_length=1, max_length=8)
    architecture: str = Field(min_length=30, max_length=2500)
    tools: list[ToolChoice] = Field(max_length=5)
    pilot_plan: list[str] = Field(min_length=2, max_length=6)
    metrics: list[str] = Field(min_length=2, max_length=8)
    risks: list[str] = Field(min_length=1, max_length=8)
    @field_validator('corrections','missing_information','pilot_plan','metrics','risks')
    @classmethod
    def bounded_items(cls, values):
        if any(not x.strip() or len(x)>1200 for x in values):
            raise ValueError('Items must contain 1–1200 characters')
        return values
