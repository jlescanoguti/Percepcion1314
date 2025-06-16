from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import torch
from torchvision import transforms
from PIL import Image
import io
import json
import mysql.connector
from torch.nn.functional import cosine_similarity
import pickle
import os
from pathlib import Path
import subprocess

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
    'user': 'root',
    'password': 'aYAWzuozJBVbtVsSimsrsHAdlNygEfGh',
    'host': 'trolley.proxy.rlwy.net',
    'port': '40718',
    'database': 'railway'
}

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

# Cargar clases
with open("clases.pkl", "rb") as f:
    clases = pickle.load(f)

model = CNNClasificador(num_classes=len(clases))
model.load_state_dict(torch.load("cnn_model.pth", map_location=torch.device("cpu")))
model.eval()
extractor = ExtractorEmbeddings(model)
extractor.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
    transforms.Resize((100, 100)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

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

        subprocess.run(["python", "entrenar_modelo.py"], check=True)

        # Recargar modelo y extractor tras reentrenamiento
        global clases, model, extractor
        with open("clases.pkl", "rb") as f:
            clases = pickle.load(f)
        model = CNNClasificador(num_classes=len(clases))
        model.load_state_dict(torch.load("cnn_model.pth", map_location="cpu"))
        model.eval()
        extractor = ExtractorEmbeddings(model)
        extractor.eval()

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_tensor = transform(img).unsqueeze(0).to("cpu")
        with torch.no_grad():
            embedding = extractor(img_tensor).float()
        embedding_list = embedding.squeeze().tolist()
        embedding_json = json.dumps(embedding_list)

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM usuario WHERE codigo = %s OR correo = %s", (codigo, correo))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="⚠️ Código o correo ya registrados")

        cursor.execute("SELECT kp FROM usuario")
        registros = cursor.fetchall()
        for (kp_json,) in registros:
            kp_array = torch.tensor(json.loads(kp_json), dtype=torch.float32).unsqueeze(0)
            sim = cosine_similarity(embedding, kp_array).item()
            if sim > 0.70:
                raise HTTPException(status_code=400, detail=f"❌ Rostro ya registrado con similitud {sim:.4f}")

        sql = """
        INSERT INTO usuario (nombre, apellido, codigo, correo, requisitoriado, foto, kp)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores = (nombre, apellido, codigo, correo, requisitoriado, image_bytes, embedding_json)
        cursor.execute(sql, valores)
        conn.commit()
        cursor.close()
        conn.close()

        return {"mensaje": "✅ Usuario registrado y modelo actualizado"}

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="❌ Error al reentrenar el modelo")

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"❌ Error en la base de datos: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error general: {e}")

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

@app.post("/comparar_rostro")
async def comparar_rostro(imagen: UploadFile = File(...)):
    try:
        image_bytes = await imagen.read()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_tensor = transform(img).unsqueeze(0).to("cpu")

        with torch.no_grad():
            embedding = extractor(img_tensor).float()

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM usuario")
        usuarios = cursor.fetchall()

        mejor_similitud = 0.0
        usuario_encontrado = None

        for usuario in usuarios:
            kp_array = torch.tensor(json.loads(usuario["kp"]), dtype=torch.float32).unsqueeze(0)
            similitud = cosine_similarity(embedding, kp_array).item()

            if similitud > mejor_similitud and similitud > 0.70:
                mejor_similitud = similitud
                usuario_encontrado = usuario

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
