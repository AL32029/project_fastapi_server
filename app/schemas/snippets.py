import uuid
import datetime

from pydantic import BaseModel


class CodeSnippetCreateSchema(BaseModel):
    title: str
    code: str
    language: str

class CodeSnippetInfoSchema(BaseModel):
    uid: uuid.UUID
    title: str
    code: str
    language: str
    created_at: datetime.datetime