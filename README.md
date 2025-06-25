# Sistema de Reconocimiento Facial - Gestión de Asistencias

Sistema completo de reconocimiento facial para gestión de asistencias en salones de clase, desarrollado con FastAPI, PyTorch y MySQL.

## 🚀 Características

- **Reconocimiento Facial**: Modelo CNN ligero entrenado con PyTorch
- **Gestión de Alumnos**: Registro con fotos y datos personales
- **Sesiones de Asistencia**: Crear, gestionar y finalizar sesiones
- **Reconocimiento Automático**: Pasar asistencia con reconocimiento facial
- **Reportes**: Generar reportes detallados de asistencia
- **API REST**: Endpoints completos para integración con frontend

## 🛠️ Tecnologías

- **Backend**: FastAPI (Python 3.13+)
- **IA/ML**: PyTorch, torchvision
- **Base de Datos**: MySQL
- **Procesamiento de Imágenes**: Pillow
- **Despliegue**: Docker, Railway

## 📁 Estructura del Proyecto

```
Percepcion1314/
├── main.py                 # API FastAPI principal
├── entrenar_modelo.py      # Script de entrenamiento del modelo
├── migrar_imagenes.py      # Migración de imágenes
├── test_api.py            # Script de pruebas
├── requirements.txt       # Dependencias Python
├── Dockerfile            # Configuración Docker
├── dataset_augmented/    # Dataset con imágenes por alumno
├── rostros/              # Imágenes originales
├── modelo_reconocimiento.pth  # Modelo entrenado
├── clases_modelo.json    # Clases del modelo
└── README.md
```

## 🔧 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd Percepcion1314
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar base de datos
Crear una base de datos MySQL y configurar las variables de entorno:
```bash
export MYSQLUSER=tu_usuario
export MYSQLPASSWORD=tu_password
export MYSQLHOST=localhost
export MYSQLPORT=3306
export MYSQLDATABASE=asistencias_db
```

### 4. Migrar imágenes existentes
```bash
python migrar_imagenes.py
```

### 5. Entrenar modelo inicial
```bash
python entrenar_modelo.py
```

### 6. Ejecutar la aplicación
```bash
python main.py
```

## 📡 Endpoints de la API

### Gestión de Alumnos
- `POST /alumnos` - Registrar nuevo alumno
- `GET /alumnos` - Listar todos los alumnos

### Gestión de Sesiones
- `POST /crear-sesion` - Crear nueva sesión
- `GET /listar-sesiones` - Listar todas las sesiones
- `POST /finalizar-sesion/{sesion_id}` - Finalizar sesión

### Reconocimiento Facial
- `POST /asistencia/{sesion_id}` - Pasar asistencia con foto

### Reportes
- `GET /reporte-asistencia/{sesion_id}` - Generar reporte de asistencia

### Utilidades
- `GET /` - Endpoint raíz
- `DELETE /reiniciar_datos` - Reiniciar base de datos

## 🔄 Flujo de Trabajo

### 1. Registrar Alumnos
```bash
curl -X POST "http://localhost:8000/alumnos" \
  -F "nombre=Juan" \
  -F "apellido=Pérez" \
  -F "codigo=2024001" \
  -F "correo=juan.perez@email.com" \
  -F "foto=@foto.jpg"
```

### 2. Crear Sesión
```bash
curl -X POST "http://localhost:8000/crear-sesion" \
  -F "nombre=Clase de Matemáticas"
```

### 3. Pasar Asistencia
```bash
curl -X POST "http://localhost:8000/asistencia/1" \
  -F "foto=@foto_alumno.jpg"
```

### 4. Generar Reporte
```bash
curl -X GET "http://localhost:8000/reporte-asistencia/1"
```

## 🧪 Pruebas

Ejecutar el script de pruebas:
```bash
python test_api.py
```

## 🐳 Despliegue con Docker

### Construir imagen
```bash
docker build -t sistema-asistencias .
```

### Ejecutar contenedor
```bash
docker run -p 8000:8000 \
  -e MYSQLUSER=tu_usuario \
  -e MYSQLPASSWORD=tu_password \
  -e MYSQLHOST=tu_host \
  -e MYSQLPORT=3306 \
  -e MYSQLDATABASE=asistencias_db \
  sistema-asistencias
```

## 📊 Base de Datos

### Tablas Principales

#### `alumnos`
- `id` (INT, PK)
- `nombre` (VARCHAR)
- `apellido` (VARCHAR)
- `codigo` (VARCHAR, UNIQUE)
- `correo` (VARCHAR)
- `foto` (VARCHAR)
- `fecha_registro` (TIMESTAMP)

#### `sesiones`
- `id` (INT, PK)
- `nombre` (VARCHAR)
- `fecha_inicio` (TIMESTAMP)
- `fecha_fin` (TIMESTAMP)
- `estado` (ENUM: 'activa', 'finalizada')

#### `asistencias`
- `id` (INT, PK)
- `id_sesion` (INT, FK)
- `id_alumno` (INT, FK)
- `estado` (VARCHAR)
- `fecha_hora` (TIMESTAMP)

## 🤖 Modelo de IA

### Arquitectura CNN
- **Entrada**: Imágenes RGB 100x100 píxeles
- **Capas Convolucionales**: 3 capas con ReLU y MaxPooling
- **Capas Densa**: 2 capas fully connected
- **Salida**: Clasificación por alumno

### Entrenamiento
- **Data Augmentation**: Rotación, zoom, brillo, contraste
- **Optimizador**: Adam
- **Función de Pérdida**: CrossEntropyLoss
- **Épocas**: 10 (configurable)

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Base de datos
MYSQLUSER=usuario
MYSQLPASSWORD=password
MYSQLHOST=host
MYSQLPORT=3306
MYSQLDATABASE=nombre_db

# API
HOST=0.0.0.0
PORT=8000
```

### Parámetros del Modelo
- `IMG_SIZE`: Tamaño de imagen (default: 100)
- `BATCH_SIZE`: Tamaño de batch (default: 32)
- `EPOCHS`: Número de épocas (default: 10)
- `LEARNING_RATE`: Tasa de aprendizaje (default: 0.001)

## 🚨 Solución de Problemas

### Error de conexión a MySQL
- Verificar variables de entorno
- Comprobar que MySQL esté ejecutándose
- Verificar credenciales

### Error de modelo no encontrado
- Ejecutar `python entrenar_modelo.py`
- Verificar que existan `modelo_reconocimiento.pth` y `clases_modelo.json`

### Error de reconocimiento
- Verificar calidad de la imagen
- Comprobar que el alumno esté registrado
- Reentrenar modelo si es necesario

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👥 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abrir un Pull Request

## 📞 Soporte

Para soporte técnico o preguntas, contactar al equipo de desarrollo.