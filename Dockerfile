FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

USER root

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-python-dev \
    libboost-thread-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# No es necesario start.sh, la imagen base ya ejecuta Uvicorn correctamente
# El puerto 80 es el predeterminado en la imagen base
EXPOSE 80