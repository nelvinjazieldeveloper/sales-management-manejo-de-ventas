import sqlite3
conn = sqlite3.connect("gestion_de_ventas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
            CREATE TABLE IF NOT EXISTS cobros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente INT(11),
            monto DECIMAL(10,2),
            monto_bs DECIMAL(10,2),
            fecha DATETIME
            )
            """)

def registrar_deuda(cliente, monto, monto_bs):
    cursor.execute("INSERT INTO cobros (cliente, monto, monto_bs, fecha) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (cliente, monto, monto_bs))
    conn.commit()
    if cursor.rowcount == 1:
        return "Deuda registrada exitosamente"
    else:
        return "Error al registrar la deuda"
    
def obtener_deudas(cliente):
    if cliente is None:
        cursor.execute("SELECT * FROM cobros")
        return cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM cobros WHERE cliente = ?", (cliente,))
        return cursor.fetchall()

def pagar(id):
    cursor.execute("SELECT * FROM cobros WHERE id = ?", (id,))
    conn.commit()
    datos = cursor.fetchone()
    
    cursor.execute("INSERT INTO ventas (cliente, monto, monto_bs, fecha) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (datos[1], datos[2], datos[3]))
    conn.commit()
    
    cursor.execute("DELETE FROM cobros WHERE id = ?", (id,))
    conn.commit()
    
    if cursor.rowcount == 1:
        return "Deuda pagada exitosamente"
    else:
        return "Error al pagar la deuda"