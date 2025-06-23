FROM python:3.12-slim

# Instala dependencias del sistema necesarias para OpenCV y otras librerías
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de dependencias
COPY requirements.txt ./

# Instala las dependencias de Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia el resto del código
COPY . .

# Expone el puerto (opcional, Railway lo maneja automáticamente)
EXPOSE 8000

# Comando para iniciar el servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 