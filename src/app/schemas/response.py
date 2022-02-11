from pydantic import BaseModel
from typing import List


class ResponseMsg(BaseModel):
    message: str = "Successfully Requested"


class ErrorBody(BaseModel):
    status: int
    code: str
    message: str


class Errors(BaseModel):
    errors: List[ErrorBody]
