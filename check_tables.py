from core.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

print("Todas las tablas en la base de datos:")
for table in sorted(tables):
    print(f"  - {table}")

print("\n\nTablas que contienen 'incid' o 'incident':")
incident_tables = [t for t in tables if 'incident' in t.lower() or 'incid' in t.lower()]
for t in incident_tables:
    print(f"  - {t}")
