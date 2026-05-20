import datetime
import uuid

from pydantic import BaseModel, model_validator, field_serializer
from starlette.datastructures import URL

from core.config import app_settings


class CodeSnippetCRUDSchema(BaseModel):
    title: str
    code: str
    language: str

class CodeSnippetInfoSchema(BaseModel):
    uid: uuid.UUID
    url: URL
    title: str
    code: str
    language: str
    created_at: datetime.datetime

    @model_validator(mode='after')
    def convert_timezone(self):
        if self.created_at and self.created_at.tzinfo is not None:
            self.created_at = self.created_at.astimezone(app_settings.timezone)
        return self

    @field_serializer("url")
    def serialize_url(self, url: URL) -> str:
        return str(url)

    model_config = {"arbitrary_types_allowed": True}