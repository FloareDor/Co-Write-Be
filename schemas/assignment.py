from pydantic import BaseModel, Field, validator, ValidationError
from typing import Optional, List, Union
from datetime import datetime
from bson import ObjectId

class assignmentSchema(BaseModel):
    _id: Optional[str] = None
    professor_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    ai_limitation: Optional[str] = None
    # code: Optional[str] = None
    resource: Optional[Union[str, bytes]] = None
    active: Optional[bool] = True

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

    @validator('title')
    def title_must_not_be_empty(cls, title):
        if not title or len(title.strip()) == 0:
            raise ValueError('Title cannot be empty')
        return title

    @validator('description')
    def description_must_not_be_empty(cls, description):
        if not description or len(description.strip()) == 0:
            raise ValueError('Description cannot be empty')
        return description
    
