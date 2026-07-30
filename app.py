# app.py
# Aplicación Flask conectada con MongoDB

from flask import Flask, jsonify, request, render_template
from conexion import col_productos
from bson import ObjectId
from bson.errors import InvalidId


app = Flask(__name__)


# Convierte el ObjectId de MongoDB en texto
# Esto es necesario para mostrar los documentos como JSON
def doc_a_dict(documento):
    documento["_id"] = str(documento["_id"])
    return documento


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/saludo")
def saludo():
    return "Bienvenido al taller de Python + MongoDB"


@app.route("/info")
def info():
    return "Taller Python + MongoDB - Ricaurte Contreras Criado"


# Insertar un producto
@app.route("/insertar")
def insertar():
    producto = {
        "nombre": "Teclado Mecánico",
        "precio": 185000,
        "categoria": "periféricos",
        "stock": 24,
        "activo": True,
        "marca": "Logitech"
    }

    resultado = col_productos.insert_one(producto)

    return f"Producto insertado con id: {resultado.inserted_id}"


# Insertar varios productos
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
            "categoria": "monitores",
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

    resultado = col_productos.insert_many(productos)

    return f"Insertados: {len(resultado.inserted_ids)} documentos"


# Consultar todos los productos
@app.route("/api/productos")
def get_productos():
    productos = list(col_productos.find())

    productos = [
        doc_a_dict(producto)
        for producto in productos
    ]

    return jsonify(productos)


# EJERCICIO 7
# Consultar solamente los productos activos
@app.route("/api/activos")
def get_activos():
    documentos = list(
        col_productos.find({"activo": True})
    )

    documentos = [
        doc_a_dict(documento)
        for documento in documentos
    ]

    return jsonify(documentos)

@app.route("/api/productos/caros")
def get_caros():
    documentos = list(
        col_productos.find({
            "precio": {"$gt": 200000}
        })
    )

    documentos = [
        doc_a_dict(documento)
        for documento in documentos
    ]

    return jsonify(documentos)



# EJERCICIO 9
# Actualizar el precio del Teclado Mecánico
@app.route("/actualizar-teclado")
def actualizar_teclado():
    resultado = col_productos.update_one(
        {"nombre": "Teclado Mecánico"},
        {"$set": {"precio": 195000}}
    )

    return (
        f"Documentos encontrados: {resultado.matched_count}. "
        f"Documentos actualizados: {resultado.modified_count}"
    )



# EJERCICIO E3
# Crear un producto validando que el precio sea mayor que cero
@app.route("/api/productos", methods=["POST"])
def crear_producto():
    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({
            "error": "No se recibieron datos"
        }), 400

    precio = datos.get("precio")

    if not isinstance(precio, (int, float)) or precio <= 0:
        return jsonify({
            "error": "Precio inválido. Debe ser mayor que cero"
        }), 400

    resultado = col_productos.insert_one(datos)

    return jsonify({
        "id": str(resultado.inserted_id),
        "mensaje": "Producto creado correctamente"
    }), 201

# EJERCICIO 11
# Consultar un producto por su ID
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



# RETO FINAL A
# Consultar productos por categoría
@app.route("/api/productos/categoria/<nombre>", methods=["GET"])
def productos_por_categoria(nombre):
    documentos = list(
        col_productos.find({
            "categoria": nombre
        })
    )

    documentos = [
        doc_a_dict(documento)
        for documento in documentos
    ]

    return jsonify(documentos)







if __name__ == "__main__":
    app.run(debug=True, port=5000)