from sqlalchemy import text
from typing import List
from app.schemas.users import UserOut
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from core.database import get_db
from app.schemas.chicken_incident import PaginatedChickenIncidents, incidentChickenBase, incidentChickenCreate, incidentChickenEstado, incidentChickenOut, incidentChickenUpdate
from app.crud import chicken_incident as crud_chicken_incident

router = APIRouter()
modulo = 22

@router.post("/crear", status_code=status.HTTP_201_CREATED)
def create_incident(
    incident_ch: incidentChickenCreate, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    
    
    
    result = db.execute(text("SELECT id_galpon FROM galpones WHERE id_galpon = :id"), {"id": incident_ch.galpon_origen}).first()
    
    if incident_ch.galpon_origen <= 0:
        raise HTTPException(status_code=404, detail="El id del galpon debe ser mayor a cero")
    
    if not result:
         raise HTTPException(status_code=404, detail="El id del galpon ingresado no existe")
    try:
     id_rol = user_token.id_rol
     if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
     
     crud_chicken_incident.create_incident(db, incident_ch)
     return {"message": "Incidente gallina creado correctamente"}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-id", response_model=incidentChickenOut)
def get_incident_by_id(
    id: int, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        # El rol de quien usa el endpoint
        id_rol = user_token.id_rol
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        chicken_incident = crud_chicken_incident.get_incident_chicken_by_id(db, id)
        if not chicken_incident:
            raise HTTPException(status_code=404, detail="incidente gallina no encontrado")
        return chicken_incident
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-chicken_incidents", response_model=List[incidentChickenOut])
def get_chicken_incidents(
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.id_rol  

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        incident_chicken = crud_chicken_incident.get_all_chicken_incidents(db)
        if not incident_chicken:
            raise HTTPException(status_code=404, detail="incidentes de gallinas no encontrados")
        return incident_chicken

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/by-id/{chicken_incident_id}")
def update_chicken_incident(
    chicken_incident_id: int,
    chicken_incidente: incidentChickenUpdate,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.id_rol

        # Verificación de permisos
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(
                status_code=401,
                detail="Usuario no autorizado para actualizar incidentes de gallinas"
            )

        # Validar galpón solo si se envió
        if chicken_incidente.galpon_origen is not None:
            if chicken_incidente.galpon_origen <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="El id del galpón debe ser mayor a cero"
                )

            result = db.execute(
                text("SELECT id_galpon FROM galpones WHERE id_galpon = :id"),
                {"id": chicken_incidente.galpon_origen}
            ).first()

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"No se encontró un galpón con id {chicken_incidente.galpon_origen}"
                )

        # Llamar al CRUD para actualizar solo los campos enviados
        success = crud_chicken_incident.update_chicken_incident_by_id(
            db, chicken_incident_id, chicken_incidente
        )

        if not success:
            raise HTTPException(
                status_code=400,
                detail="No se pudo actualizar el incidente de gallina"
            )

        return {"message": "Incidente de gallina actualizado correctamente"}

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en la base de datos: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
        )


@router.get("/rango-fechas", response_model=PaginatedChickenIncidents)
def obtener_incidentes_gallina_por_rango_fechas(
    fecha_inicio: str = Query(..., description="Fecha inicial en formato YYYY-MM-DD"),
    fecha_fin: str = Query(..., description="Fecha final en formato YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    """
    Obtiene los incidentes de gallinas dentro de un rango de fechas y aplica paginación.
    """
    try:
        id_rol = user_token.id_rol
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        incidentes = crud_chicken_incident.get_incidentes_gallina_by_date_range(
            db, fecha_inicio, fecha_fin
        )

        if not incidentes:
            return PaginatedChickenIncidents(
                page=page,
                page_size=page_size,
                total_incidents=0,
                total_pages=0,
                incidents=[]
            )


        total = len(incidentes)
        skip = (page - 1) * page_size
        incidentes_paginados = incidentes[skip : skip + page_size]


        return PaginatedChickenIncidents(
            page=page,
            page_size=page_size,
            total_incidents=total,
            total_pages=(total + page_size - 1) // page_size,
            incidents=incidentes_paginados
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los incidentes de gallinas: {e}"
        )

@router.get("/all_incidentes-gallinas-pag", response_model=PaginatedChickenIncidents)
def get_incidentes_gallinas_pag(
    page: int = Query(1, ge=1, description="Número de página (empieza en 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Cantidad de registros por página"),
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    """
    Obtiene incidentes de gallinas paginados.
    Incluye el total de incidentes y el número total de páginas.
    """
    try:
        id_rol = user_token.id_rol

        # Verificación de permisos
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")


        skip = (page - 1) * page_size

        data = crud_chicken_incident.get_all_chicken_incidents_pag(db, skip=skip, limit=page_size)
        total = data["total"]
        incidents = data["incidents"]

        if not incidents:
            raise HTTPException(status_code=404, detail="No se encontraron incidentes de gallinas")

        return {
            "page": page,
            "page_size": page_size,
            "total_incidents": total,
            "total_pages": (total + page_size - 1) // page_size,
            "incidents": incidents
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener incidentes de gallinas: {e}")


     
@router.put("/cambiar-estado/{user_id}", status_code=status.HTTP_200_OK)
def change_chiken_status(
    chiken_id: int,
    nuevo_estado: bool,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        # Verificar permisos del usuario
        id_rol = user_token.id_rol
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        success = crud_chicken_incident.change_chiken_status(db, chiken_id, nuevo_estado)
        if not success:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {"message": f"Estado del incidente  actualizado a {nuevo_estado}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
