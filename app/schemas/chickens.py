from datetime import date
from pydantic import BaseModel
from typing import List, Optional

class ChickenBase(BaseModel):
    id_galpon: int
    fecha: date
    id_tipo_gallina: int
    cantidad_gallinas: int

class ChickenCreate(ChickenBase):
    pass

class ChickenUpdate(BaseModel):
    id_galpon: Optional[int] = None
    fecha: Optional[date] = None
    id_tipo_gallina: Optional[int] = None
    cantidad_gallinas: Optional[int] = None

class ChickenOut(ChickenBase):
    id_ingreso: int
    raza: str
    nombre_galpon: str

class ChickenPaginated(BaseModel):
    page: int
    page_size: int
    total_record_chickens: int
    total_pages: int
    record_chickens: List[ChickenOut]