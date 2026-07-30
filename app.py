# app.py
# Aplicación Flask conectada con MongoDB
# Incluye validación, autenticación y auditoría

from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, jsonify, render_template, request
from pymongo.errors import WriteError

from conexion import col_auditoria, col_productos


app = Flask(__name__)


# ---------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------

def doc_a_dict(documento):
    """
    Convierte el ObjectId de MongoDB en texto para poder
    devolver el documento como JSON.
    """
    if documento and "_id" in documento:
        documento["_id"] = str(documento["_id"])

    return documento


def registrar_auditoria(accion, datos):
    """
    Registra una operación en la colección auditoria.
    """
    registro = {
        "accion": accion,
        "fecha": datetime.now(timezone.utc),
        "usuario": "tienda_app",
        "ip": request.remote_addr,
        "resumen": str(datos)[:200]
    }

    col_auditoria.insert_one(registro)


# ---------------------------------------------------------
# PÁGINA PRINCIPAL
# ---------------------------------------------------------

@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/saludo")
def saludo():
    return "Bienvenido al taller de Python + MongoDB"


@app.route("/info")
def info():
    return "Taller Python + MongoDB - Ricaurte Contreras Criado"


# ---------------------------------------------------------
# RUTAS INICIALES DEL TALLER
# ---------------------------------------------------------

@app.route("/insertar")
def insertar():
    producto = {
        "nombre": "Teclado Mecánico",
        "precio": 185000,
        "categoria": "periféricos",
        "stock": 24,
        "activo": True,
        "marca": "Logitech",
        "creado_en": datetime.now(timezone.utc)
    }

    try:
        resultado = col_productos.insert_one(producto)

        registrar_auditoria("INSERT", producto)

        return (
            f"Producto insertado con id: "
            f"{resultado.inserted_id}"
        )

    except WriteError as error:
        return jsonify({
            "error": "El producto no cumple la validación de MongoDB",
            "detalle": str(error)
        }), 400


@app.route("/cargar-datos")
def cargar_datos():
    productos = [
        {
            "nombre": "Mouse Gamer",
            "precio": 95000,
            "categoria": "periféricos",
            "stock": 15,
            "activo": True
        },
        {
            "nombre": "Monitor 27'",
            "precio": 850000,
            "categoria": "pantallas",
            "stock": 8,
            "activo": True
        },
        {
            "nombre": "Webcam HD",
            "precio": 210000,
            "categoria": "periféricos",
            "stock": 10,
            "activo": False
        },
        {
            "nombre": "SSD 1TB",
            "precio": 320000,
            "categoria": "almacenamiento",
            "stock": 20,
            "activo": True
        },
        {
            "nombre": "Auriculares BT",
            "precio": 280000,
            "categoria": "audio",
            "stock": 12,
            "activo": True
        }
    ]

    fecha_actual = datetime.now(timezone.utc)

    for producto in productos:
        producto["creado_en"] = fecha_actual

    try:
        resultado = col_productos.insert_many(productos)

        registrar_auditoria(
            "INSERT_MANY",
            {
                "cantidad": len(resultado.inserted_ids),
                "productos": productos
            }
        )

        return (
            f"Insertados: "
            f"{len(resultado.inserted_ids)} documentos"
        )

    except WriteError as error:
        return jsonify({
            "error": "Uno de los productos no cumple la validación",
            "detalle": str(error)
        }), 400


# ---------------------------------------------------------
# GET: CONSULTAR PRODUCTOS
# ---------------------------------------------------------

@app.route("/api/productos", methods=["GET"])
def get_productos():
    productos = list(col_productos.find())

    productos_convertidos = [
        doc_a_dict(producto)
        for producto in productos
    ]

    return jsonify(productos_convertidos)


@app.route("/api/activos", methods=["GET"])
def get_activos():
    documentos = list(
        col_productos.find({
            "activo": True
        })
    )

    documentos_convertidos = [
        doc_a_dict(documento)
        for documento in documentos
    ]

    return jsonify(documentos_convertidos)


@app.route("/api/productos/caros", methods=["GET"])
def get_caros():
    documentos = list(
        col_productos.find({
            "precio": {
                "$gt": 200000
            }
        })
    )

    documentos_convertidos = [
        doc_a_dict(documento)
        for documento in documentos
    ]

    return jsonify(documentos_convertidos)


@app.route(
    "/api/productos/categoria/<nombre>",
    methods=["GET"]
)
def productos_por_categoria(nombre):
    documentos = list(
        col_productos.find({
            "categoria": {
                "$regex": f"^{nombre}$",
                "$options": "i"
            }
        })
    )

    documentos_convertidos = [
        doc_a_dict(documento)
        for documento in documentos
    ]

    return jsonify(documentos_convertidos)


@app.route("/api/productos/<id>", methods=["GET"])
def get_producto_por_id(id):
    try:
        producto = col_productos.find_one({
            "_id": ObjectId(id)
        })

    except InvalidId:
        return jsonify({
            "error": "El ID ingresado no es válido"
        }), 400

    if producto is None:
        return jsonify({
            "error": "Producto no encontrado"
        }), 404

    return jsonify(doc_a_dict(producto))


