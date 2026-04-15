from pydantic import BaseModel
from typing import List



class DocumentResponse(BaseModel):
    id: int
    document_type_id: int  
    document_type: str     
    file_path: str         

    class Config:
        from_attributes = True


class UploadDocumentResponse(BaseModel):
    success: bool
    message: str
    data: DocumentResponse 

class DocumentListResponse(BaseModel):
    success: bool
    data: List[DocumentResponse]