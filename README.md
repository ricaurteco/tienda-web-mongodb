# Tienda Web con Flask y MongoDB

Proyecto académico desarrollado con **Python, Flask y MongoDB** para gestionar productos mediante una API web e implementar controles básicos de seguridad, validación, auditoría y respaldo de la base de datos.

## Objetivo

Construir una aplicación Flask conectada a MongoDB que permita consultar, crear, actualizar y eliminar productos, aplicando buenas prácticas de seguridad y control de datos.

## Tecnologías utilizadas

- Python
- Flask
- MongoDB
- PyMongo
- python-dotenv
- Postman
- Git y GitHub
- MongoDB Compass
- MongoDB Database Tools (`mongodump` y `mongorestore`)

## Estructura principal del proyecto

```text
tienda_web/
├── templates/
├── .gitignore
├── app.py
└── conexion.py
```

> El archivo `.env` se utiliza localmente para almacenar la cadena de conexión y otras variables sensibles. Está excluido del repositorio mediante `.gitignore` y no debe publicarse en GitHub.

## Funcionalidades principales

La aplicación incluye:

- Conexión segura a MongoDB mediante variables de entorno.
- Consulta de todos los productos.
- Consulta de productos activos.
- Consulta de productos con precio superior a 200000.
- Consulta de productos por categoría.
- Consulta de un producto por su identificador.
- Creación de productos mediante `POST`.
- Actualización de productos mediante `PUT`.
- Eliminación de productos mediante `DELETE`.
- Validación del campo `precio`.
- Registro automático de operaciones en la colección `auditoria`.
- Consulta de los últimos registros de auditoría mediante API.
- Modo `debug` de Flask desactivado.

## Endpoints principales

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Página principal |
| GET | `/saludo` | Mensaje de bienvenida |
| GET | `/info` | Información del taller |
| GET | `/api/productos` | Lista todos los productos |
| GET | `/api/activos` | Lista productos activos |
| GET | `/api/productos/caros` | Lista productos con precio superior a 200000 |
| GET | `/api/productos/<id>` | Consulta un producto por ID |
| GET | `/api/productos/categoria/<nombre>` | Consulta productos por categoría |
| POST | `/api/productos` | Crea un producto |
| PUT | `/api/productos/<id>` | Actualiza un producto |
| DELETE | `/api/productos/<id>` | Elimina un producto |
| GET | `/api/auditoria` | Consulta los últimos registros de auditoría |

## Validación de productos

Antes de insertar información, la aplicación valida datos como:

- Nombre válido.
- Precio numérico.
- Precio mayor que cero.
- Categoría obligatoria.

Además, la colección `productos` fue configurada con validación de esquema en MongoDB para reforzar la integridad de los datos.

## Auditoría

Se implementó una colección llamada `auditoria` que registra operaciones realizadas sobre los productos.

Cada registro puede incluir:

- Acción realizada.
- Fecha y hora.
- Usuario de la aplicación.
- Dirección IP.
- Resumen de los datos involucrados.

Se probaron registros de tipo `INSERT`, `UPDATE` y `DELETE`.

El endpoint `GET /api/auditoria` permite consultar los últimos eventos registrados.

## Seguridad implementada

### 1. Autenticación de MongoDB

Se comprobó que una consulta sin credenciales es rechazada por MongoDB con un mensaje de autorización requerida.

### 2. Variables de entorno

La cadena de conexión se obtiene desde:

```python
os.environ.get("MONGO_URI")
```

Las credenciales no están escritas directamente en el código fuente.

### 3. Protección del archivo `.env`

El archivo `.env` está incluido en `.gitignore`, evitando que las credenciales sean publicadas en GitHub.

### 4. Prevención básica de inyección NoSQL

Se probó el envío de un operador de MongoDB dentro del campo `precio`. La aplicación rechazó la solicitud con estado `400 Bad Request` porque el precio debe ser un valor numérico válido.

### 5. Modo de depuración

El modo de depuración de Flask fue desactivado:

```python
debug=False
```

## Respaldo y restauración

Se realizó un respaldo de la base de datos utilizando `mongodump`.

Posteriormente se probó la restauración con `mongorestore` en una base de datos de prueba llamada `tienda_db_restaurada`.

La restauración finalizó correctamente con:

```text
22 documentos restaurados
0 documentos fallidos
```

Esto permitió comprobar que el respaldo podía recuperarse correctamente sin afectar la base de datos original.

## Pruebas realizadas

Durante el desarrollo se realizaron, entre otras, las siguientes pruebas:

- Creación correcta de productos.
- Rechazo de precios iguales o menores que cero.
- Actualización de productos.
- Eliminación de productos.
- Registro de operaciones en auditoría.
- Consulta de auditoría.
- Intento de acceso a MongoDB sin credenciales.
- Intento básico de inyección NoSQL.
- Búsqueda de posibles credenciales expuestas en archivos controlados por Git.
- Verificación de que `.env` está ignorado por Git.
- Verificación de Flask con `Debug mode: off`.
- Respaldo y restauración de MongoDB.

## Ejecución local

### 1. Crear y activar un entorno virtual

En Windows:

```cmd
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar dependencias

```cmd
pip install flask pymongo python-dotenv
```

### 3. Crear el archivo `.env`

Crear un archivo `.env` en la raíz del proyecto con las variables necesarias para la conexión.

Ejemplo de estructura:

```env
MONGO_URI=<cadena_de_conexion>
SECRET_KEY=<clave_secreta>
```

No publicar valores reales de usuario, contraseña o claves.

### 4. Ejecutar la aplicación

```cmd
python app.py
```

La aplicación queda disponible localmente en:

```text
http://127.0.0.1:5000
```

## Control de versiones

El proyecto fue gestionado con Git. Entre los cambios registrados se encuentran:

- Configuración de autenticación y variables de entorno.
- Validación del precio en el endpoint de productos.
- Implementación de auditoría de operaciones.
- Desactivación del modo debug de Flask.

## Autor

**Ricaurte Contreras Criado**

Proyecto académico de formación ADSO.
