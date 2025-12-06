from pydantic import BaseModel, Field
from typing import Optional, Literal

class StockBase(BaseModel):
    nombre_producto: str 
    tipo: Optional[str] = None 
    unidad_medida: Literal['unidad', 'panal', 'docena', 'medio_panal']
    # id_produccion: int = Field(..., gt=0)
    cantidad_disponible: int = Field(..., ge=0)

class StockCreate(StockBase):
    pass

class StockUpdate(BaseModel):
    unidad_medida: Optional[Literal['unidad', 'panal', 'docena', 'medio_panal']] = None
    id_produccion: Optional[int] = Field(default=None, gt=0)
    cantidad_disponible: Optional[int] = Field(default=None, ge=0)

class StockOut(StockBase):
    id_producto: int
