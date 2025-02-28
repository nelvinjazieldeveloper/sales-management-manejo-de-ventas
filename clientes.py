import sqlite3

# Conectar a la base de datos (crear si no existe)
conn = sqlite3.connect("gestion_de_ventas.db", check_same_thread=False)
cursor = conn.cursor()


# Crear la tabla 'clientes' si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    cedula INT(15) PRIMARY KEY,
    nombre TEXT,
    apellido TEXT,
    direccion TEXT,
    telefono TEXT
)""")

conn.commit()  # Confirmar los cambios en la base de datos

# Función para registrar un nuevo cliente
def registrar_cliente(cedula, nombre, apellido, direccion, telefono):
    """Registra un nuevo cliente en la base de datos.

    Args:
        cedula (int): Cédula de identidad del cliente.
        nombre (str): Nombre del cliente.
        apellido (str): Apellido del cliente.
        direccion (str): Dirección del cliente.
        telefono (str): Número de teléfono del cliente.

    Returns:
        bool: True si el cliente se registró correctamente, False en caso contrario.
    """

    cursor.execute("INSERT INTO clientes (cedula, nombre, apellido, direccion, telefono) VALUES (?, ?, ?, ?, ?)",
                    (cedula, nombre, apellido, direccion, telefono))
    conn.commit()

    if cursor.rowcount == 1:
        return "Cliente registrado exitosamente"
    else:
        return "Error al registrar el cliente"

# Función para buscar un cliente por su cédula
def buscar_cliente(cedula):
    """Busca un cliente en la base de datos por su cédula.

    Args:
        cedula (int): Cédula de identidad del cliente a buscar.

    Returns:
        tuple: Una tupla con los datos del cliente si se encuentra, None en caso contrario.
    """

    cursor.execute("SELECT * FROM clientes WHERE cedula = ?", (cedula,))
    return cursor.fetchone()

def obtener_clientes():
    cursor.execute("SELECT * FROM clientes")
    return cursor.fetchall()