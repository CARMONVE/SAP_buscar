from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import pandas as pd
import re

app = FastAPI(
    title="Buscador Público de Datos",
    description="Busca por SAP, Ciudad o Nombre y devuelve la información de las demás columnas.",
    version="5.0"
)

# 🧩 Cargar Excel con encabezados originales
df = pd.read_excel("datos.xlsx", dtype=str, header=0).fillna("")

# 🧩 Convertir valores a botones interactivos (WhatsApp / Mapas)
def formatear_valor(valor):
    if not isinstance(valor, str):
        return valor

    # Si es un enlace (ej: Google Maps)
    if re.match(r"^https?://", valor):
        return f'<button onclick="window.open(\'{valor}\')" class="map-btn">📍 Ver mapa</button>'

    # Si es un número tipo WhatsApp colombiano
    if re.match(r"^57\d{10}$", valor):
        return f'<button onclick="window.open(\'https://wa.me/{valor}\')" class="whatsapp-btn">💬 WhatsApp</button>'

    # Si dentro del texto hay número de WhatsApp
    wsp = re.search(r"57\d{10}", valor)
    if wsp:
        num = wsp.group(0)
        return f'<button onclick="window.open(\'https://wa.me/{num}\')" class="whatsapp-btn">💬 {valor}</button>'

    return valor


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
      <head>
        <meta charset='utf-8'>
        <title>Buscador SAP</title>
        <link href='https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap' rel='stylesheet'>
        <style>
          body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #d9d9d9, #bfbfbf);
            color: #0a3d91;
            margin: 0; padding: 0;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
          }
          .card {
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            padding: 40px;
            width: 90%;
            max-width: 700px;
            text-align: center;
          }
          h2 {
            color: #0a3d91;
            margin-bottom: 20px;
          }
          input {
            padding: 10px;
            width: 70%;
            border-radius: 8px;
            border: 1px solid #ccc;
            font-size: 16px;
          }
          button {
            padding: 10px 15px;
            border: none;
            border-radius: 8px;
            background-color: #0a3d91;
            color: white;
            font-size: 16px;
            cursor: pointer;
          }
          button:hover {
            background-color: #062a6e;
          }
        </style>
      </head>
      <body>
        <div class='card'>
          <h2>🔍 Buscador de SAP, Ciudad o Nombre</h2>
          <form method='get' action='/buscar'>
            <input type='text' name='q' placeholder='Escribe SAP, Ciudad o Nombre'>
            <button type='submit'>Buscar</button>
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

    # 🔹 Si el texto es numérico → buscar solo en SAP
    if q.isdigit():
        if "Unnamed: 3" not in df.columns:
            return "<p>Error: no existe una columna llamada 'SAP' en el archivo Excel.</p>"
        resultados = df[df["Unnamed: 3"].astype(str).str.contains(q, case=False, na=False)]
    else:
        # 🔹 Si es texto → buscar en todas las columnas
        resultados = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(q.lower()).any(), axis=1)]

    if resultados.empty:
        return f"<p>No se encontraron resultados para '{q}'.</p><a href='/'>Volver</a>"

    # Aplicar formato (links y botones)
    resultados_html = resultados.applymap(formatear_valor)

    # Construir tabla HTML
    tabla_html = f"""
    <table>
      <thead>
        <tr>{"".join([f"<th>{c}</th>" for c in resultados_html.columns])}</tr>
      </thead>
      <tbody>
    """
    for _, fila in resultados_html.iterrows():
        tabla_html += "<tr>" + "".join([f"<td>{v}</td>" for v in fila]) + "</tr>"
    tabla_html += "</tbody></table>"

    # Página final
    return f"""
    <html>
      <head>
        <meta charset='utf-8'>
        <link href='https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap' rel='stylesheet'>
        <style>
          body {{
            background: #ff8000;
            font-family: 'Poppins', sans-serif;
            padding: 40px;
            color: #0a3d91;
          }}
          h3 {{
            color: #0a3d91;
          }}
          table {{
            border-collapse: collapse;
            width: 100%;
            background: white;
            border-radius: 10px;
            overflow: hidden;
          }}
          th {{
            background: #999999;
            color: white;
            padding: 10px;
            text-align: left;
          }}
          td {{
            border: 1px solid #ddd;
            padding: 8px;
          }}
          tr:nth-child(even) {{ background: #e8e8e8; }}
          .whatsapp-btn {{
            background-color: #25d366;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 6px 10px;
            cursor: pointer;
          }}
          .map-btn {{
            background-color: #4285F4;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 6px 10px;
            cursor: pointer;
          }}
        </style>
      </head>
      <body>
        <h3>Resultados para: '{q}'</h3>
        {tabla_html}
        <br><a href='/' style='color:#0a3d91; font-weight:bold;'>🔙 Nueva búsqueda</a>
      </body>
    </html>
    """


@app.get("/api/consulta/{valor}")
async def consulta(valor: str):
    valor = valor.strip()
    if valor.isdigit() and "Unnamed: 3" in df.columns:
        coincidencias = df[df["Unnamed: 3"].astype(str).str.contains(valor, case=False, na=False)]
    else:
        coincidencias = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(valor.lower()).any(), axis=1)]
    if coincidencias.empty:
        return {"error": f"No se encontró '{valor}'"}
    return {"resultados": coincidencias.to_dict(orient="records")}
