from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import pandas as pd
import re

app = FastAPI(
    title="Buscador Público de Datos",
    description="Busca por SAP, Ciudad o Nombre y devuelve la información de las demás columnas.",
    version="3.6"
)

# 🧩 Cargar el Excel
df = pd.read_excel("datos.xlsx", dtype=str).fillna("")

# 🧩 Definir manualmente los títulos de tus columnas (ajústalos según tu Excel)
df.columns = [
    "Ciudad",
    "Nombre",
    "SAP",
    "Teléfono",
    "WhatsApp",
    "Dirección",
    "Mapa"
]

# 🧩 Función: convertir URLs y teléfonos a enlaces clicables
def formatear_valor(valor):
    if not isinstance(valor, str):
        return valor

    # Si es un enlace (http o https)
    if re.match(r"^https?://", valor):
        return f'<a href="{valor}" target="_blank">🌐 Ver mapa</a>'

    # Si es un número tipo teléfono colombiano
    if re.match(r"^57\\d{10}$", valor):
        return f'<a href="https://wa.me/{valor}" target="_blank">💬 WhatsApp</a>'

    # Si incluye "Wsp" seguido de número
    wsp_match = re.search(r"57\\d{10}", valor)
    if wsp_match:
        numero = wsp_match.group(0)
        return f'<a href="https://wa.me/{numero}" target="_blank">💬 {valor}</a>'

    return valor


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
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
          table {
            border-collapse: collapse; margin-top: 20px;
            width: 100%; background: white; border-radius: 6px;
            overflow: hidden;
          }
          th {
            background: #007bff; color: white; padding: 10px;
            text-align: left;
          }
          td { border: 1px solid #ddd; padding: 8px; }
          tr:nth-child(even) { background: #f9f9f9; }
          a { color: #007bff; text-decoration: none; }
          a:hover { text-decoration: underline; }
          .container { max-width: 900px; margin: auto; }
        </style>
      </head>
      <body>
        <div class="container">
          <h2>🔍 Buscador público de SAP, Ciudad o Nombre</h2>
          <form method="get" action="/buscar">
            <input type="text" name="q" placeholder="Escribe SAP, Ciudad o Nombre" style="width: 60%">
            <button type="submit">Buscar</button>
          </form>
        </div>
      </body>
    </html>
    """


@app.get("/buscar", response_class=HTMLResponse)
async def buscar(request: Request):
    q = request.query_params.get("q", "").strip()
    if not q:
        return "<p>Por favor escribe algo para buscar.</p><a href='/'>Volver</a>"

    # 🔹 Si el texto ingresado es numérico → buscar solo en SAP
    if q.isdigit():
        resultados = df[df["SAP"].astype(str).str.contains(q, case=False, na=False)]
    else:
        # 🔹 Si es texto → buscar en todas las columnas
        resultados = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(q.lower()).any(), axis=1)]

    if resultados.empty:
        return f"<p>No se encontraron resultados para '{q}'.</p><a href='/'>Volver</a>"

    # Convertir links y teléfonos
    resultados_html = resultados.applymap(formatear_valor)

    # Generar tabla HTML con encabezados visibles
    columnas = "".join([f"<th>{col}</th>" for col in resultados_html.columns])
    filas = ""
    for _, fila in resultados_html.iterrows():
        filas += "<tr>" + "".join([f"<td>{valor}</td>" for valor in fila]) + "</tr>"
    tabla_html = f"<table><thead><tr>{columnas}</tr></thead><tbody>{filas}</tbody></table>"

    return f"""
    <html>
      <body style='font-family: Arial; background: #f4f4f4; padding: 20px;'>
        <div style='max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px;'>
          <h3>Resultados para: '{q}'</h3>
          {tabla_html}
          <br><a href='/'>🔙 Nueva búsqueda</a>
        </div>
      </body>
    </html>
    """


@app.get("/api/consulta/{valor}")
async def consulta(valor: str):
    valor = valor.strip()
    if valor.isdigit():
        coincidencias = df[df["SAP"].astype(str).str.contains(valor, case=False, na=False)]
    else:
        coincidencias = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(valor.lower()).any(), axis=1)]

    if coincidencias.empty:
        return {"error": f"No se encontró '{valor}'"}
    return {"resultados": coincidencias.to_dict(orient="records")}
