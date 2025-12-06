from pydantic import BaseModel, Field
from typing import Optional

class CategoryBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)

class CategoryOut(CategoryBase):
    id_categoria: int
    
    class Config:
        from_attributes = True