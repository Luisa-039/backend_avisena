from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

def get_total_gallinas(db: Session) -> int:
    """Obtiene el total de gallinas en todos los galpones"""
    try:
        query = text("""
            SELECT COALESCE(SUM(cant_actual), 0) as total
            FROM galpones
        """)
        result = db.execute(query).mappings().first()
        return result['total'] if result else 0
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener total de gallinas: {e}")
        return 0

def get_produccion_hoy(db: Session) -> int:
    """Obtiene la producción de huevos de hoy"""
    try:
        hoy = date.today()
        query = text("""
            SELECT COALESCE(SUM(cantidad), 0) as total
            FROM produccion_huevos
            WHERE fecha = :fecha
        """)
        result = db.execute(query, {"fecha": hoy}).mappings().first()
        return result['total'] if result else 0
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener producción de hoy: {e}")
        return 0

def get_galpones_activos(db: Session) -> int:
    """Obtiene el número de galpones activos"""
    try:
        query = text("""
            SELECT COUNT(*) as total
            FROM galpones
            WHERE estado = 1
        """)
        result = db.execute(query).mappings().first()
        return result['total'] if result else 0
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener galpones activos: {e}")
        return 0

def get_alertas_activas(db: Session) -> int:
    """Obtiene el número de incidentes activos"""
    try:
        query = text("""
            SELECT COUNT(*) as total
            FROM incidentes_gallina
            WHERE esta_resuelto = 0
        """)
        result = db.execute(query).mappings().first()
        return result['total'] if result else 0
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener alertas activas: {e}")
        return 0

def get_produccion_semanal(db: Session) -> Dict:
    """Obtiene la producción de los últimos 7 días comparados con la semana anterior"""
    try:
        hoy = date.today()
        inicio_actual = hoy - timedelta(days=6)
        inicio_anterior = hoy - timedelta(days=13)
        fin_anterior = hoy - timedelta(days=7)
        
        # Producción de la semana actual
        query_actual = text("""
            SELECT fecha, COALESCE(SUM(cantidad), 0) as total
            FROM produccion_huevos
            WHERE fecha BETWEEN :inicio AND :fin
            GROUP BY fecha
            ORDER BY fecha
        """)
        
        resultados_actual = db.execute(query_actual, {
            "inicio": inicio_actual,
            "fin": hoy
        }).mappings().all()
        
        # Producción de la semana anterior
        resultados_anterior = db.execute(query_actual, {
            "inicio": inicio_anterior,
            "fin": fin_anterior
        }).mappings().all()
        
        # Crear diccionarios para ambas semanas
        fechas_actual = {}
        fechas_anterior = {}
        dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        
        for i in range(7):
            fecha_actual = inicio_actual + timedelta(days=i)
            fecha_anterior = inicio_anterior + timedelta(days=i)
            fechas_actual[fecha_actual] = 0
            fechas_anterior[fecha_anterior] = 0
        
        # Llenar con datos reales
        for row in resultados_actual:
            fechas_actual[row['fecha']] = int(row['total']) if row['total'] else 0
        
        for row in resultados_anterior:
            fechas_anterior[row['fecha']] = int(row['total']) if row['total'] else 0
        
        # Generar arrays de datos
        labels = []
        data_actual = []
        data_anterior = []
        
        for i in range(7):
            fecha_actual = inicio_actual + timedelta(days=i)
            fecha_anterior = inicio_anterior + timedelta(days=i)
            
            labels.append(dias_semana[fecha_actual.weekday()])
            data_actual.append(fechas_actual[fecha_actual])
            data_anterior.append(fechas_anterior[fecha_anterior])
        
        return {
            "labels": labels,
            "data_actual": data_actual,
            "data_anterior": data_anterior
        }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener producción semanal: {e}")
        return {
            "labels": ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
            "data_actual": [0, 0, 0, 0, 0, 0, 0],
            "data_anterior": [0, 0, 0, 0, 0, 0, 0]
        }

