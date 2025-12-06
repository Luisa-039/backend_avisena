from datetime import date
from pydantic import BaseModel, Field
from typing import List, Optional



class RescueBase(BaseModel):
    id_galpon: int
    fecha: date
    id_tipo_gallina: int
    cantidad_gallinas: int

class RescueCreate(RescueBase):
    pass

class RescueUpdate(BaseModel):
    id_galpon: Optional[int] = None
    fecha: Optional[date] = None
    id_tipo_gallina: Optional[int] = None
    cantidad_gallinas: Optional[int] = None

class RescueOut(RescueBase):
    id_salvamento: int
    nombre: str
    raza: str

class RescuePaginatedResponse(BaseModel):
    page: int
    page_size: int
    total_rescues: int
    total_pages: int
    rescues: List[RescueOut]