FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# No es necesario start.sh, la imagen base ya ejecuta Uvicorn correctamente
# El puerto 80 es el predeterminado en la imagen base
EXPOSE 80