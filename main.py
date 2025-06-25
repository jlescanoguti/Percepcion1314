from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import mysql.connector
from PIL import Image
import io
import pickle
import torch
from torchvision import transforms
import subprocess
import numpy as np
from pathlib import Path
import json
from datetime import datetime, timedelta
import sys
import uuid

app = FastAPI(title="Sistema de Reconocimiento Facial - Gestión de Asistencias")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración MySQL - Railway
config = {
    'user': os.environ.get('MYSQLUSER', 'root'),
    'password': os.environ.get('MYSQLPASSWORD', 'fTYMTAYZqsLCnLJalSbBOKssAFEmovIg'),
    'host': os.environ.get('MYSQLHOST', 'hopper.proxy.rlwy.net'),
    'port': int(os.environ.get('MYSQLPORT', 15015)),
    'database': os.environ.get('MYSQLDATABASE', 'railway')
}

def get_db_connection():
    return mysql.connector.connect(**config)

# === Función para inicializar la base de datos ===
def init_database():
    """Inicializar las tablas en la base de datos de Railway"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Crear tabla de alumnos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alumnos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                codigo VARCHAR(20) UNIQUE NOT NULL,
                correo VARCHAR(100),
                foto VARCHAR(255),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear tabla de sesiones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sesiones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_fin TIMESTAMP NULL,
                estado ENUM('activa', 'finalizada') DEFAULT 'activa'
            )
        """)
        
        # Crear tabla de asistencias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asistencias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_sesion INT,
                id_alumno INT,
                estado VARCHAR(50) DEFAULT 'Asistió',
                fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_sesion) REFERENCES sesiones(id),
                FOREIGN KEY (id_alumno) REFERENCES alumnos(id)
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Base de datos inicializada correctamente")
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")

# Inicializar base de datos al arrancar
init_database()

# === Transformación para preprocesar imágenes ===
transform = transforms.Compose([
    transforms.Resize((100, 100)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# === Arquitectura CNN ligera (debe coincidir con entrenar_modelo.py) ===
class CNNClasificador(torch.nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.features = torch.nn.Sequential(
            torch.nn.Conv2d(3, 16, 3, padding=1), torch.nn.ReLU(), torch.nn.MaxPool2d(2),
            torch.nn.Conv2d(16, 32, 3, padding=1), torch.nn.ReLU(), torch.nn.MaxPool2d(2),
            torch.nn.Conv2d(32, 64, 3, padding=1), torch.nn.ReLU(), torch.nn.MaxPool2d(2)
        )
        self.flatten = torch.nn.Flatten()
        self.fc1 = torch.nn.Linear(64 * 12 * 12, 128)
        self.relu = torch.nn.ReLU()
        self.output = torch.nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.features(x)
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.relu(x)
        return self.output(x)

# === Cargar modelo y clases ===
def cargar_modelo_y_clases():
    try:
        # Intentar cargar con el nuevo formato
        if os.path.exists("clases_modelo.json"):
            with open("clases_modelo.json", "r") as f:
                clases = json.load(f)
            model = CNNClasificador(num_classes=len(clases))
            model.load_state_dict(torch.load("modelo_reconocimiento.pth", map_location=torch.device("cpu")))
            model.eval()
            return model, clases
        # Fallback al formato anterior
        elif os.path.exists("clases.pkl"):
            with open("clases.pkl", "rb") as f:
                clases = pickle.load(f)
            model = CNNClasificador(num_classes=len(clases))
            model.load_state_dict(torch.load("cnn_model.pth", map_location=torch.device("cpu")))
            model.eval()
            return model, clases
        else:
            return None, None
    except Exception as e:
        print(f"Error cargando modelo: {e}")
        return None, None

# === Endpoint raíz ===
@app.get("/")
def read_root():
    return {"message": "Sistema de Reconocimiento Facial - API funcionando"}

# === Endpoint para registrar alumnos ===
@app.post("/alumnos")
async def registrar_alumno(
    nombre: str = Form(...),
    apellido: str = Form(...),
    codigo: str = Form(...),
    correo: str = Form(...),
    foto: UploadFile = File(...)
):
    # Guardar la foto en dataset_augmented/<NombreApellido>/
    nombre_usuario = f"{nombre}{apellido}".replace(" ", "")
    carpeta_usuario = Path("dataset_augmented") / nombre_usuario
    carpeta_usuario.mkdir(parents=True, exist_ok=True)
    img_path = carpeta_usuario / f"{nombre_usuario}.jpg"
    image_bytes = await foto.read()
    with open(img_path, "wb") as f:
        f.write(image_bytes)
    # Reentrenar el modelo
    try:
        subprocess.run(["python", "entrenar_modelo.py"], check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error al reentrenar el modelo: {e}")
    # Guardar datos en la base de datos
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alumnos (nombre, apellido, codigo, correo, foto) VALUES (%s, %s, %s, %s, %s)",
            (nombre, apellido, codigo, correo, str(img_path))
        )
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.IntegrityError:
        os.remove(img_path)
        raise HTTPException(status_code=400, detail="El código de alumno ya existe.")
    except Exception as e:
        os.remove(img_path)
        raise HTTPException(status_code=500, detail=f"Error al registrar alumno: {str(e)}")
    return {"mensaje": "Alumno registrado exitosamente y modelo actualizado."}

# === Endpoint para pasar asistencia (reconocimiento facial) ===
@app.post("/asistencia/{id_sesion}")
async def pasar_asistencia(id_sesion: int, foto: UploadFile = File(...)):
    # Cargar modelo y clases
    model, clases = cargar_modelo_y_clases()
    if model is None or clases is None:
        raise HTTPException(status_code=500, detail="Modelo no disponible")
    
    # Procesar imagen
    image_bytes = await foto.read()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_tensor = transform(img).unsqueeze(0)
    
    # Predicción
    with torch.no_grad():
        outputs = model(img_tensor)
        _, pred = torch.max(outputs, 1)
        alumno_idx = pred.item()
        alumno_nombre = clases[alumno_idx]
    
    # Buscar alumno en la base de datos
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alumnos WHERE REPLACE(CONCAT(nombre, apellido), ' ', '') = %s", (alumno_nombre,))
        alumno = cursor.fetchone()
        if not alumno:
            raise HTTPException(status_code=404, detail="Alumno no encontrado en la base de datos.")
        
        # Marcar asistencia en la sesión
        cursor.execute("UPDATE asistencias SET estado = 'Asistió' WHERE id_sesion = %s AND id_alumno = %s", (id_sesion, alumno['id']))
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": f"Asistencia registrada para {alumno['nombre']} {alumno['apellido']} en la sesión {id_sesion}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al pasar asistencia: {str(e)}")

# === Endpoint para crear una nueva sesión ===
@app.post("/crear-sesion")
async def crear_sesion(nombre: str = Form(...)):
    """Crear una nueva sesión de asistencia"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sesiones (nombre, fecha_inicio, estado)
            VALUES (%s, NOW(), 'activa')
        """, (nombre,))
        
        sesion_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": f"Sesión '{nombre}' creada exitosamente", "sesion_id": sesion_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando sesión: {str(e)}")

# === Endpoint para listar todas las sesiones ===
@app.get("/listar-sesiones")
async def listar_sesiones():
    """Listar todas las sesiones"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, nombre, fecha_inicio, fecha_fin, estado
            FROM sesiones
            ORDER BY fecha_inicio DESC
        """)
        
        sesiones = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"sesiones": sesiones}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando sesiones: {str(e)}")

