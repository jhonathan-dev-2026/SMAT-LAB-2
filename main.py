from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="SMAT API - Sistema de Monitoreo")

class Estacion(BaseModel):
    id: int
    nombre: str
    ubicacion: str

class Lectura(BaseModel):
    estacion_id: int
    valor: float

db_estaciones = []
db_lecturas = []

@app.post("/estaciones/", status_code=201)
async def crear_estacion(estacion: Estacion):
    db_estaciones.append(estacion)
    return {"msj": "Estación creada", "data": estacion}

@app.get("/estaciones/", response_model=List[Estacion])
async def listar_estaciones():
    return db_estaciones

@app.post("/lecturas/", status_code=201)
async def registrar_lectura(lectura: Lectura):
    db_lecturas.append(lectura)
    return {"status": "Lectura recibida"}

@app.get("/estaciones/{id}/riesgo")
async def obtener_riesgo(id: int):
    estacion_existe = any(e.id == id for e in db_estaciones)
    if not estacion_existe:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    lecturas = [l for l in db_lecturas if l.estacion_id == id]
    if not lecturas:
        return {"id": id, "nivel": "SIN DATOS", "valor": 0}

    ultima_lectura = lecturas[-1].valor
    if ultima_lectura > 20.0:
        nivel = "PELIGRO"
    elif ultima_lectura > 10.0:
        nivel = "ALERTA"
    else:
        nivel = "NORMAL"
    
    return {"id": id, "valor": ultima_lectura, "nivel": nivel}

@app.get("/estaciones/{id}/historial")
async def obtener_historial(id: int):
    estacion_existe = any(e.id == id for e in db_estaciones)
    if not estacion_existe:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    historial = [l for l in db_lecturas if l.estacion_id == id]
    conteo = len(historial)
    
    if conteo > 0:
        promedio = sum(l.valor for l in historial) / conteo
    else:
        promedio = 0.0
        
    return {
        "estacion_id": id,
        "lecturas": historial,
        "conteo": conteo,
        "promedio": round(promedio, 2)
    }