def get_produccion_por_rango(db: Session, dias: int = 7) -> Dict:
    """Obtiene la producción de huevos para un rango de días específico"""
    try:
        hoy = date.today()
        inicio = hoy - timedelta(days=dias - 1)
        
        query = text("""
            SELECT fecha, COALESCE(SUM(cantidad), 0) as total
            FROM produccion_huevos
            WHERE fecha BETWEEN :inicio AND :fin
            GROUP BY fecha
            ORDER BY fecha
        """)
        
        resultados = db.execute(query, {
            "inicio": inicio,
            "fin": hoy
        }).mappings().all()
        
        # Crear diccionario con todas las fechas
        fechas_dict = {}
        for i in range(dias):
            fecha = inicio + timedelta(days=i)
            fechas_dict[fecha] = 0
        
        # Llenar con datos reales
        for row in resultados:
            fechas_dict[row['fecha']] = row['total']
        
        # Generar labels según el rango
        labels = []
        datos = []
        
        for i in range(dias):
            fecha = inicio + timedelta(days=i)
            # Convertir Decimal a int para serialización JSON
            valor = int(fechas_dict[fecha]) if fechas_dict[fecha] else 0
            datos.append(valor)
            
            # Formato de label según rango
            if dias <= 7:
                # Última semana: mostrar día de semana
                dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
                labels.append(dias_semana[fecha.weekday()])
            elif dias <= 31:
                # Último mes: mostrar día del mes
                labels.append(f"{fecha.day}/{fecha.month}")
            else:
                # 3 o 6 meses: mostrar día/mes
                labels.append(f"{fecha.day}/{fecha.month}")
        
        total = sum(datos)
        promedio = round(total / dias, 1) if dias > 0 else 0
        
        return {
            "labels": labels,
            "data": datos,
            "inicio": inicio.isoformat(),
            "fin": hoy.isoformat(),
            "total": total,
            "promedio": promedio
        }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener producción por rango: {e}")
        return {
            "labels": [],
            "data": [],
            "inicio": None,
            "fin": None,
            "total": 0,
            "promedio": 0
        }

def get_distribucion_tipos(db: Session) -> List[Dict]:
    """Obtiene la distribución de gallinas por tipo"""
    try:
        query = text("""
            SELECT 
                tg.raza as tipo,
                COALESCE(SUM(ig.cantidad_gallinas), 0) as cantidad
            FROM tipo_gallinas tg
            LEFT JOIN ingreso_gallinas ig ON tg.id_tipo_gallinas = ig.id_tipo_gallina
            GROUP BY tg.raza
            HAVING SUM(ig.cantidad_gallinas) > 0
            ORDER BY cantidad DESC
        """)
        resultados = db.execute(query).mappings().all()
        
        total = sum(r['cantidad'] for r in resultados)
        
        return [
            {
                "tipo": r['tipo'],
                "cantidad": r['cantidad'],
                "porcentaje": round((r['cantidad'] / total * 100), 2) if total > 0 else 0
            }
            for r in resultados
        ]
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener distribución de tipos: {e}")
        return []

def get_ocupacion_galpones(db: Session) -> List[Dict]:
    """Obtiene la ocupación de cada galpón"""
    try:
        query = text("""
            SELECT 
                nombre,
                capacidad,
                cant_actual as cantidad_actual,
                CASE 
                    WHEN capacidad > 0 THEN ROUND((CAST(cant_actual AS DECIMAL) / capacidad) * 100)
                    ELSE 0 
                END as ocupacion_porcentaje
            FROM galpones
            ORDER BY nombre
            LIMIT 8
        """)
        resultados = db.execute(query).mappings().all()
        
        return [
            {
                "nombre": r['nombre'],
                "capacidad": r['capacidad'],
                "cantidad_actual": r['cantidad_actual'],
                "ocupacion_porcentaje": int(r['ocupacion_porcentaje'])
            }
            for r in resultados
        ]
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener ocupación de galpones: {e}")
        return []

def get_incidentes_recientes(db: Session, limit: int = 5) -> List[Dict]:
    """Obtiene los incidentes más recientes"""
    try:
        query = text("""
            SELECT 
                id_inc_gallina as id,
                tipo_incidente as tipo,
                CASE 
                    WHEN esta_resuelto = 0 THEN 'warning'
                    WHEN esta_resuelto = 1 THEN 'success'
                    ELSE 'danger'
                END as severidad,
                descripcion,
                DATE(fecha_hora) as fecha,
                CASE 
                    WHEN DATE(fecha_hora) = CURRENT_DATE THEN 'Hoy'
                    WHEN DATE(fecha_hora) = CURRENT_DATE - INTERVAL 1 DAY THEN 'Ayer'
                    ELSE CONCAT(DATEDIFF(CURRENT_DATE, DATE(fecha_hora)), ' días')
                END as tiempo
            FROM incidentes_gallina
            ORDER BY fecha_hora DESC
            LIMIT :limit
        """)
        resultados = db.execute(query, {"limit": limit}).mappings().all()
        
        return [dict(r) for r in resultados]
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener incidentes recientes: {e}")
        return []

