from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from typing import Optional
import logging

from app.schemas.rescue import RescueCreate, RescueUpdate

logger = logging.getLogger(__name__)

def create_rescue(db: Session, rescue: RescueCreate) -> Optional[bool]:
    try:
        query = text("""
            INSERT INTO salvamento (
                id_galpon, fecha, id_tipo_gallina, cantidad_gallinas
            ) VALUES (
                :id_galpon, :fecha, :id_tipo_gallina, :cantidad_gallinas
            )
        """)
        db.execute(query, rescue.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear salvamento: {e}")
        raise Exception("Error de base de datos al crear la salvamento")


def get_rescue_by_id(db: Session, id_salvamento: int):
    try:
        query = text("""SELECT salvamento.id_salvamento, salvamento.id_galpon, salvamento.fecha, salvamento.id_tipo_gallina, 
                        salvamento.cantidad_gallinas,  galpones.nombre, tipo_gallinas.raza
                        FROM salvamento
                        JOIN galpones ON salvamento.id_galpon = galpones.id_galpon
                        JOIN tipo_gallinas ON salvamento.id_tipo_gallina = tipo_gallinas.id_tipo_gallinas
                        WHERE id_salvamento = :salvamento_id
                    """)
        result = db.execute(query, {"salvamento_id": id_salvamento}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener salvamento por id: {e}")
        raise Exception("Error de base de datos al obtener la salvamento")


def get_all_rescues(db: Session):
    try:
        query = text("""SELECT salvamento.id_salvamento, salvamento.id_galpon, salvamento.fecha, 
                        salvamento.id_tipo_gallina, salvamento.cantidad_gallinas,  
                        galpones.nombre as nombre, 
                        tipo_gallinas.raza as raza
                        FROM salvamento
                        JOIN galpones ON salvamento.id_galpon = galpones.id_galpon
                        JOIN tipo_gallinas ON salvamento.id_tipo_gallina = tipo_gallinas.id_tipo_gallinas
                        ORDER BY salvamento.fecha DESC, salvamento.id_salvamento DESC
                    """)
        result = db.execute(query).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener todos los salvamentos: {e}")
        raise Exception("Error de base de datos al obtener los salvamentos")


def update_rescue_by_id(db: Session, id_salvamento: int, rescue:RescueUpdate) -> Optional[bool]:
    try:
        # Solo los campos enviados por el cliente
        rescue_data = rescue.model_dump(exclude_unset=True, exclude_none=True)

        rescue_data = {key: value for key, value in rescue_data.items() if value != 0}
        
        if not rescue_data:
            return False  # nada que actualizar
        
        logger.info(f"Actualizando finca {id_salvamento} con datos: {rescue_data}")

        # Construir dinámicamente la sentencia UPDATE
        set_clauses = ", ".join([f"{key} = :{key}" for key in rescue_data.keys()])
        sentencia = text(f"""
            UPDATE salvamento 
            SET {set_clauses}
            WHERE id_salvamento = :id_salvamento
        """)

        # Agregar el id_usuario
        rescue_data["id_salvamento"] = id_salvamento

        result = db.execute(sentencia, rescue_data)
        db.commit()
        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar salvamento {id_salvamento}: {e}")
        raise Exception("Error de base de datos al actualizar la salvamento")
    
def delete_rescue_by_id(db: Session, id_salvamento: int) -> Optional[bool]:
    try:
        query = text("""
            DELETE FROM salvamento 
            WHERE id_salvamento = :id_salvamento
        """)
        result = db.execute(query, {"id_salvamento": id_salvamento})
        db.commit()
        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar salvamento {id_salvamento}: {e}")
        raise Exception("Error de base de datos al eliminar el salvamento")

def get_all_rescues_pag(db: Session, skip: int = 0, limit: int = 10):
    """
    Obtiene los salvamentos con paginación.
    """
    try:
        # 1. Contar total de salvamentos
        count_query = text("""
            SELECT COUNT(id_salvamento) AS total
            FROM salvamento
        """)
        total_result = db.execute(count_query).scalar()
    
        # 2. Consultar salvamentos paginados - CON NOMBRES REALES DE COLUMNAS
        data_query = text("""
            SELECT salvamento.id_salvamento, salvamento.id_galpon, salvamento.fecha, 
                   salvamento.id_tipo_gallina, salvamento.cantidad_gallinas,
                   galpones.nombre as nombre, 
                   tipo_gallinas.raza as raza
            FROM salvamento
            JOIN galpones ON salvamento.id_galpon = galpones.id_galpon
            JOIN tipo_gallinas ON salvamento.id_tipo_gallina = tipo_gallinas.id_tipo_gallinas
            ORDER BY salvamento.fecha DESC, salvamento.id_salvamento DESC
            LIMIT :limit OFFSET :skip
        """)

        result = db.execute(data_query, {"skip": skip, "limit": limit}).mappings().all()

        # 3. Retornar resultados
        return {
            "total": total_result or 0,
            "rescues": [dict(row) for row in result]
        }
    
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener los salvamentos: {e}", exc_info=True)
        raise Exception(f"Error de base de datos al obtener los salvamentos: {str(e)}")    

def get_rescues_by_date_range_pag(
    db: Session, 
    fecha_inicio: date, 
    fecha_fin: date, 
    skip: int = 0, 
    limit: int = 10
):
    """
    Obtiene los salvamentos con paginación filtrados por rango de fechas.
    """
    try:
        # 1. Contar total de salvamentos en el rango de fechas
        count_query = text("""
            SELECT COUNT(id_salvamento) AS total
            FROM salvamento
            WHERE fecha BETWEEN :fecha_inicio AND :fecha_fin
        """)
        total_result = db.execute(
            count_query, 
            {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
        ).scalar()
    
        # 2. Consultar salvamentos paginados en el rango de fechas
        data_query = text("""
            SELECT salvamento.id_salvamento, salvamento.id_galpon, salvamento.fecha, 
                    salvamento.id_tipo_gallina, salvamento.cantidad_gallinas,
                    galpones.nombre as nombre, 
                    tipo_gallinas.raza as raza
            FROM salvamento
            JOIN galpones ON salvamento.id_galpon = galpones.id_galpon
            JOIN tipo_gallinas ON salvamento.id_tipo_gallina = tipo_gallinas.id_tipo_gallinas
            WHERE salvamento.fecha BETWEEN :fecha_inicio AND :fecha_fin
            ORDER BY salvamento.fecha DESC, salvamento.id_salvamento DESC
            LIMIT :limit OFFSET :skip
        """)

        result = db.execute(
            data_query, 
            {
                "fecha_inicio": fecha_inicio, 
                "fecha_fin": fecha_fin,
                "skip": skip, 
                "limit": limit
            }
        ).mappings().all()

        # 3. Retornar resultados
        return {
            "total": total_result or 0,
            "rescues": [dict(row) for row in result]
        }
    
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener los salvamentos por rango de fechas: {e}", exc_info=True)
        raise Exception(f"Error de base de datos al obtener los salvamentos: {str(e)}")