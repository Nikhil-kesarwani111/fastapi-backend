from pydantic import BaseModel

class PDFRequest(BaseModel):
    name: str
    selected: bool = False
    file: str | None = None   # optional for create_pdf (normal create)

class PDFResponse(BaseModel):
    id: int
    name: str
    selected: bool
    file: str | None

    class Config:
        orm_mode = True
