import torch
import pickle

# Suponiendo que ya tienes el modelo entrenado como `model`
# Guarda los pesos
torch.save(model.state_dict(), "cnn_model.pth")

# Guarda las clases (etiquetas) si las tienes como `dataset.classes`
with open("clases.pkl", "wb") as f:
    pickle.dump(dataset.classes, f)

print("✅ Modelo y clases guardados.")
