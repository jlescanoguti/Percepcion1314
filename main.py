from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import mysql.connector
import face_recognition
import shutil
import json

app = FastAPI()

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración MySQL
config = {
    'user': os.environ.get('MYSQLUSER'),
    'password': os.environ.get('MYSQLPASSWORD'),
    'host': os.environ.get('MYSQLHOST'),
    'port': int(os.environ.get('MYSQLPORT', 3306)),
    'database': os.environ.get('MYSQLDATABASE')
}

def get_db_connection():
    return mysql.connector.connect(**config)

# Endpoint para registrar alumnos
@app.post("/alumnos")
async def registrar_alumno(
    nombre: str = Form(...),
    apellido: str = Form(...),
    codigo: str = Form(...),
    correo: str = Form(...),
    foto: UploadFile = File(...)
):
    # Crear carpeta si no existe
    os.makedirs("rostros", exist_ok=True)
    ruta_foto = f"rostros/{codigo}.jpg"

    # Guardar la foto en disco
    with open(ruta_foto, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    # Cargar la imagen y calcular el encoding facial
    imagen = face_recognition.load_image_file(ruta_foto)
    encodings = face_recognition.face_encodings(imagen)
    if len(encodings) == 0:
        os.remove(ruta_foto)
        raise HTTPException(status_code=400, detail="No se detectó ningún rostro en la imagen.")
    encoding = encodings[0]
    encoding_json = json.dumps(encoding.tolist())

    # Guardar en la base de datos
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alumnos (nombre, apellido, codigo, correo, foto, encoding) VALUES (%s, %s, %s, %s, %s, %s)",
            (nombre, apellido, codigo, correo, ruta_foto, encoding_json)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.IntegrityError:
        os.remove(ruta_foto)
        raise HTTPException(status_code=400, detail="El código de alumno ya existe.")
    except Exception as e:
        os.remove(ruta_foto)
        raise HTTPException(status_code=500, detail=f"Error al registrar alumno: {str(e)}")

    return {"mensaje": "Alumno registrado exitosamente."}

@app.delete("/reiniciar_datos")
def reiniciar_datos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Vaciar las tablas en orden para evitar conflictos de claves foráneas
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE asistencias;")
        cursor.execute("TRUNCATE TABLE sesiones;")
        cursor.execute("TRUNCATE TABLE alumnos;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Datos reiniciados correctamente."}
    except Exception as e:
        return {"error": f"Error al reiniciar datos: {str(e)}"}

# Aquí puedes agregar los siguientes endpoints para el sistema de asistencias 