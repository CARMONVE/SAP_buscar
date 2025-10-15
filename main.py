from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI(
    title="Buscador Público de Datos",
    description="Busca por SAP, Ciudad o Nombre y devuelve la información de las demás columnas.",
    version="2.0"
)

# Cargar el Excel
df = pd.read_excel("datos.xlsx", dtype=str).fillna("")

# Página web principal
@app.get("/", response_class=HTMLResponse)
async def home():
    return '''
    <html>
      <head>
        <meta charset="utf-8">
        <title>Buscador SAP</title>
        <style>
          body { font-family: Arial; padding: 40px; background: #f4f4f4; }
          h2 { color: #333; }
          form { margin-top: 20px; }
          input, button {
            padding: 10px; font-size: 16px;
            border: 1px solid #ccc; border-radius: 5px;
          }
          table { border-collapse: collapse; margin-top: 20px; width: 100%; }
          th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
          th { background: #eee; }
        </style>
      </head>
      <body>
        <h2>🔍 Buscador público de SAP, Ciudad o Nombre</h2>
        <form method="get" action="/buscar">
          <input type="text" name="q" placeholder="Escribe SAP, Ciudad o Nombre" style="width: 60%">
          <button type="submit">Buscar</button>
        </form>
      </body>
    </html>
    '''

# Página de resultados
@app.get("/buscar", response_class=HTMLResponse)
async def buscar(request: Request):
    q = request.query_params.get("q", "").strip().lower()
    if not q:
        return "<p>Por favor escribe algo para buscar.</p><a href='/'>Volver</a>"
    resultados = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(q).any(), axis=1)]
    if resultados.empty:
        return f"<p>No se encontraron resultados para '{q}'.</p><a href='/'>Volver</a>"
    tabla_html = resultados.to_html(index=False, border=1)
    return f"<html><body><h3>Resultados para: '{q}'</h3>{tabla_html}<br><a href='/'>🔙 Nueva búsqueda</a></body></html>"

# API JSON (opcional)
@app.get("/api/consulta/{valor}")
async def consulta(valor: str):
    valor = valor.strip().lower()
    coincidencias = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(valor).any(), axis=1)]
    if coincidencias.empty:
        return {"error": f"No se encontró '{valor}'"}
    return {"resultados": coincidencias.to_dict(orient="records")}