# ---------------------------------------------------------
# POST: CREAR PRODUCTO Y REGISTRAR AUDITORÍA
# ---------------------------------------------------------

@app.route("/api/productos", methods=["POST"])
def crear_producto():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or not datos:
        return jsonify({
            "error": "No se recibieron datos JSON válidos"
        }), 400

    nombre = datos.get("nombre")
    precio = datos.get("precio")
    categoria = datos.get("categoria")

    if not isinstance(nombre, str) or len(nombre.strip()) < 2:
        return jsonify({
            "error": "El nombre debe tener mínimo 2 caracteres"
        }), 400

    if (
        isinstance(precio, bool)
        or not isinstance(precio, (int, float))
        or precio <= 0
    ):
        return jsonify({
            "error": "Precio inválido. Debe ser mayor que cero"
        }), 400

    if not isinstance(categoria, str) or not categoria.strip():
        return jsonify({
            "error": "La categoría es obligatoria"
        }), 400

    datos["nombre"] = nombre.strip()
    datos["categoria"] = categoria.strip()
    datos.setdefault("activo", True)
    datos.setdefault("stock", 0)
    datos["creado_en"] = datetime.now(timezone.utc)

    try:
        resultado = col_productos.insert_one(datos)

        registrar_auditoria("INSERT", datos)

        return jsonify({
            "id": str(resultado.inserted_id),
            "mensaje": "Producto creado correctamente"
        }), 201

    except WriteError as error:
        return jsonify({
            "error": "El producto no cumple el esquema de MongoDB",
            "detalle": str(error)
        }), 400


# ---------------------------------------------------------
# PUT: ACTUALIZAR PRODUCTO Y REGISTRAR AUDITORÍA
# ---------------------------------------------------------

@app.route("/api/productos/<id>", methods=["PUT"])
def actualizar_producto(id):
    try:
        id_producto = ObjectId(id)

    except InvalidId:
        return jsonify({
            "error": "El ID ingresado no es válido"
        }), 400

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or not datos:
        return jsonify({
            "error": "No se recibieron datos para actualizar"
        }), 400

    if "precio" in datos:
        precio = datos["precio"]

        if (
            isinstance(precio, bool)
            or not isinstance(precio, (int, float))
            or precio <= 0
        ):
            return jsonify({
                "error": "Precio inválido. Debe ser mayor que cero"
            }), 400

    datos["actualizado_en"] = datetime.now(timezone.utc)

    try:
        resultado = col_productos.update_one(
            {
                "_id": id_producto
            },
            {
                "$set": datos
            }
        )

    except WriteError as error:
        return jsonify({
            "error": "La actualización no cumple el esquema",
            "detalle": str(error)
        }), 400

    if resultado.matched_count == 0:
        return jsonify({
            "error": "Producto no encontrado"
        }), 404

    registrar_auditoria(
        "UPDATE",
        {
            "id": id,
            "cambios": datos
        }
    )

    return jsonify({
        "mensaje": "Producto actualizado correctamente",
        "documentos_modificados": resultado.modified_count
    })


# ---------------------------------------------------------
# RUTA DEL EJERCICIO 9
# ---------------------------------------------------------

@app.route("/actualizar-teclado")
def actualizar_teclado():
    cambios = {
        "precio": 195000,
        "actualizado_en": datetime.now(timezone.utc)
    }

    resultado = col_productos.update_one(
        {
            "nombre": "Teclado Mecánico"
        },
        {
            "$set": cambios
        }
    )

    if resultado.matched_count > 0:
        registrar_auditoria(
            "UPDATE",
            {
                "producto": "Teclado Mecánico",
                "cambios": cambios
            }
        )

    return (
        f"Documentos encontrados: {resultado.matched_count}. "
        f"Documentos actualizados: {resultado.modified_count}"
    )


# ---------------------------------------------------------
# DELETE: ELIMINAR PRODUCTO Y REGISTRAR AUDITORÍA
# ---------------------------------------------------------

@app.route("/api/productos/<id>", methods=["DELETE"])
def eliminar_producto(id):
    try:
        id_producto = ObjectId(id)

    except InvalidId:
        return jsonify({
            "error": "El ID ingresado no es válido"
        }), 400

    producto = col_productos.find_one({
        "_id": id_producto
    })

    if producto is None:
        return jsonify({
            "error": "Producto no encontrado"
        }), 404

    resultado = col_productos.delete_one({
        "_id": id_producto
    })

    if resultado.deleted_count == 1:
        registrar_auditoria(
            "DELETE",
            producto
        )

    return jsonify({
        "mensaje": "Producto eliminado correctamente"
    })


# ---------------------------------------------------------
# GET: CONSULTAR LOS ÚLTIMOS 20 REGISTROS DE AUDITORÍA
# ---------------------------------------------------------

@app.route("/api/auditoria", methods=["GET"])
def get_auditoria():
    documentos = list(
        col_auditoria
        .find()
        .sort("fecha", -1)
        .limit(20)
    )

    documentos_convertidos = [
        doc_a_dict(documento)
        for documento in documentos
    ]

    return jsonify(documentos_convertidos)


# ---------------------------------------------------------
# INICIAR EL SERVIDOR
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=False,
        port=5000
    )