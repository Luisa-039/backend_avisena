from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class ConsumoBase(BaseModel):
    id_alimento: int
    cantidad_alimento: int
    fecha_registro: date
    id_galpon: int
    
class ConsumoCreate(ConsumoBase):
    pass

class ConsumoUpdate(BaseModel):
    id_alimento: Optional[int] = None
    cantidad_alimento: Optional[int] = None
    fecha_registro: Optional[date] = None
    id_galpon: Optional[int] = None

class ConsumoOut(ConsumoBase):
    id_consumo: int
    alimento: str
    galpon: str
    fecha_registro: date

class ConsumoPaginated(BaseModel):
    page: int
    page_size: int
    total_consumos: int
    total_pages: int
    consumos: List[ConsumoOut]
