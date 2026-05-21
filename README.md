# Sistema de Tarjetas de Circulación Vehicular

Sistema web de gestión de tarjetas de circulación vehicular desarrollado para el curso de **Base de Datos I**, Universidad Rafael Landívar — Campus San Alberto Hurtado, S.J. de Quetzaltenango.

**Autor:** José Javier Rodríguez Alvarado — Carnet 1535524
**Docente:** Ing. Manuel Rojas

---

## Tecnologías utilizadas

| Capa | Tecnología |
|------|------------|
| Backend | Python 3.11+ con Flask |
| Base de datos | PostgreSQL 16 |
| Driver BD | psycopg2-binary |
| Frontend | HTML + CSS + JavaScript (vanilla) |
| Contenedor BD | Docker / Docker Compose |
| IDE BD | DataGrip |

---

## Requisitos previos

- Python 3.11 o superior
- Docker Desktop (para levantar PostgreSQL)
- pip (incluido con Python)
- DataGrip (opcional, para administrar la BD visualmente)

---

## Instrucciones de instalación

```bash
# 1. Clonar el repositorio
git clone <https://github.com/Javier-r04/ProyectoFinal_BD1/tree/main>
cd proyecto_bd1

# 2. Levantar la base de datos con Docker
docker compose up -d

# 3. Instalar dependencias del backend
cd backend
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env       # Windows
cp .env.example .env         # Linux/Mac
```

> El `docker compose up -d` ejecuta automáticamente los scripts `schema.sql` (crea tablas) e `inserts.sql` (carga datos de prueba).

---

## Cómo ejecutar el proyecto

```bash
# Desde la carpeta backend
python app.py
```

El servidor Flask inicia en `http://localhost:5000` y sirve tanto la API REST como el frontend desde la misma URL.

---

## Credenciales

### Base de datos PostgreSQL

| Campo | Valor |
|-------|-------|
| Host | `localhost` |
| Puerto | `5433` |
| Base de datos | `tarjetas_circulacion` |
| Usuario | `postgres` |
| Contraseña | `postgres` |

---

## Puerto utilizado

| Servicio | Puerto |
|----------|--------|
| Aplicación web + API (Flask) | `5000` |
| PostgreSQL (Docker) | `5433` |

> El puerto `5433` se eligió para no chocar con instalaciones nativas de PostgreSQL que usan el `5432` por defecto.

---

## Nombre de la base de datos

```
tarjetas_circulacion
```

---

## Estructura del repositorio

```
proyecto_bd1/
├── database/
│   ├── schema.sql              # Definición de tablas, PK, FK y restricciones
│   ├── inserts.sql             # Datos de prueba
│   └── consultas_demo.sql      # Consultas SQL para la demostración
├── docs/
│   ├── modelo_er.md            # Diagrama Entidad-Relación
│   └── modelo_relacional.md    # Modelo relacional
├── backend/                    # Servidor Flask
│   ├── app.py                  # Endpoints REST de la API
│   ├── db.py                   # Módulo de conexión a PostgreSQL
│   ├── requirements.txt        # Dependencias Python
│   └── .env.example            # Plantilla de variables de entorno
├── frontend/                   # Cliente web (SPA vanilla JS)
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── docker-compose.yml
├── iniciar.bat                 # Script de arranque rápido (Windows)
├── iniciar.sh                  # Script de arranque rápido (Linux/Mac)
└── README.md
```

---

## Funcionalidades principales

### Gestión de catálogos
- Registro de **marcas** de vehículos
- Registro de **modelos** (con creación de marca al vuelo si no existe)
- Catálogo de **tipos de uso** (Particular, Comercial, Mercantil, Oficial, etc.)

### Gestión de propietarios
- Registro de nuevos propietarios con validación de DPI (13 dígitos, único)
- Listado y búsqueda

### Gestión de vehículos
- Registro de nuevos vehículos con asignación de propietario
- Validación de placa, motor y chasis únicos
- Consulta unificada por placa, marca, modelo, color, motor, chasis, propietario o DPI
- Soporte para vehículos sin propietario y sin tarjeta (recién registrados)

### Tarjetas de circulación
- Emisión de nueva tarjeta con vigencia de 3 años
- Consulta detallada con información completa del vehículo y propietario
- Desactivación por **vencimiento** o **impago**
- Histórico completo de tarjetas por vehículo

### Trámites (con histórico automático)
- **Cambio de color**: actualiza el vehículo, registra el cambio en histórico, desactiva la tarjeta actual y emite una nueva
- **Cambio de motor**: mismo flujo aplicado al número de motor
- **Cambio de dueño**: cierra la relación de propietario actual, registra al nuevo y emite tarjeta nueva
- Cada cambio se guarda con fecha y observaciones

### Calcomanías
- Registro anual con estados: VIGENTE, VENCIDA, ANULADA

### Dashboard
- Estadísticas en tiempo real: vehículos, propietarios, tarjetas activas/vencidas/desactivadas
- Vista de tarjetas recientes

---

## Endpoints principales de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/health` | Verificar conexión a BD |
| `GET` | `/api/estadisticas` | Estadísticas del dashboard |
| `GET` | `/api/marcas` | Listar marcas |
| `POST` | `/api/marcas` | Crear marca |
| `GET` | `/api/modelos` | Listar modelos con su marca |
| `POST` | `/api/modelos` | Crear modelo (acepta marca nueva o existente) |
| `GET` | `/api/propietarios` | Listar propietarios |
| `POST` | `/api/propietarios` | Crear propietario |
| `GET` | `/api/vehiculos` | Listar vehículos (con búsqueda) |
| `POST` | `/api/vehiculos` | Crear vehículo + asignar propietario |
| `PUT` | `/api/vehiculos/<id>` | Modificar vehículo |
| `POST` | `/api/vehiculos/<id>/cambio-color` | Trámite de cambio de color |
| `POST` | `/api/vehiculos/<id>/cambio-motor` | Trámite de cambio de motor |
| `POST` | `/api/vehiculos/<id>/cambio-dueno` | Trámite de cambio de dueño |
| `GET` | `/api/vehiculos/<id>/historial` | Historial completo del vehículo |
| `GET` | `/api/tarjetas` | Listar/buscar tarjetas y vehículos |
| `POST` | `/api/tarjetas` | Crear tarjeta de circulación |
| `POST` | `/api/tarjetas/<id>/desactivar` | Desactivar por vencimiento o impago |
| `GET` | `/api/calcomanias` | Listar calcomanías |
| `POST` | `/api/calcomanias` | Crear calcomanía |

---

## Variables de entorno (`.env`)

```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=tarjetas_circulacion
DB_USER=postgres
DB_PASSWORD=postgres
FLASK_PORT=5000
```

---

