"""
Servidor Flask - API REST para gestión de tarjetas de circulación.
Proyecto Final - Base de Datos I
Autor: José Javier Rodríguez Alvarado - 1535524
"""
import os
from datetime import date
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

import db

load_dotenv()

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)


# =====================================================================
# Frontend (sirve index.html)
# =====================================================================
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


# =====================================================================
# Health check
# =====================================================================
@app.route("/api/health")
def health():
    try:
        db.query_one("SELECT 1 AS ok")
        return jsonify({"status": "ok", "db": "connected"})
    except Exception as e:
        return jsonify({"status": "error", "db": str(e)}), 500


# =====================================================================
# CATÁLOGOS (para llenar combos del frontend)
# =====================================================================
@app.route("/api/marcas")
def listar_marcas():
    return jsonify(db.query_all("SELECT * FROM marca ORDER BY nombre_marca"))


@app.route("/api/marcas", methods=["POST"])
def crear_marca():
    """Body: { nombre_marca: 'Volkswagen' }"""
    data = request.get_json() or {}
    nombre = (data.get("nombre_marca") or "").strip()
    if not nombre:
        return jsonify({"error": "nombre_marca es requerido"}), 400
    try:
        nueva = db.execute(
            "INSERT INTO marca (nombre_marca) VALUES (%s) RETURNING id_marca",
            (nombre,), returning=True,
        )
        return jsonify({"ok": True, "id_marca": nueva["id_marca"]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/modelos")
def listar_modelos():
    sql = """
        SELECT mo.id_modelo, mo.nombre_modelo, mo.id_marca, ma.nombre_marca
        FROM modelo mo
        INNER JOIN marca ma ON mo.id_marca = ma.id_marca
        ORDER BY ma.nombre_marca, mo.nombre_modelo
    """
    return jsonify(db.query_all(sql))


@app.route("/api/modelos", methods=["POST"])
def crear_modelo():
    """
    Body: { nombre_modelo: 'Jetta', id_marca: 11 }
    O para crear marca y modelo al mismo tiempo:
           { nombre_modelo: 'Jetta', nombre_marca: 'Volkswagen' }
    """
    data = request.get_json() or {}
    nombre_modelo = (data.get("nombre_modelo") or "").strip()
    id_marca = data.get("id_marca")
    nombre_marca = (data.get("nombre_marca") or "").strip()

    if not nombre_modelo:
        return jsonify({"error": "nombre_modelo es requerido"}), 400
    if not id_marca and not nombre_marca:
        return jsonify({"error": "id_marca o nombre_marca es requerido"}), 400

    try:
        # Si dieron nombre_marca pero no id_marca, crear (o reutilizar) la marca
        if not id_marca:
            existente = db.query_one(
                "SELECT id_marca FROM marca WHERE LOWER(nombre_marca) = LOWER(%s)",
                (nombre_marca,),
            )
            if existente:
                id_marca = existente["id_marca"]
            else:
                creada = db.execute(
                    "INSERT INTO marca (nombre_marca) VALUES (%s) RETURNING id_marca",
                    (nombre_marca,), returning=True,
                )
                id_marca = creada["id_marca"]

        nuevo = db.execute(
            """INSERT INTO modelo (nombre_modelo, id_marca)
               VALUES (%s, %s) RETURNING id_modelo""",
            (nombre_modelo, id_marca), returning=True,
        )
        return jsonify({
            "ok": True,
            "id_modelo": nuevo["id_modelo"],
            "id_marca": id_marca,
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/tipos-uso")
def listar_tipos_uso():
    return jsonify(db.query_all("SELECT * FROM tipo_uso ORDER BY descripcion"))


@app.route("/api/propietarios")
def listar_propietarios():
    return jsonify(db.query_all(
        "SELECT * FROM propietario ORDER BY nombre"
    ))


@app.route("/api/usuarios")
def listar_usuarios():
    return jsonify(db.query_all("SELECT * FROM usuario ORDER BY nombre"))


# =====================================================================
# CRUD: PROPIETARIOS
# =====================================================================
@app.route("/api/propietarios", methods=["POST"])
def crear_propietario():
    """Registrar un nuevo propietario."""
    data = request.get_json() or {}
    try:
        nuevo = db.execute(
            """
            INSERT INTO propietario (nombre, dpi, direccion, telefono)
            VALUES (%s, %s, %s, %s)
            RETURNING id_propietario
            """,
            (data["nombre"], data["dpi"],
             data.get("direccion", ""), data.get("telefono", "")),
            returning=True,
        )
        return jsonify({"ok": True, "id_propietario": nuevo["id_propietario"]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# =====================================================================
# CRUD: VEHÍCULOS (crear un vehículo y asignar propietario)
# =====================================================================
@app.route("/api/vehiculos", methods=["GET"])
def listar_vehiculos():
    busqueda = request.args.get("q", "").strip()

    sql = """
        SELECT v.id_vehiculo, v.numero_placa, v.tipo_placa, v.anio, v.color,
               v.numero_motor, v.numero_chasis,
               ma.nombre_marca, mo.nombre_modelo, tu.descripcion AS tipo_uso,
               p.nombre AS propietario_actual,
               p.dpi AS dpi_propietario,
               (SELECT COUNT(*) FROM tarjeta_circulacion t
                WHERE t.id_vehiculo = v.id_vehiculo AND t.estado = 'ACTIVA') AS tiene_tarjeta_activa
        FROM vehiculo v
        INNER JOIN modelo mo ON v.id_modelo = mo.id_modelo
        INNER JOIN marca ma  ON mo.id_marca = ma.id_marca
        INNER JOIN tipo_uso tu ON v.id_tipo_uso = tu.id_tipo_uso
        LEFT JOIN vehiculo_propietario vp
               ON vp.id_vehiculo = v.id_vehiculo AND vp.es_actual = TRUE
        LEFT JOIN propietario p ON vp.id_propietario = p.id_propietario
    """
    params = []
    if busqueda:
        sql += """ WHERE v.numero_placa ILIKE %s
                       OR v.color ILIKE %s
                       OR v.numero_motor ILIKE %s
                       OR v.numero_chasis ILIKE %s
                       OR mo.nombre_modelo ILIKE %s
                       OR ma.nombre_marca ILIKE %s """
        like = f"%{busqueda}%"
        params = [like, like, like, like, like, like]
    sql += " ORDER BY v.id_vehiculo DESC"
    return jsonify(db.query_all(sql, params))


@app.route("/api/vehiculos", methods=["POST"])
def crear_vehiculo():
    """
    Registrar un vehículo nuevo y asignarle propietario.
    Body: { vehiculo: {...}, id_propietario: N }
    """
    data = request.get_json() or {}
    veh = data.get("vehiculo", {})
    id_prop = data.get("id_propietario")
    if not id_prop:
        return jsonify({"error": "id_propietario es requerido"}), 400

    try:
        inserted = db.execute(
            """
            INSERT INTO vehiculo
                (anio, color, numero_motor, numero_chasis,
                 numero_placa, tipo_placa, id_modelo, id_tipo_uso)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id_vehiculo
            """,
            (
                veh["anio"], veh["color"], veh["numero_motor"],
                veh["numero_chasis"], veh["numero_placa"], veh["tipo_placa"],
                veh["id_modelo"], veh["id_tipo_uso"],
            ),
            returning=True,
        )
        id_vehiculo = inserted["id_vehiculo"]

        # Asignar propietario
        db.execute(
            """
            INSERT INTO vehiculo_propietario
                (id_vehiculo, id_propietario, fecha_inicio, es_actual)
            VALUES (%s, %s, CURRENT_DATE, TRUE)
            """,
            (id_vehiculo, id_prop),
        )
        return jsonify({"ok": True, "id_vehiculo": id_vehiculo}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# =====================================================================
# CRUD: CALCOMANÍAS
# =====================================================================
@app.route("/api/calcomanias", methods=["GET"])
def listar_calcomanias():
    sql = """
        SELECT c.id_calcomania, c.anio, c.estado,
               v.numero_placa, v.id_vehiculo
        FROM calcomania c
        INNER JOIN vehiculo v ON c.id_vehiculo = v.id_vehiculo
        ORDER BY c.id_calcomania DESC
    """
    return jsonify(db.query_all(sql))


@app.route("/api/calcomanias", methods=["POST"])
def crear_calcomania():
    """
    Body: { id_vehiculo: N, anio: 2026, estado: 'VIGENTE' }
    """
    data = request.get_json() or {}
    try:
        nuevo = db.execute(
            """
            INSERT INTO calcomania (anio, estado, id_vehiculo)
            VALUES (%s, %s, %s)
            RETURNING id_calcomania
            """,
            (data["anio"], data.get("estado", "VIGENTE"), data["id_vehiculo"]),
            returning=True,
        )
        return jsonify({"ok": True, "id_calcomania": nuevo["id_calcomania"]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# =====================================================================
# TARJETAS DE CIRCULACIÓN
# =====================================================================
@app.route("/api/tarjetas")
def listar_tarjetas():
    """
    Lista vehículos con o sin tarjeta de circulación.
    Permite filtrar por placa, propietario, DPI, chasis, motor, marca, modelo, color.
    Si estado='SIN_TARJETA', solo muestra vehículos sin ninguna tarjeta.
    """
    estado = request.args.get("estado")
    busqueda = (request.args.get("q") or "").strip()

    # Consulta principal: parte del vehículo (LEFT JOIN con tarjeta para
    # poder mostrar también vehículos sin tarjeta).
    sql = """
        SELECT
            v.id_vehiculo,
            v.numero_placa,
            v.tipo_placa,
            v.anio,
            v.color,
            v.numero_motor,
            v.numero_chasis,
            ma.nombre_marca,
            mo.nombre_modelo,
            tu.descripcion AS tipo_uso,
            t.id_tarjeta,
            t.fecha_emision,
            t.fecha_vencimiento,
            t.estado AS estado_tarjeta,
            t.motivo_desactivacion,
            p.id_propietario,
            p.nombre AS nombre_propietario,
            p.dpi AS dpi_propietario,
            p.direccion AS direccion_propietario,
            p.telefono AS telefono_propietario,
            u.nombre AS nombre_usuario_sat,
            u.dpi AS dpi_usuario_sat,
            u.licencia
        FROM vehiculo v
        INNER JOIN modelo mo   ON v.id_modelo   = mo.id_modelo
        INNER JOIN marca ma    ON mo.id_marca   = ma.id_marca
        INNER JOIN tipo_uso tu ON v.id_tipo_uso = tu.id_tipo_uso
        LEFT JOIN vehiculo_propietario vp
               ON vp.id_vehiculo = v.id_vehiculo AND vp.es_actual = TRUE
        LEFT JOIN propietario p ON vp.id_propietario = p.id_propietario
        LEFT JOIN LATERAL (
            SELECT *
            FROM tarjeta_circulacion tc
            WHERE tc.id_vehiculo = v.id_vehiculo
            ORDER BY tc.id_tarjeta DESC
            LIMIT 1
        ) t ON TRUE
        LEFT JOIN usuario u ON t.id_usuario = u.id_usuario
        WHERE 1=1
    """
    params = []

    if busqueda:
        sql += """ AND (v.numero_placa     ILIKE %s
                    OR  v.numero_chasis    ILIKE %s
                    OR  v.numero_motor     ILIKE %s
                    OR  v.color            ILIKE %s
                    OR  ma.nombre_marca    ILIKE %s
                    OR  mo.nombre_modelo   ILIKE %s
                    OR  p.nombre           ILIKE %s
                    OR  p.dpi              ILIKE %s) """
        like = f"%{busqueda}%"
        params.extend([like] * 8)

    if estado == "SIN_TARJETA":
        sql += " AND t.id_tarjeta IS NULL "
    elif estado:
        sql += " AND t.estado = %s "
        params.append(estado)

    sql += " ORDER BY v.id_vehiculo DESC"
    return jsonify(db.query_all(sql, params))


@app.route("/api/tarjetas/<int:id_tarjeta>")
def obtener_tarjeta(id_tarjeta):
    row = db.query_one(
        "SELECT * FROM v_tarjeta_completa WHERE id_tarjeta = %s",
        (id_tarjeta,)
    )
    if not row:
        return jsonify({"error": "Tarjeta no encontrada"}), 404
    return jsonify(row)


@app.route("/api/tarjetas/buscar-por-placa/<placa>")
def buscar_por_placa(placa):
    rows = db.query_all(
        "SELECT * FROM v_tarjeta_completa WHERE numero_placa ILIKE %s",
        (f"%{placa}%",)
    )
    return jsonify(rows)


@app.route("/api/tarjetas", methods=["POST"])
def crear_tarjeta():
    """
    Registra una nueva tarjeta de circulación.
    Si el vehículo no existe, lo crea junto con el propietario.
    Body esperado:
        {
          "vehiculo": {...},
          "id_propietario": 1,
          "id_usuario": 1,
          "fecha_emision": "2026-05-17",
          "fecha_vencimiento": "2029-05-17"
        }
    """
    data = request.get_json() or {}

    try:
        # 1. Crear o reutilizar vehículo
        veh = data.get("vehiculo", {})
        id_vehiculo = veh.get("id_vehiculo")
        if not id_vehiculo:
            inserted = db.execute(
                """
                INSERT INTO vehiculo
                    (anio, color, numero_motor, numero_chasis,
                     numero_placa, tipo_placa, id_modelo, id_tipo_uso)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id_vehiculo
                """,
                (
                    veh["anio"], veh["color"], veh["numero_motor"],
                    veh["numero_chasis"], veh["numero_placa"], veh["tipo_placa"],
                    veh["id_modelo"], veh["id_tipo_uso"],
                ),
                returning=True,
            )
            id_vehiculo = inserted["id_vehiculo"]

            # Asociar propietario
            db.execute(
                """
                INSERT INTO vehiculo_propietario
                    (id_vehiculo, id_propietario, fecha_inicio, es_actual)
                VALUES (%s, %s, CURRENT_DATE, TRUE)
                """,
                (id_vehiculo, data["id_propietario"]),
            )

            # Calcomanía automática para el año actual
            db.execute(
                """
                INSERT INTO calcomania (anio, estado, id_vehiculo)
                VALUES (EXTRACT(YEAR FROM CURRENT_DATE)::INT, 'VIGENTE', %s)
                """,
                (id_vehiculo,),
            )

        # 2. Crear la tarjeta de circulación
        nueva = db.execute(
            """
            INSERT INTO tarjeta_circulacion
                (fecha_emision, fecha_vencimiento, estado,
                 id_vehiculo, id_usuario)
            VALUES (%s, %s, 'ACTIVA', %s, %s)
            RETURNING id_tarjeta
            """,
            (
                data["fecha_emision"], data["fecha_vencimiento"],
                id_vehiculo, data["id_usuario"],
            ),
            returning=True,
        )
        return jsonify({"ok": True, "id_tarjeta": nueva["id_tarjeta"]}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# =====================================================================
# VEHÍCULOS - Modificación
# =====================================================================
@app.route("/api/vehiculos/<int:id_vehiculo>", methods=["PUT"])
def modificar_vehiculo(id_vehiculo):
    """Modificación general de un vehículo."""
    data = request.get_json() or {}
    campos_validos = ["color", "numero_motor", "numero_chasis",
                      "numero_placa", "tipo_placa", "id_modelo",
                      "id_tipo_uso", "anio"]
    set_clauses, params = [], []
    for c in campos_validos:
        if c in data:
            set_clauses.append(f"{c} = %s")
            params.append(data[c])
    if not set_clauses:
        return jsonify({"error": "Sin campos para actualizar"}), 400

    params.append(id_vehiculo)
    try:
        db.execute(
            f"UPDATE vehiculo SET {', '.join(set_clauses)} WHERE id_vehiculo = %s",
            params,
        )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# =====================================================================
# CAMBIO DE COLOR (desactiva tarjeta actual y emite una nueva)
# =====================================================================
@app.route("/api/vehiculos/<int:id_vehiculo>/cambio-color", methods=["POST"])
def cambio_color(id_vehiculo):
    data = request.get_json() or {}
    nuevo = data.get("color_nuevo")
    obs   = data.get("observaciones", "")
    if not nuevo:
        return jsonify({"error": "color_nuevo es requerido"}), 400

    actual = db.query_one(
        "SELECT color FROM vehiculo WHERE id_vehiculo = %s",
        (id_vehiculo,),
    )
    if not actual:
        return jsonify({"error": "Vehículo no encontrado"}), 404

    # Buscar la tarjeta activa actual (si existe)
    tarjeta_actual = db.query_one(
        """SELECT id_tarjeta, id_usuario FROM tarjeta_circulacion
           WHERE id_vehiculo = %s AND estado = 'ACTIVA'
           ORDER BY id_tarjeta DESC LIMIT 1""",
        (id_vehiculo,),
    )

    try:
        operaciones = [
            # 1) Guardar histórico de cambio
            (
                """INSERT INTO historial_cambio_color
                       (id_vehiculo, color_anterior, color_nuevo, observaciones)
                   VALUES (%s, %s, %s, %s)""",
                (id_vehiculo, actual["color"], nuevo, obs),
            ),
            # 2) Actualizar color del vehículo
            (
                "UPDATE vehiculo SET color = %s WHERE id_vehiculo = %s",
                (nuevo, id_vehiculo),
            ),
        ]
        nueva_tarjeta_info = None

        if tarjeta_actual:
            # 3) Desactivar tarjeta actual
            operaciones.append((
                """UPDATE tarjeta_circulacion
                       SET estado = 'DESACTIVADA',
                           motivo_desactivacion = %s
                   WHERE id_tarjeta = %s""",
                (f"Cambio de color de {actual['color']} a {nuevo}",
                 tarjeta_actual["id_tarjeta"]),
            ))
            # 4) Emitir nueva tarjeta
            operaciones.append((
                """INSERT INTO tarjeta_circulacion
                       (fecha_emision, fecha_vencimiento, estado,
                        id_vehiculo, id_usuario)
                   VALUES (CURRENT_DATE,
                           CURRENT_DATE + INTERVAL '3 years',
                           'ACTIVA', %s, %s)""",
                (id_vehiculo, tarjeta_actual["id_usuario"]),
            ))
            nueva_tarjeta_info = "Se emitió una nueva tarjeta de circulación"

        db.execute_many(operaciones)
        return jsonify({
            "ok": True,
            "color_anterior": actual["color"],
            "color_nuevo": nuevo,
            "tarjeta": nueva_tarjeta_info,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# =====================================================================
# CAMBIO DE MOTOR (desactiva tarjeta actual y emite una nueva)
# =====================================================================
@app.route("/api/vehiculos/<int:id_vehiculo>/cambio-motor", methods=["POST"])
def cambio_motor(id_vehiculo):
    data = request.get_json() or {}
    nuevo = data.get("motor_nuevo")
    obs   = data.get("observaciones", "")
    if not nuevo:
        return jsonify({"error": "motor_nuevo es requerido"}), 400

    actual = db.query_one(
        "SELECT numero_motor FROM vehiculo WHERE id_vehiculo = %s",
        (id_vehiculo,),
    )
    if not actual:
        return jsonify({"error": "Vehículo no encontrado"}), 404

    tarjeta_actual = db.query_one(
        """SELECT id_tarjeta, id_usuario FROM tarjeta_circulacion
           WHERE id_vehiculo = %s AND estado = 'ACTIVA'
           ORDER BY id_tarjeta DESC LIMIT 1""",
        (id_vehiculo,),
    )

    try:
        operaciones = [
            (
                """INSERT INTO historial_cambio_motor
                       (id_vehiculo, motor_anterior, motor_nuevo, observaciones)
                   VALUES (%s, %s, %s, %s)""",
                (id_vehiculo, actual["numero_motor"], nuevo, obs),
            ),
            (
                "UPDATE vehiculo SET numero_motor = %s WHERE id_vehiculo = %s",
                (nuevo, id_vehiculo),
            ),
        ]
        nueva_tarjeta_info = None

        if tarjeta_actual:
            operaciones.append((
                """UPDATE tarjeta_circulacion
                       SET estado = 'DESACTIVADA',
                           motivo_desactivacion = %s
                   WHERE id_tarjeta = %s""",
                (f"Cambio de motor: {actual['numero_motor']} a {nuevo}",
                 tarjeta_actual["id_tarjeta"]),
            ))
            operaciones.append((
                """INSERT INTO tarjeta_circulacion
                       (fecha_emision, fecha_vencimiento, estado,
                        id_vehiculo, id_usuario)
                   VALUES (CURRENT_DATE,
                           CURRENT_DATE + INTERVAL '3 years',
                           'ACTIVA', %s, %s)""",
                (id_vehiculo, tarjeta_actual["id_usuario"]),
            ))
            nueva_tarjeta_info = "Se emitió una nueva tarjeta de circulación"

        db.execute_many(operaciones)
        return jsonify({
            "ok": True,
            "motor_anterior": actual["numero_motor"],
            "motor_nuevo": nuevo,
            "tarjeta": nueva_tarjeta_info,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# =====================================================================
# CAMBIO DE DUEÑO (desactiva tarjeta actual y emite una nueva)
# =====================================================================
@app.route("/api/vehiculos/<int:id_vehiculo>/cambio-dueno", methods=["POST"])
def cambio_dueno(id_vehiculo):
    """
    Body: { "id_propietario_nuevo": 5 }
    """
    data = request.get_json() or {}
    nuevo_prop = data.get("id_propietario_nuevo")
    if not nuevo_prop:
        return jsonify({"error": "id_propietario_nuevo es requerido"}), 400

    # Buscar propietario actual para guardar nombre en el motivo
    prop_actual = db.query_one(
        """SELECT p.nombre, p.id_propietario
           FROM vehiculo_propietario vp
           INNER JOIN propietario p ON vp.id_propietario = p.id_propietario
           WHERE vp.id_vehiculo = %s AND vp.es_actual = TRUE""",
        (id_vehiculo,),
    )
    prop_nuevo = db.query_one(
        "SELECT nombre FROM propietario WHERE id_propietario = %s",
        (nuevo_prop,),
    )
    if not prop_nuevo:
        return jsonify({"error": "Nuevo propietario no encontrado"}), 404

    tarjeta_actual = db.query_one(
        """SELECT id_tarjeta, id_usuario FROM tarjeta_circulacion
           WHERE id_vehiculo = %s AND estado = 'ACTIVA'
           ORDER BY id_tarjeta DESC LIMIT 1""",
        (id_vehiculo,),
    )

    try:
        operaciones = [
            # 1) Cerrar la relación actual de propietario
            (
                """UPDATE vehiculo_propietario
                       SET es_actual = FALSE, fecha_fin = CURRENT_DATE
                   WHERE id_vehiculo = %s AND es_actual = TRUE""",
                (id_vehiculo,),
            ),
            # 2) Registrar nuevo propietario
            (
                """INSERT INTO vehiculo_propietario
                       (id_vehiculo, id_propietario, fecha_inicio, es_actual)
                   VALUES (%s, %s, CURRENT_DATE, TRUE)""",
                (id_vehiculo, nuevo_prop),
            ),
        ]
        nueva_tarjeta_info = None

        if tarjeta_actual:
            motivo = f"Cambio de dueño: {prop_actual['nombre'] if prop_actual else 'N/A'} a {prop_nuevo['nombre']}"
            operaciones.append((
                """UPDATE tarjeta_circulacion
                       SET estado = 'DESACTIVADA',
                           motivo_desactivacion = %s
                   WHERE id_tarjeta = %s""",
                (motivo, tarjeta_actual["id_tarjeta"]),
            ))
            operaciones.append((
                """INSERT INTO tarjeta_circulacion
                       (fecha_emision, fecha_vencimiento, estado,
                        id_vehiculo, id_usuario)
                   VALUES (CURRENT_DATE,
                           CURRENT_DATE + INTERVAL '3 years',
                           'ACTIVA', %s, %s)""",
                (id_vehiculo, tarjeta_actual["id_usuario"]),
            ))
            nueva_tarjeta_info = "Se emitió una nueva tarjeta de circulación"

        db.execute_many(operaciones)
        return jsonify({
            "ok": True,
            "propietario_anterior": prop_actual["nombre"] if prop_actual else None,
            "propietario_nuevo": prop_nuevo["nombre"],
            "tarjeta": nueva_tarjeta_info,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# =====================================================================
# DESACTIVAR TARJETA (vencimiento / impago)
# =====================================================================
@app.route("/api/tarjetas/<int:id_tarjeta>/desactivar", methods=["POST"])
def desactivar_tarjeta(id_tarjeta):
    """
    Body: { "motivo": "vencimiento" | "impago", "observacion": "..." }
    """
    data = request.get_json() or {}
    motivo = (data.get("motivo") or "").lower()
    obs = data.get("observacion", "")

    if motivo == "vencimiento":
        nuevo_estado = "VENCIDA"
        descripcion = obs or "Desactivada por vencimiento"
    elif motivo == "impago":
        nuevo_estado = "IMPAGO"
        descripcion = obs or "Desactivada por impago"
    else:
        nuevo_estado = "DESACTIVADA"
        descripcion = obs or "Desactivada manualmente"

    try:
        db.execute(
            """UPDATE tarjeta_circulacion
                   SET estado = %s, motivo_desactivacion = %s
               WHERE id_tarjeta = %s""",
            (nuevo_estado, descripcion, id_tarjeta),
        )
        return jsonify({"ok": True, "estado": nuevo_estado})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# =====================================================================
# HISTORIAL COMPLETO DE UN VEHÍCULO
# =====================================================================
@app.route("/api/vehiculos/<int:id_vehiculo>/historial")
def historial_vehiculo(id_vehiculo):
    propietarios = db.query_all(
        """
        SELECT vp.id_vehiculo_propietario, vp.fecha_inicio, vp.fecha_fin,
               vp.es_actual, p.nombre, p.dpi
        FROM vehiculo_propietario vp
        INNER JOIN propietario p ON vp.id_propietario = p.id_propietario
        WHERE vp.id_vehiculo = %s
        ORDER BY vp.fecha_inicio DESC
        """,
        (id_vehiculo,),
    )
    colores = db.query_all(
        """SELECT * FROM historial_cambio_color
           WHERE id_vehiculo = %s
           ORDER BY fecha_cambio DESC""",
        (id_vehiculo,),
    )
    motores = db.query_all(
        """SELECT * FROM historial_cambio_motor
           WHERE id_vehiculo = %s
           ORDER BY fecha_cambio DESC""",
        (id_vehiculo,),
    )
    # Todas las tarjetas (activas y desactivadas) del vehículo
    tarjetas = db.query_all(
        """SELECT t.id_tarjeta, t.fecha_emision, t.fecha_vencimiento,
                  t.estado, t.motivo_desactivacion,
                  u.nombre AS nombre_usuario
           FROM tarjeta_circulacion t
           INNER JOIN usuario u ON t.id_usuario = u.id_usuario
           WHERE t.id_vehiculo = %s
           ORDER BY t.id_tarjeta DESC""",
        (id_vehiculo,),
    )
    return jsonify({
        "propietarios":  propietarios,
        "cambios_color": colores,
        "cambios_motor": motores,
        "tarjetas":      tarjetas,
    })


# =====================================================================
# ESTADÍSTICAS
# =====================================================================
@app.route("/api/estadisticas")
def estadisticas():
    return jsonify({
        "total_vehiculos":     db.query_one("SELECT COUNT(*) AS n FROM vehiculo")["n"],
        "total_propietarios":  db.query_one("SELECT COUNT(*) AS n FROM propietario")["n"],
        "tarjetas_activas":    db.query_one("SELECT COUNT(*) AS n FROM tarjeta_circulacion WHERE estado='ACTIVA'")["n"],
        "tarjetas_vencidas":   db.query_one("SELECT COUNT(*) AS n FROM tarjeta_circulacion WHERE estado='VENCIDA'")["n"],
        "tarjetas_desactiv":   db.query_one("SELECT COUNT(*) AS n FROM tarjeta_circulacion WHERE estado IN ('DESACTIVADA','IMPAGO')")["n"],
    })


# =====================================================================
# Manejo de errores
# =====================================================================
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Recurso no encontrado"}), 404
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", "5000"))
    print(f"\n  Servidor escuchando en http://localhost:{port}")
    print(f"  API health:               http://localhost:{port}/api/health\n")
    app.run(host="0.0.0.0", port=port, debug=True)
