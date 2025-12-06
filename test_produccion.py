import sys
sys.path.insert(0, '.')
from core.database import get_db
from app.crud.dashboard import get_produccion_semanal
from datetime import date

db = next(get_db())
resultado = get_produccion_semanal(db)

print('=== RESPUESTA DEL ENDPOINT get_produccion_semanal ===')
print(f'Labels: {resultado["labels"]}')
print(f'Semana actual: {resultado["data_actual"]}')
print(f'Semana anterior: {resultado["data_anterior"]}')
print(f'\nTotal semana actual: {sum(resultado["data_actual"])}')
print(f'Total semana anterior: {sum(resultado["data_anterior"])}')

print('\n=== MAPEO DÍA A DÍA ===')
for i, label in enumerate(resultado["labels"]):
    print(f'{label}: {resultado["data_actual"][i]} huevos (anterior: {resultado["data_anterior"][i]})')
