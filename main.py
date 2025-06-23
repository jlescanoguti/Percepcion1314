from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import torch
from torchvision import transforms
from PIL import Image, ImageEnhance, ImageFilter
import io
import json
import mysql.connector
from torch.nn.functional import cosine_similarity
import pickle
import os
from pathlib import Path
import subprocess
import numpy as np
import cv2
from typing import List, Tuple

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración MySQL
config = {
       'user': os.environ.get('DB_USER'),
       'password': os.environ.get('DB_PASSWORD'),
       'host': os.environ.get('DB_HOST'),
       'port': os.environ.get('DB_PORT'),
       'database': os.environ.get('DB_NAME')
   }

# === FUNCIONES DE PREPROCESAMIENTO MEJORADO ===
def detectar_y_recortar_rostro(imagen: Image.Image) -> Image.Image:
    """Detecta y recorta el rostro principal de la imagen"""
    try:
        # Convertir a numpy array
        img_array = np.array(imagen)
        
        # Convertir a escala de grises para detección
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Cargar clasificador Haar para rostros (usar ruta alternativa)
        cascade_path = 'haarcascade_frontalface_default.xml'
        if not os.path.exists(cascade_path):
            # Si no existe, usar la imagen original
            return imagen
        
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Detectar rostros
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            # Tomar el rostro más grande
            x, y, w, h = max(faces, key=lambda x: x[2] * x[3])
            
            # Agregar margen del 20%
            margin = int(min(w, h) * 0.2)
            x = max(0, x - margin)
            y = max(0, y - margin)
            w = min(img_array.shape[1] - x, w + 2 * margin)
            h = min(img_array.shape[0] - y, h + 2 * margin)
            
            # Recortar y convertir de vuelta a PIL
            rostro_recortado = img_array[y:y+h, x:x+w]
            return Image.fromarray(rostro_recortado)
        
        return imagen  # Si no detecta rostro, devolver imagen original
    except Exception:
        return imagen

def aplicar_aumentacion(imagen: Image.Image) -> List[Image.Image]:
    """Aplica técnicas de data augmentation para generar múltiples variaciones"""
    variaciones = [imagen]
    
    # 1. Rotación ligera
    for angulo in [-5, 5, -10, 10]:
        variaciones.append(imagen.rotate(angulo, expand=False))
    
    # 2. Cambios de brillo
    for factor in [0.8, 1.2]:
        enhancer = ImageEnhance.Brightness(imagen)
        variaciones.append(enhancer.enhance(factor))
    
    # 3. Cambios de contraste
    for factor in [0.9, 1.1]:
        enhancer = ImageEnhance.Contrast(imagen)
        variaciones.append(enhancer.enhance(factor))
    
    # 4. Suavizado ligero
    variaciones.append(imagen.filter(ImageFilter.GaussianBlur(radius=0.5)))
    
    # 5. Nitidez
    variaciones.append(imagen.filter(ImageFilter.UnsharpMask(radius=1, percent=150)))
    
    return variaciones

def normalizar_embedding(embedding: torch.Tensor) -> torch.Tensor:
    """Normaliza el embedding para mejorar la comparación"""
    # Normalización L2
    norm = torch.norm(embedding, p=2, dim=1, keepdim=True)
    return embedding / (norm + 1e-8)

# Modelo y extractor
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
        self.output = torch.nn.Linear(128, len(clases))

    def forward(self, x):
        x = self.features(x)
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.relu(x)
        return self.output(x)

class ExtractorEmbeddings(torch.nn.Module):
    def __init__(self, modelo_entrenado):
        super().__init__()
        self.features = modelo_entrenado.features
        self.flatten = modelo_entrenado.flatten
        self.fc1 = modelo_entrenado.fc1
        self.relu = modelo_entrenado.relu

    def forward(self, x):
        x = self.features(x)
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.relu(x)
        return x

# === Cargar modelo entrenado y clases ===
try:
    with open("clases.pkl", "rb") as f:
        clases = pickle.load(f)

    if len(clases) == 0:
        print("⚠️ No hay clases disponibles. El modelo está vacío.")
        clases = []
        model = CNNClasificador(num_classes=0)
        model.eval()
        extractor = ExtractorEmbeddings(model)
        extractor.eval()
    else:
        model = CNNClasificador(num_classes=len(clases))
        model.load_state_dict(torch.load("cnn_model.pth", map_location=torch.device("cpu")))
        model.eval()
        extractor = ExtractorEmbeddings(model)
        extractor.eval()
        print(f"✅ Modelo cargado con {len(clases)} clases: {clases}")
        
except FileNotFoundError:
    print("⚠️ Archivos de modelo no encontrados. Creando modelo vacío.")
    clases = []
    model = CNNClasificador(num_classes=0)
    model.eval()
    extractor = ExtractorEmbeddings(model)
    extractor.eval()
except Exception as e:
    print(f"❌ Error al cargar modelo: {e}")
    clases = []
    model = CNNClasificador(num_classes=0)
    model.eval()
    extractor = ExtractorEmbeddings(model)
    extractor.eval()