def get_ultimos_registros_sensores(db: Session) -> Dict:
    """Obtiene los últimos registros de sensores"""
    try:
        query = text("""
            SELECT 
                st.nombre as tipo_sensor,
                rs.dato_sensor as valor,
                rs.fecha_hora
            FROM registro_sensores rs
            JOIN sensores s ON rs.id_sensor = s.id_sensor
            JOIN tipo_sensores st ON s.id_tipo_sensor = st.id_tipo
            WHERE rs.fecha_hora >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
            ORDER BY rs.fecha_hora DESC
            LIMIT 20
        """)
        resultados = db.execute(query).mappings().all()
        
        # Agrupar por tipo de sensor y obtener el último valor
        sensores = {
            "temperatura": 25.0,
            "humedad": 60.0,
            "co2": 450,
            "luminosidad": 750
        }
        
        for r in resultados:
            tipo = r['tipo_sensor'].lower()
            if 'temperatura' in tipo:
                sensores['temperatura'] = float(r['valor'])
            elif 'humedad' in tipo:
                sensores['humedad'] = float(r['valor'])
            elif 'co2' in tipo or 'dioxido' in tipo:
                sensores['co2'] = int(float(r['valor']))
            elif 'luz' in tipo or 'luminosidad' in tipo:
                sensores['luminosidad'] = int(float(r['valor']))
        
        return sensores
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener datos de sensores: {e}")
        return {
            "temperatura": 25.0,
            "humedad": 60.0,
            "co2": 450,
            "luminosidad": 750
        }

def get_actividad_reciente(db: Session, limit: int = 10) -> List[Dict]:
    """Obtiene la actividad reciente del sistema"""
    try:
        # Obtener últimas producciones
        query_produccion = text("""
            SELECT 
                'produccion' as tipo,
                CONCAT('Producción registrada: ', cantidad, ' huevos') as descripcion,
                fecha as fecha_registro,
                'success' as color
            FROM produccion_huevos
            ORDER BY fecha DESC
            LIMIT 2
        """)
        
        # Obtener últimos ingresos de gallinas
        query_gallinas = text("""
            SELECT 
                'gallinas' as tipo,
                CONCAT('Nuevo registro de gallinas en ', g.nombre) as descripcion,
                ig.fecha as fecha_registro,
                'primary' as color
            FROM ingreso_gallinas ig
            JOIN galpones g ON ig.id_galpon = g.id_galpon
            ORDER BY ig.fecha DESC
            LIMIT 2
        """)
        
        # Obtener últimos incidentes
        query_incidentes = text("""
            SELECT 
                'incidente' as tipo,
                CONCAT('Alerta: ', tipo_incidente) as descripcion,
                fecha_hora as fecha_registro,
                'warning' as color
            FROM incidentes_gallina
            ORDER BY fecha_hora DESC
            LIMIT 2
        """)
        
        # Obtener últimas ventas
        query_ventas = text("""
            SELECT 
                'venta' as tipo,
                CONCAT('Venta registrada: ', cantidad, ' unidades') as descripcion,
                fecha as fecha_registro,
                'info' as color
            FROM ventas
            ORDER BY fecha DESC
            LIMIT 2
        """)
        
        # Obtener últimos movimientos de stock
        query_stock = text("""
            SELECT 
                'stock' as tipo,
                CONCAT('Movimiento de stock: ', tipo_movimiento) as descripcion,
                fecha as fecha_registro,
                'secondary' as color
            FROM stock
            ORDER BY fecha DESC
            LIMIT 2
        """)
        
        # Obtener últimas tareas
        query_tareas = text("""
            SELECT 
                'tarea' as tipo,
                CONCAT('Tarea: ', titulo) as descripcion,
                fecha_creacion as fecha_registro,
                'primary' as color
            FROM tareas
            ORDER BY fecha_creacion DESC
            LIMIT 2
        """)
        
        produccion = db.execute(query_produccion).mappings().all()
        gallinas = db.execute(query_gallinas).mappings().all()
        incidentes = db.execute(query_incidentes).mappings().all()
        
        # Intentar obtener ventas, stock y tareas (pueden fallar si las tablas están vacías o tienen problemas)
        try:
            ventas = db.execute(query_ventas).mappings().all()
        except Exception as e:
            logger.warning(f"No se pudieron obtener ventas: {e}")
            ventas = []
        
        try:
            stock = db.execute(query_stock).mappings().all()
        except Exception as e:
            logger.warning(f"No se pudo obtener stock: {e}")
            stock = []
        
        try:
            tareas = db.execute(query_tareas).mappings().all()
        except Exception as e:
            logger.warning(f"No se pudieron obtener tareas: {e}")
            tareas = []
        
        # Combinar y ordenar - convertir RowMapping a dict
        actividades = []
        for act in list(produccion) + list(gallinas) + list(incidentes) + list(ventas) + list(stock) + list(tareas):
            act_dict = dict(act)
            fecha = act_dict['fecha_registro']
            # Convertir date a datetime para poder ordenar
            if isinstance(fecha, date) and not isinstance(fecha, datetime):
                act_dict['fecha_registro'] = datetime.combine(fecha, datetime.min.time())
            actividades.append(act_dict)
        
        actividades.sort(key=lambda x: x['fecha_registro'], reverse=True)
        
        # Calcular tiempo relativo
        ahora = datetime.now()
        resultado = []
        for act in actividades[:limit]:
            fecha = act['fecha_registro']
            if isinstance(fecha, date) and not isinstance(fecha, datetime):
                fecha = datetime.combine(fecha, datetime.min.time())
            
            diff = ahora - fecha
            if diff.days == 0:
                if diff.seconds < 3600:
                    tiempo = f"Hace {diff.seconds // 60} min"
                else:
                    tiempo = f"Hace {diff.seconds // 3600} horas"
            else:
                tiempo = f"Hace {diff.days} días"
            
            resultado.append({
                "tipo": act['tipo'],
                "descripcion": act['descripcion'],
                "tiempo": tiempo,
                "color": act['color']
            })
        
        return resultado
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener actividad reciente: {e}")
        return []

