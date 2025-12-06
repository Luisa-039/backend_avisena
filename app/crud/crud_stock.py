from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from typing import Optional
from app.schemas.stock import StockCreate, StockUpdate  # Ajusta si usas también StockUpdate



def get_stock_by_id(db: Session, id_producto: int):
    try:
        query = text("""
            SELECT nombre_producto, tipo, id_producto, unidad_medida, cantidad_disponible
            FROM stock
            WHERE id_producto = :id_producto
        """)
        result = db.execute(query, {"id_producto": id_producto}).mappings().first()
        return result
    except SQLAlchemyError as e:
        raise Exception(f"Error de base de datos al obtener stock por ID: {e}")

def get_all_stock(db: Session, skip: int = 0, limit: int = 100):
    try:
        query = text("""
            SELECT nombre_producto, tipo, id_producto, unidad_medida, cantidad_disponible
            FROM stock
            ORDER BY id_producto ASC
            LIMIT :limit OFFSET :skip
        """)
        result = db.execute(query, {"skip": skip, "limit": limit}).mappings().all()
        return result
    except SQLAlchemyError as e:
        raise Exception(f"Error de base de datos al obtener todos los stocks: {e}")
    
    
# def update_stock_by_id(db: Session, id_producto: int, stock: StockUpdate) -> Optional[bool]:
#     try:
#         stock_data = stock.model_dump(exclude_unset=True)
#         if not stock_data:
#             return False
#         set_clauses = ", ".join([f"{key} = :{key}" for key in stock_data.keys()])
#         sentencia = text(f"""
#             UPDATE stock
#             SET {set_clauses}
#             WHERE id_producto = :id_producto
#         """)
#         stock_data["id_producto"] = id_producto
#         result = db.execute(sentencia, stock_data)
#         db.commit()
#         return result.rowcount > 0
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise Exception(f"Error de base de datos al actualizar stock {id_producto}: {e}")
