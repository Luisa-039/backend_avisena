from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class RegistroSensorBase(BaseModel):
    id_sensor: int
    dato_sensor: float
    fecha_hora: datetime
    u_medida: str = Field(..., min_length=1, max_length=10)

class RegistroSensorCreate(RegistroSensorBase):
    pass

class RegistroSensorOut(RegistroSensorBase):
    id_registro: int
    nombre_sensor: Optional[str] = None  # viene del JOIN

    class Config:
        from_attributes = True

# Nuevo schema para la respuesta paginada
class RegistroSensorPaginado(BaseModel):
    registros: List[RegistroSensorOut]
    total: int
    skip: int
    limit: int