def calcular_tendencias(db: Session) -> Dict:
    """Calcula las tendencias de gallinas y producción"""
    try:
        # Tendencia de gallinas (comparar con mes anterior)
        query_gallinas = text("""
            SELECT 
                SUM(CASE WHEN fecha >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY) THEN cantidad_gallinas ELSE 0 END) as mes_actual,
                SUM(CASE WHEN fecha BETWEEN DATE_SUB(CURRENT_DATE, INTERVAL 60 DAY) AND DATE_SUB(CURRENT_DATE, INTERVAL 31 DAY) THEN cantidad_gallinas ELSE 0 END) as mes_anterior
            FROM ingreso_gallinas
        """)
        result_gallinas = db.execute(query_gallinas).mappings().first()
        
        mes_actual = result_gallinas['mes_actual'] or 0
        mes_anterior = result_gallinas['mes_anterior'] or 1
        
        if mes_anterior > 0:
            trend_gallinas = ((mes_actual - mes_anterior) / mes_anterior) * 100
        else:
            trend_gallinas = 0
        
        # Tendencia de producción (comparar hoy con ayer)
        query_produccion = text("""
            SELECT 
                COALESCE(SUM(CASE WHEN fecha = CURRENT_DATE THEN cantidad ELSE 0 END), 0) as hoy,
                COALESCE(SUM(CASE WHEN fecha = DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY) THEN cantidad ELSE 0 END), 1) as ayer
            FROM produccion_huevos
        """)
        result_produccion = db.execute(query_produccion).mappings().first()
        
        hoy = result_produccion['hoy'] or 0
        ayer = result_produccion['ayer'] or 1
        
        if ayer > 0:
            trend_produccion = ((hoy - ayer) / ayer) * 100
        else:
            trend_produccion = 0
        
        return {
            "gallinas_trend": f"{'+' if trend_gallinas >= 0 else ''}{trend_gallinas:.1f}%",
            "produccion_trend": f"{'+' if trend_produccion >= 0 else ''}{trend_produccion:.1f}%"
        }
    except SQLAlchemyError as e:
        logger.error(f"Error al calcular tendencias: {e}")
        return {
            "gallinas_trend": "+0.0%",
            "produccion_trend": "+0.0%"
        }
