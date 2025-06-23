import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import pickle

# === Configuración de paths ===
DATASET_DIR = "dataset_augmented"
MODEL_PATH = "cnn_model.pth"
CLASES_PATH = "clases.pkl"

# === Verificar si hay imágenes válidas en el dataset ===
def verificar_dataset():
    """Verifica si hay imágenes válidas en el dataset"""
    if not os.path.exists(DATASET_DIR):
        print("⚠️ Carpeta dataset_augmented no existe")
        return False
    
    # Buscar imágenes válidas en subcarpetas
    imagenes_encontradas = []
    for root, dirs, files in os.walk(DATASET_DIR):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                imagenes_encontradas.append(os.path.join(root, file))
    
    if not imagenes_encontradas:
        print("⚠️ No se encontraron imágenes válidas en dataset_augmented")
        return False
    
    print(f"✅ Encontradas {len(imagenes_encontradas)} imágenes válidas")
    return True

# === Arquitectura CNN ===
class CNNClasificador(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2)
        )
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(64 * 12 * 12, 128)
        self.relu = nn.ReLU()
        self.output = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.features(x)
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.relu(x)
        return self.output(x)

# === Transformaciones ===
transform = transforms.Compose([
    transforms.Resize((100, 100)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# === Verificar dataset antes de entrenar ===
if not verificar_dataset():
    print("❌ No se puede entrenar el modelo sin imágenes válidas")
    print("💡 Registra al menos un usuario con imagen antes de entrenar")
    
    # Crear clases vacías para evitar errores
    clases = []
    with open(CLASES_PATH, "wb") as f:
        pickle.dump(clases, f)
    
    # Crear modelo vacío
    model = CNNClasificador(num_classes=0)
    torch.save(model.state_dict(), MODEL_PATH)
    print("✅ Modelo vacío creado para evitar errores")
    exit(0)

# === Cargar dataset ===
try:
    dataset = datasets.ImageFolder(DATASET_DIR, transform=transform)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
    
    # === Guardar clases ===
    clases = dataset.classes
    with open(CLASES_PATH, "wb") as f:
        pickle.dump(clases, f)
    
    print(f"✅ Dataset cargado con {len(clases)} clases: {clases}")
    
    # === Entrenamiento del modelo ===
    model = CNNClasificador(num_classes=len(clases))
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print("🚀 Iniciando entrenamiento del modelo...")
    for epoch in range(10):
        total_loss = 0
        for images, labels in dataloader:
            outputs = model(images)
            loss = criterion(outputs, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"🔁 Época {epoch+1}/10 - Pérdida total: {total_loss:.4f}")
    
    # === Guardar modelo entrenado ===
    torch.save(model.state_dict(), MODEL_PATH)
    print("✅ Modelo y clases guardados correctamente.")
    
except Exception as e:
    print(f"❌ Error durante el entrenamiento: {e}")
    print("💡 Verifica que las imágenes en dataset_augmented sean válidas")
    
    # Crear modelo básico para evitar errores
    clases = []
    with open(CLASES_PATH, "wb") as f:
        pickle.dump(clases, f)
    
    model = CNNClasificador(num_classes=0)
    torch.save(model.state_dict(), MODEL_PATH)
    print("✅ Modelo básico creado para evitar errores")
