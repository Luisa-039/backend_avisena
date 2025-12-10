from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import tareas
from app.router import users, auth, ventas,modulos, permisos, roles, detalle_huevos, metodo_pago, detalle_salvamento, produccion_huevos, stock, tipo_huevos, rescue, chickens, isolation, type_chickens, chicken_incident, sheds, lands, incidentes_generales, registro_sensores, categories, inventory, sensor_types, sensors, dashboard, alimento, consumo_gallinas
app = FastAPI()

# Configuración de CORS para permitir todas las solicitudes desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Permitir estos métodos HTTP
    allow_headers=["*"],  # Permitir cualquier encabezado en las solicitudes
)
 
# Incluir en el objeto app los routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(lands.router, prefix="/lands", tags=["lands"])
app.include_router(incidentes_generales.router, prefix="/incidentes_generales", tags=["incidentes_generales"])
app.include_router(registro_sensores.router, prefix="/registro-sensores", tags=["Registro Sensores"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
app.include_router(sensor_types.router, prefix="/sensor-types", tags=["sensor_types"])
app.include_router(sensors.router, prefix="/sensors", tags=["sensors"])
app.include_router(isolation.router, prefix="/isolations", tags=["aislamiento"])
app.include_router(auth.router, prefix="/access", tags=["login"])
app.include_router(chicken_incident.router, prefix="/incident", tags=["incidentes"])
app.include_router(rescue.router, prefix="/rescue", tags=["salvamentos"])
app.include_router(chickens.router, prefix="/chickens", tags=["gallinas"])
app.include_router(type_chickens.router, prefix="/type_chicken", tags=['type_chicken'])
app.include_router(sheds.router, prefix="/sheds", tags=['sheds'])
app.include_router(produccion_huevos.router, prefix="/produccion-huevos", tags=["produccion-huevos"])
app.include_router(stock.router, prefix="/stock", tags=["stock"])
app.include_router(tipo_huevos.router, prefix="/tipo-huevos", tags=["tipo-huevos"])
app.include_router(modulos.router, prefix="/modulos", tags=["modulos"])
app.include_router(permisos.router, prefix="/permisos", tags=["permisos"])
app.include_router(roles.router, prefix="/roles", tags=["roles"])
app.include_router(ventas.router, prefix="/ventas", tags=["ventas"])
app.include_router(tareas.router, prefix="/tareas", tags=["tareas"])
app.include_router(detalle_huevos.router, prefix="/detalle_huevos", tags=["detalle_huevos"])
app.include_router(metodo_pago.router, prefix="/metodo_pago", tags=["metodo_pago"])
app.include_router(detalle_salvamento.router, prefix="/detalle_salvamento", tags=["detalle_salvamento"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(alimento.router, prefix="/alimento", tags=["alimento"])
app.include_router(consumo_gallinas.router, prefix="/consumo_gallinas", tags=["consumo_gallinas"])


@app.get("/")
def read_root():
    return {
                "message": "ok",
                "autor": "ADSO 2925889"
            }

