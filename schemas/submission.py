from pydantic import BaseModel, Field, validator, ValidationError
from typing import Optional, List, Union
from datetime import datetime
from bson import ObjectId

class submissionSchema(BaseModel):
    id: Optional[str] = None
    student_id: Optional[str] = "default_student"
    assignment_id: Optional[str] = None
    submission_text: Optional[str] = None
    submission_file: Optional[Union[str, bytes]] = None
    active: Optional[bool] = True

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

    @validator('student_id')
    def student_id_must_not_be_empty(cls, student_id):
        if not student_id or len(student_id.strip()) == 0:
            raise ValueError('Student ID cannot be empty')
        return student_id

    @validator('assignment_id')
    def assignment_id_must_not_be_empty(cls, assignment_id):
        if not isinstance(assignment_id, str):
            raise ValueError('Invalid assignment ID')
        return assignment_id