# === Endpoint para finalizar una sesión ===
@app.post("/finalizar-sesion/{sesion_id}")
async def finalizar_sesion(sesion_id: int):
    """Finalizar una sesión específica"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sesiones 
            SET fecha_fin = NOW(), estado = 'finalizada'
            WHERE id = %s AND estado = 'activa'
        """, (sesion_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Sesión no encontrada o ya finalizada")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": f"Sesión {sesion_id} finalizada exitosamente"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finalizando sesión: {str(e)}")

# === Endpoint para generar reporte de asistencia ===
@app.get("/reporte-asistencia/{sesion_id}")
async def generar_reporte_asistencia(sesion_id: int):
    """Generar reporte de asistencia para una sesión específica"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        
        cursor = conn.cursor(dictionary=True)
        
        # Obtener información de la sesión
        cursor.execute("SELECT * FROM sesiones WHERE id = %s", (sesion_id,))
        sesion = cursor.fetchone()
        
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        # Obtener lista de todos los alumnos
        cursor.execute("SELECT id, nombre, apellido, codigo FROM alumnos ORDER BY apellido, nombre")
        todos_alumnos = cursor.fetchall()
        
        # Obtener asistencias de la sesión
        cursor.execute("""
            SELECT a.alumno_id, al.nombre, al.apellido, al.codigo, a.fecha_hora
            FROM asistencias a
            JOIN alumnos al ON a.alumno_id = al.id
            WHERE a.sesion_id = %s
            ORDER BY al.apellido, al.nombre
        """, (sesion_id,))
        asistencias = cursor.fetchall()
        
        # Crear diccionario de asistencias para búsqueda rápida
        asistencias_dict = {a['alumno_id']: a for a in asistencias}
        
        # Generar reporte
        reporte = {
            "sesion": {
                "id": sesion['id'],
                "nombre": sesion['nombre'],
                "fecha_inicio": sesion['fecha_inicio'].isoformat() if sesion['fecha_inicio'] else None,
                "fecha_fin": sesion['fecha_fin'].isoformat() if sesion['fecha_fin'] else None,
                "estado": sesion['estado']
            },
            "resumen": {
                "total_alumnos": len(todos_alumnos),
                "asistencias": len(asistencias),
                "ausencias": len(todos_alumnos) - len(asistencias),
                "porcentaje_asistencia": f"{(len(asistencias) / len(todos_alumnos) * 100):.1f}%" if todos_alumnos else "0%"
            },
            "alumnos": []
        }
        
        for alumno in todos_alumnos:
            asistio = alumno['id'] in asistencias_dict
            reporte["alumnos"].append({
                "id": alumno['id'],
                "nombre": f"{alumno['nombre']} {alumno['apellido']}",
                "codigo": alumno['codigo'],
                "asistio": asistio,
                "hora_asistencia": asistencias_dict[alumno['id']]['fecha_hora'].isoformat() if asistio else None
            })
        
        cursor.close()
        conn.close()
        
        return reporte
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")

# === Endpoint para listar todos los alumnos registrados ===
@app.get("/alumnos")
async def listar_alumnos():
    """Listar todos los alumnos registrados"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, nombre, apellido, codigo, fecha_registro
            FROM alumnos
            ORDER BY apellido, nombre
        """)
        
        alumnos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"alumnos": alumnos}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando alumnos: {str(e)}")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 