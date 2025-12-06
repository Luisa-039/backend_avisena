from core.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)

print("Columnas de la tabla 'tipo_sensores':")
columns = inspector.get_columns('tipo_sensores')
for col in columns:
    print(f"  - {col['name']} ({col['type']})")

print("\nColumnas de la tabla 'sensores':")
columns = inspector.get_columns('sensores')
for col in columns:
    print(f"  - {col['name']} ({col['type']})")


