from fastapi import FastAPI
import pandas as pd

app = FastAPI(
    title="Buscador Público de Datos en Excel",
    description="API pública que devuelve la información según el Nombre o SAP.",
    version="1.0"
)

# Cargar el archivo Excel al iniciar la app
data = pd.read_excel("datos.xlsx")

@app.get("/")
def home():
    return {
        "mensaje": "Bienvenido al Buscador Público de Datos",
        "uso": "/consulta/{nombre_o_sap}"
    }

@app.get("/consulta/{valor}")
def consulta(valor: str):
    valor = valor.strip().lower()
    
    # Filtrar por coincidencia exacta en Nombre o SAP
    fila = data[
        (data["Nombre"].str.lower() == valor) |
        (data["SAP"].astype(str).str.lower() == valor)
    ]
    
    if not fila.empty:
        return {"resultado": fila.iloc[0].to_dict()}
    
    # Si no encuentra coincidencia exacta, intenta parcial (por si escriben incompleto)
    coincidencias = data[
        data["Nombre"].str.lower().str.contains(valor, na=False)
    ]
    if not coincidencias.empty:
        return {"sugerencias": coincidencias.to_dict(orient="records")}
    
    return {"error": f"No se encontró '{valor}' en los datos."}
