from pydantic import BaseModel, Field, validator, ValidationError
from typing import Optional, Literal
from datetime import datetime

class userSchema(BaseModel):
    _id: Optional[str] = None
    type: Literal["professor", "student"]

    # google stuff
    sub: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    picture: Optional[str] = None

    @validator('type')
    def type_must_be_valid(cls, type):
        if type not in ["professor", "student"]:
            raise ValueError('Type must be either "professor" or "student"')
        return type