transform = transforms.Compose([
    transforms.Resize((100, 100)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# === FUNCIÓN MEJORADA PARA EXTRAER EMBEDDINGS ===
def extraer_embeddings_robustos(imagen: Image.Image) -> List[torch.Tensor]:
    """Extrae múltiples embeddings de una imagen usando técnicas de augmentation"""
    embeddings = []
    
    # 1. Preprocesamiento: detectar y recortar rostro
    rostro_recortado = detectar_y_recortar_rostro(imagen)
    
    # 2. Aplicar augmentation
    variaciones = aplicar_aumentacion(rostro_recortado)
    
    # 3. Extraer embeddings de cada variación
    for variacion in variaciones:
        try:
            img_tensor = transform(variacion)
            img_tensor = img_tensor.unsqueeze(0)  # Agregar dimensión de batch
            with torch.no_grad():
                embedding = extractor(img_tensor).float()
                embedding_norm = normalizar_embedding(embedding)
                embeddings.append(embedding_norm.squeeze())
        except Exception:
            continue
    
    return embeddings

# === FUNCIÓN MEJORADA PARA COMPARAR EMBEDDINGS ===
def comparar_embeddings_robustos(embedding_actual: torch.Tensor, embeddings_almacenados: List[torch.Tensor]) -> Tuple[float, float]:
    """Compara embeddings usando múltiples métricas"""
    embedding_actual_norm = normalizar_embedding(embedding_actual.unsqueeze(0)).squeeze()
    
    similitudes_cosine = []
    similitudes_euclidean = []
    
    for emb_almacenado in embeddings_almacenados:
        # Similitud coseno
        sim_cos = cosine_similarity(embedding_actual_norm.unsqueeze(0), emb_almacenado.unsqueeze(0)).item()
        similitudes_cosine.append(sim_cos)
        
        # Distancia euclidiana normalizada
        dist_euc = torch.norm(embedding_actual_norm - emb_almacenado).item()
        sim_euc = 1.0 / (1.0 + dist_euc)  # Convertir distancia a similitud
        similitudes_euclidean.append(sim_euc)
    
    # Combinar métricas (promedio ponderado)
    max_cosine = max(similitudes_cosine)
    max_euclidean = max(similitudes_euclidean)
    
    # Peso mayor para similitud coseno (más robusta)
    similitud_final = 0.7 * max_cosine + 0.3 * max_euclidean
    
    return similitud_final, max_cosine

# === Ruta: Registrar nuevo usuario ===
@app.post("/registrar_usuario")
async def registrar_usuario(
    nombre: str = Form(...),
    apellido: str = Form(...),
    codigo: str = Form(...),
    correo: str = Form(...),
    requisitoriado: bool = Form(...),
    imagen: UploadFile = File(...)
):
    try:
        nombre_usuario = f"{nombre}{apellido}".replace(" ", "")
        carpeta_usuario = Path("dataset_augmented") / nombre_usuario
        carpeta_usuario.mkdir(parents=True, exist_ok=True)

        image_bytes = await imagen.read()
        img_path = carpeta_usuario / f"{nombre_usuario}.jpg"
        with open(img_path, "wb") as f:
            f.write(image_bytes)

        # Solo reentrenar si hay imágenes válidas
        try:
            subprocess.run(["python", "entrenar_modelo.py"], check=True, capture_output=True, text=True)
            print("✅ Modelo reentrenado exitosamente")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Error al reentrenar modelo: {e}")
            print("💡 Continuando con el modelo actual...")

        # Recargar modelo
        global clases, model, extractor
        try:
            with open("clases.pkl", "rb") as f:
                clases = pickle.load(f)
                
                if len(clases) > 0:
                    model = CNNClasificador(num_classes=len(clases))
                    model.load_state_dict(torch.load("cnn_model.pth", map_location="cpu"))
                    model.eval()
                    extractor = ExtractorEmbeddings(model)
                    extractor.eval()
                    print(f"✅ Modelo recargado con {len(clases)} clases")
                else:
                    print("⚠️ Modelo vacío, usando embeddings básicos")
        except Exception as e:
            print(f"⚠️ Error al recargar modelo: {e}")
            print("💡 Continuando con embeddings básicos...")

        # Extraer múltiples embeddings robustos
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        embeddings = extraer_embeddings_robustos(img)
        
        if not embeddings:
            raise HTTPException(status_code=400, detail="❌ No se pudieron extraer características faciales válidas")
        
        # Guardar múltiples embeddings como JSON
        embeddings_json = json.dumps([emb.tolist() for emb in embeddings])

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuario WHERE codigo = %s OR correo = %s", (codigo, correo))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="⚠️ Código o correo ya registrados")

        # Verificar duplicados con múltiples embeddings (solo si hay usuarios existentes)
        cursor.execute("SELECT COUNT(*) FROM usuario")
        count_result = cursor.fetchone()
        if count_result and count_result[0] > 0:
            cursor.execute("SELECT kp FROM usuario")
            for row in cursor.fetchall():
                kp_json = row[0]
                if kp_json:  # Verificar que no sea None
                    try:
                        embeddings_almacenados = [torch.tensor(emb, dtype=torch.float32) for emb in json.loads(str(kp_json))]
                        for embedding_actual in embeddings:
                            similitud, _ = comparar_embeddings_robustos(embedding_actual, embeddings_almacenados)
                            if similitud > 0.75:  # Threshold más estricto
                                raise HTTPException(status_code=400, detail=f"❌ Rostro ya registrado con similitud {similitud:.4f}")
                    except Exception as e:
                        print(f"⚠️ Error al verificar duplicados: {e}")
                        continue

        sql = """INSERT INTO usuario (nombre, apellido, codigo, correo, requisitoriado, foto, kp)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (nombre, apellido, codigo, correo, requisitoriado, image_bytes, embeddings_json))
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "✅ Usuario registrado y modelo actualizado"}

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="❌ Error al reentrenar el modelo")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error general: {e}")

# === Ruta: Listar todos los usuarios ===
@app.get("/usuarios")
def listar_usuarios():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, apellido, codigo, correo, requisitoriado FROM usuario")
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Ruta: Consultar usuario por código ===
@app.get("/usuario/{codigo}")
def obtener_usuario(codigo: str):
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, apellido, codigo, correo, requisitoriado FROM usuario WHERE codigo = %s", (codigo,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        if usuario:
            return usuario
        raise HTTPException(status_code=404, detail="❌ Usuario no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Ruta: Editar usuario existente ===
@app.put("/usuario/{codigo}")
async def actualizar_usuario(
    codigo: str,
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo: str = Form(...),
    requisitoriado: bool = Form(...),
    imagen: UploadFile = File(None)
):
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        if imagen:
            image_bytes = await imagen.read()
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            # Extraer múltiples embeddings robustos
            embeddings = extraer_embeddings_robustos(img)
            
            if not embeddings:
                raise HTTPException(status_code=400, detail="❌ No se pudieron extraer características faciales válidas")
            
            # Guardar múltiples embeddings como JSON
            embeddings_json = json.dumps([emb.tolist() for emb in embeddings])

            sql = """UPDATE usuario SET nombre=%s, apellido=%s, correo=%s,
                     requisitoriado=%s, foto=%s, kp=%s WHERE codigo=%s"""
            cursor.execute(sql, (nombre, apellido, correo, requisitoriado,
                                 image_bytes, embeddings_json, codigo))
        else:
            sql = """UPDATE usuario SET nombre=%s, apellido=%s, correo=%s,
                     requisitoriado=%s WHERE codigo=%s"""
            cursor.execute(sql, (nombre, apellido, correo, requisitoriado, codigo))

        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "✅ Usuario actualizado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Ruta: Eliminar usuario por código ===
@app.delete("/usuario/{codigo}")
def eliminar_usuario(codigo: str):
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuario WHERE codigo = %s", (codigo,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "✅ Usuario eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Ruta: Reiniciar base de usuarios ===
@app.delete("/reiniciar_usuarios")
def reiniciar_usuarios():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE usuario")
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "✅ Tabla 'usuario' reiniciada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

# === Ruta: Comparar rostro capturado ===
@app.post("/comparar_rostro")
async def comparar_rostro(imagen: UploadFile = File(...)):
    try:
        image_bytes = await imagen.read()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Extraer múltiples embeddings robustos
        embeddings_actuales = extraer_embeddings_robustos(img)
        
        if not embeddings_actuales:
            raise HTTPException(status_code=400, detail="❌ No se pudieron extraer características faciales válidas")

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuario")
        usuarios = cursor.fetchall()

        mejor_similitud = 0.0
        usuario_encontrado = None
        
        for usuario in usuarios:
            kp_json = usuario.get("kp")
            if kp_json:  # Verificar que no sea None
                try:
                    embeddings_almacenados = [torch.tensor(emb, dtype=torch.float32) for emb in json.loads(str(kp_json))]
                    # Comparar con cada embedding actual
                    for embedding_actual in embeddings_actuales:
                        similitud, sim_cosine = comparar_embeddings_robustos(embedding_actual, embeddings_almacenados)
                        if similitud > mejor_similitud and similitud > 0.70:
                            mejor_similitud = similitud
                            usuario_encontrado = usuario
                except Exception:
                    continue

        cursor.close()
        conn.close()

        if usuario_encontrado:
            alerta = usuario_encontrado["requisitoriado"] == 1
            return {
                "mensaje": "✅ Usuario identificado con éxito",
                "similitud": mejor_similitud,
                "usuario": {
                    "nombre": usuario_encontrado["nombre"],
                    "apellido": usuario_encontrado["apellido"],
                    "codigo": usuario_encontrado["codigo"],
                    "correo": usuario_encontrado["correo"],
                    "requisitoriado": bool(usuario_encontrado["requisitoriado"]),
                },
                "alerta": alerta,
                "notificacion": "🚨 ¡ALERTA DE SEGURIDAD! Usuario requisitoriado detectado. Notificación enviada a la Policía (simulada)" if alerta else None
            }

        return {
            "mensaje": "❌ No se encontró coincidencia con ningún usuario registrado",
            "similitud_maxima": mejor_similitud
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error en la comparación facial: {e}")
