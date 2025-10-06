from typing import Optional
import os
import tempfile
from fastapi import FastAPI, Form, Depends, Header, HTTPException, status, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from openpyxl import Workbook
from db import Base, engine, SessionLocal
from models import Inscripcion
from crypto import encrypt_text, decrypt_text
# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    # Si no se define, la app seguirá funcionando en local pero es inseguro
    print("WARNING: No API_KEY set in .env — protege /exportar_excel en producción")
# Crear tablas
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Portal de Inscripciones")
app.mount("/static", StaticFiles(directory="static"), name="static")
# Dependencia para verificar API key simple


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if API_KEY is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="API_KEY not configured on server")
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API Key")
    return True


@app.get("/")
def root():
    return FileResponse("static/form.html")


@app.post("/inscribir")
def inscribir(
    nombre: str = Form(...),
    apellidos: str = Form(...),
    dni: str = Form(...),
    telefono: str = Form(...),
    curso: str = Form(...),
    participo_prev: str = Form(None),
    precio_plan: str = Form(...)
):
    db = SessionLocal()
    try:
        ins = Inscripcion(
            nombre_enc=encrypt_text(nombre),
            apellidos_enc=encrypt_text(apellidos),
            dni_enc=encrypt_text(dni),
            telefono_enc=encrypt_text(telefono),
            curso_enc=encrypt_text(curso),
            participo_prev=1 if participo_prev == "1" else 0,
            precio_plan=precio_plan
        )
        db.add(ins)
        db.commit()
        return HTMLResponse("<h3>✅ Inscripción recibida correctamente</h3>")
    finally:
        db.close()


@app.get("/exportar_excel")
def exportar_excel(background_tasks: BackgroundTasks, authorized: bool = Depends(verify_api_key)):
    db = SessionLocal()
    try:
        rows = db.query(Inscripcion).all()
        wb = Workbook()
        ws = wb.active
        ws.title = "Inscripciones"
        # Cabecera
        ws.append([
            "ID", "Nombre", "Apellidos", "DNI",
            "Teléfono", "Curso", "Participó Año Pasado", "Plan"
        ])
        for r in rows:
            try:
                nombre = decrypt_text(r.nombre_enc)
                apellidos = decrypt_text(r.apellidos_enc)
                dni = decrypt_text(r.dni_enc)
                telefono = decrypt_text(r.telefono_enc)
                curso = decrypt_text(r.curso_enc)
            except Exception:
                # Si hay fallo de descifrado mostramos placeholder
                nombre = apellidos = dni = telefono = curso = "<error descifrado>"
            ws.append([r.id, nombre, apellidos, dni, telefono, curso,
                      "Sí" if r.participo_prev == 1 else "No", r.precio_plan])
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        wb.save(tmpfile.name)
        tmpfile.close()
        # Borrar el archivo tras la respuesta
        background_tasks.add_task(os.remove, tmpfile.name)

        return FileResponse(path=tmpfile.name, filename="inscripciones.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    finally:
        db.close()
