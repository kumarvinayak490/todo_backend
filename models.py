from pydantic import BaseModel
from typing import Optional

class SignUpSchema(BaseModel):
    email:str
    password:str

    class Config:
        schema_extra = {
            "example":{
                "email":"sample@gmail.com",
                "password":"samplepassword123"
            }
        }


class LoginSchema(BaseModel):
    email:str
    password:str

    class Config:
        schema_extra = {
            "example":{
                "email":"sample@gmail.com",
                "password":"samplepassword123"
            }
        }


class Todo(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    completed: bool = False

class StatusUpdate(BaseModel):
    completed:bool


