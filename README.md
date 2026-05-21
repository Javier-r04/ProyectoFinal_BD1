# Proyecto Final - Base de Datos I
## Sistema de Tarjetas de Circulación Vehicular (SAT - Guatemala)

**Autor:** José Javier Rodríguez Alvarado - 1535524
**Curso:** Base de Datos I
**Docente:** Ing. Manuel Rojas
**Universidad Rafael Landívar** - Campus San Alberto Hurtado, S.J. (Quetzaltenango)

---

## Descripción

Aplicación cliente-servidor que simula el sistema de tarjetas de circulación
vehicular de la SAT de Guatemala. Permite consultar, registrar, modificar
y desactivar tarjetas, así como llevar el control de cambios de dueño,
cambios de color y cambios de motor de los vehículos.

---

## Tecnologías utilizadas

| Capa        | Tecnología                       |
|-------------|----------------------------------|
| Base de datos | PostgreSQL 16 (en Docker)      |
| Backend     | Python 3.11+ con Flask           |
| Driver BD   | psycopg2-binary                  |
| Frontend    | HTML5 + CSS3 + JavaScript (vanilla) |
| Orquestación| Docker + Docker Compose          |
| IDE BD      | DataGrip                         |

---

##  Estructura del repositorio

```
proyecto_bd1/
├── database/
│   ├── schema.sql            ← Estructura de tablas, índices y vista
│   ├── inserts.sql           ← Datos de prueba
│   └── consultas_demo.sql    ← Consultas SQL para la demostración
├── backend/
│   ├── app.py                ← API REST (Flask)
│   ├── db.py                 ← Módulo de conexión PostgreSQL
│   ├── requirements.txt      ← Dependencias Python
│   └── .env.example          ← Plantilla de variables de entorno
├── frontend/
│   ├── index.html            ← Interfaz web
│   ├── styles.css
│   └── app.js
├── docs/
│   ├── modelo_er.md          ← Modelo Entidad-Relación
│   └── modelo_relacional.md  ← Modelo relacional
├── docker-compose.yml        ← Levanta PostgreSQL en Docker
└── README.md
```

---

##  Instalación y ejecución

###  Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python 3.11+](https://www.python.org/)
- [DataGrip](https://www.jetbrains.com/datagrip/) (opcional, para administrar la BD)

###  Levantar la base de datos en Docker

Desde la raíz del proyecto:

```bash
docker compose up -d
```

Esto crea y arranca un contenedor PostgreSQL llamado **bd1_postgres** que:
- Escucha en el puerto **5432**.
- Crea la base de datos **`tarjetas_circulacion`** automáticamente.
- Ejecuta `schema.sql` e `inserts.sql` al iniciar.

Verificar que esté corriendo:
```bash
docker ps
```

###  Conectarse desde DataGrip

1. **New → Data Source → PostgreSQL**
2. Llenar los datos:
   - Host: `localhost`
   - Port: `5432`
   - Database: `tarjetas_circulacion`
   - User: `postgres`
   - Password: `postgres`
3. Probar la conexión y aplicar.

> Si la BD no tiene datos, ejecuta manualmente `database/schema.sql` y
> luego `database/inserts.sql` desde DataGrip.

###  Levantar el backend (Python + Flask)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env       # editar si fuera necesario
python app.py
```

El servidor queda escuchando en `http://localhost:5000`.

###  Abrir la aplicación

Abrir el navegador en:

```
http://localhost:5000
```

(Flask sirve también el frontend que está en la carpeta `frontend/`).

---

##  Credenciales y configuración

| Parámetro       | Valor                  |
|-----------------|------------------------|
| Host BD         | `localhost`            |
| Puerto BD       | `5432`                 |
| Base de datos   | `tarjetas_circulacion` |
| Usuario BD      | `postgres`             |
| Contraseña BD   | `postgres`             |
| Puerto backend  | `5000`                 |

> Las credenciales se cargan desde `backend/.env`. Editarlo si se necesita
> cambiar host, puerto u otra variable.

---

##  Funcionalidades de la aplicación

-  **Dashboard** con estadísticas en tiempo real.
-  **Consultar** tarjetas de circulación por placa, propietario, DPI o chasis.
-  **Filtrar** por estado (Activa / Vencida / Desactivada / Impago).
-  **Registrar** una nueva tarjeta (crea el vehículo, asigna propietario,
  emite calcomanía).
-  **Modificar** información de un vehículo.
-  **Cambio de dueño** con histórico.
-  **Cambio de color** con histórico.
-  **Cambio de motor** con histórico.
-  **Desactivar tarjeta** por vencimiento o impago.
-  **Vista detallada** con historial completo de cada vehículo.

---

##  Correcciones respecto a la Fase 1

1. **Eliminación de la entidad `Placa`** – Sus atributos (`numero_placa`,
   `tipo_placa`) se trasladaron como columnas de la entidad `Vehiculo`,
   ya que cada vehículo posee exactamente una placa y no había información
   independiente que justificara una entidad separada.
2. **Relación Propietario ↔ Vehículo de muchos a muchos** mediante la
   tabla intermedia `vehiculo_propietario`, la cual además permite llevar
   el histórico de cambios de dueño.
3. **Nuevas tablas auxiliares** para registrar el histórico de cambios:
   `historial_cambio_color` e `historial_cambio_motor`.
4. **Restricciones de integridad** con CHECK constraints en años, DPI,
   tipos de placa y estados de las tarjetas.
5. **Vista unificada** `v_tarjeta_completa` que evita escribir los joins
   repetidamente en cada consulta.

---

##  Demostración en PostgreSQL

El archivo `database/consultas_demo.sql` contiene ejemplos de:

- `SELECT` simples y con filtros.
- `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`, `FULL JOIN`.
- `INSERT` de propietarios, vehículos y tarjetas.
- `UPDATE` para cambio de color, desactivación de tarjetas.
- Cambio de dueño con transacción (2 sentencias).
- Agregaciones (`COUNT`, `GROUP BY`).
- Demostración de integridad referencial con PK/FK.
- Uso de la vista `v_tarjeta_completa`.

Ejecutar en DataGrip o `psql`:

```bash
psql -h localhost -U postgres -d tarjetas_circulacion -f database/consultas_demo.sql
```

---

##  Solución de problemas

| Problema | Solución |
|----------|----------|
| El backend no conecta | Verificar que Docker esté corriendo: `docker ps` |
| Puerto 5432 ocupado | Cambiar el puerto en `docker-compose.yml` |
| Cambios en `schema.sql` no se aplican | `docker compose down -v && docker compose up -d` |
| psycopg2 no instala | En Linux/Mac: `pip install psycopg2-binary` |
| El frontend no carga | Verificar que el backend esté corriendo en el puerto 5000 |

---

##  Reset completo de la base de datos

```bash
docker compose down -v
docker compose up -d
```

Esto borra el volumen, recrea el contenedor y vuelve a ejecutar
`schema.sql` + `inserts.sql` desde cero.
