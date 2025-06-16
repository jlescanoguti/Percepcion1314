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

# Cargar clases
with open("clases.pkl", "rb") as f:
    clases = pickle.load(f)

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
        self.output = torch.nn.Linear(128, num_classes)

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

model = CNNClasificador(num_classes=len(clases))
model.load_state_dict(torch.load("cnn_model.pth", map_location=torch.device("cpu")))
model.eval()
extractor = ExtractorEmbeddings(model)
extractor.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
    transforms.Resize((100, 100)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])  # Cambio 2: normalización
])

@app.post("/registrar_usuario")
async def registrar_usuario(
    nombre: str = Form(...),
    apellido: str = Form(...),
    codigo: str = Form(...),
    correo: str = Form(...),
    requisitoriado: bool = Form(...),
    imagen: UploadFile = File(...)  # asegurado el tipo File
):
    try:
        # Leer imagen
        image_bytes = await imagen.read()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_tensor = transform(img).unsqueeze(0).to("cpu")

        # Embedding
        with torch.no_grad():
            embedding = extractor(img_tensor).float()  # Cambio 1: forzar float
        embedding_list = embedding.squeeze().tolist()
        embedding_json = json.dumps(embedding_list)

        # Conectar a base de datos
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # Verificar duplicado por código o correo
        cursor.execute("SELECT COUNT(*) FROM usuario WHERE codigo = %s OR correo = %s", (codigo, correo))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="⚠️ Código o correo ya registrados")

        # Verificar duplicado por similitud facial
        cursor.execute("SELECT kp FROM usuario")
        registros = cursor.fetchall()
        for (kp_json,) in registros:
            kp_array = torch.tensor(json.loads(kp_json), dtype=torch.float32).unsqueeze(0)  # Cambio 1
            sim = cosine_similarity(embedding, kp_array).item()
            print(f"Similitud con un usuario en DB: {sim:.4f}")  # Cambio 3: imprimir similitud
            if sim > 0.85:
                raise HTTPException(status_code=400, detail=f"❌ Rostro ya registrado con similitud {sim:.4f}")

        # Insertar en la base de datos
        sql = """
        INSERT INTO usuario (nombre, apellido, codigo, correo, requisitoriado, foto, kp)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores = (nombre, apellido, codigo, correo, requisitoriado, image_bytes, embedding_json)
        cursor.execute(sql, valores)
        conn.commit()
        cursor.close()
        conn.close()

        return {"mensaje": "✅ Usuario registrado correctamente"}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error general: {e}")
