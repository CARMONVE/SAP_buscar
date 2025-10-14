PASOS PARA PUBLICAR TU API EN RENDER.COM

1️⃣ Crea una cuenta en https://render.com

2️⃣ Sube esta carpeta (buscador_excel_publico) a un repositorio de GitHub.

3️⃣ En Render:
   - Haz clic en "New +" → "Web Service"
   - Conecta tu cuenta de GitHub y elige este repositorio.
   - En el campo "Start Command" escribe:
     uvicorn main:app --host 0.0.0.0 --port 10000
   - Selecciona Python 3.11 o superior.

4️⃣ Render creará una URL pública como:
   https://tubuscador.onrender.com

5️⃣ Prueba tu API:
   https://tubuscador.onrender.com/consulta/Juan%20Pérez
   o por SAP:
   https://tubuscador.onrender.com/consulta/12345

6️⃣ Si deseas actualizar los datos, reemplaza "datos.xlsx" y Render actualizará automáticamente.

---
CÓDIGO BASE: FastAPI + Pandas
Desarrollado con ayuda de ChatGPT (OpenAI)
