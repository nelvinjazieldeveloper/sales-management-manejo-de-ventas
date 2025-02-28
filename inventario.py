import sqlite3

conn = sqlite3.connect("gestion_de_ventas.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS inventario (id INTEGER PRIMARY KEY AUTOINCREMENT, producto TEXT, cantidad INTEGER, precio DECIMAL(10,2))")

conn.commit()

def registrar_producto(producto, cantidad, precio):
    cursor.execute("INSERT INTO inventario (producto, cantidad, precio) VALUES (?, ?, ?)", (producto, cantidad, precio))
    conn.commit()
    
    if cursor.rowcount == 1:
        return "Producto registrado exitosamente"
    else:
        return "Error al registrar el producto"

def abastecer_inventario(producto, cantidad):
    cursor.execute("UPDATE inventario SET cantidad = cantidad + ? WHERE producto = ?", (cantidad, producto))
    conn.commit()
    
    if cursor.rowcount == 1:
        return ("Inventario actualizado exitosamente")
    else:
        return ("Error al actualizar el inventario")
    
def obtener_producto(producto):
    cursor.execute("SELECT * FROM inventario WHERE producto = ?", (producto,))
    return cursor.fetchone()

def validar_stock(producto,cantidad):
    cursor.execute("SELECT * FROM inventario WHERE producto = ?", (producto,))
    inventario = cursor.fetchone()
    if inventario[2] >= cantidad:
        return ""
    else:
        return "No hay suficiente en el inventario abastece por favor"

def obtener_inventario():
    cursor.execute("SELECT * FROM inventario")
    return cursor.fetchall()