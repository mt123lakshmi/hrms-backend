from pydantic import BaseModel


class DocumentTypeCreate(BaseModel):
    name: str