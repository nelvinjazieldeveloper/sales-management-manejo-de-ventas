import sqlite3

conn = sqlite3.connect("gestion_de_ventas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS perfil (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa TEXT,
    rif TEXT,
    direccion TEXT,
    telefono TEXT
)""")

conn.commit()

def guardar_informacion(empresa, rif, direccion, telefono):
    cursor.execute("SELECT * FROM perfil")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO perfil (empresa, rif, direccion, telefono) VALUES (?, ?, ?, ?)", (empresa, rif, direccion, telefono))
        conn.commit()
        if cursor.rowcount == 1:
            return "Información guardada exitosamente"
        else:
            return "Error al guardar la información"
    else:
        cursor.execute("UPDATE perfil SET empresa = ?, rif = ?, direccion = ?, telefono = ? WHERE id = 1", (empresa, rif, direccion, telefono))
        conn.commit()
        if cursor.rowcount == 1:
            return "Información actualizada exitosamente"
        else:
            return "Error al actualizar la información"

def obtener_informacion():
    cursor.execute("SELECT * FROM perfil")
    return cursor.fetchone()