from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class AsyncTaskAck(BaseModel):
    task_id: str
    resource_id: str
    status: str = "queued"
