import sqlite3
from datetime import datetime, timedelta

# Conectar a la base de datos
conn = sqlite3.connect("gestion_de_ventas.db", check_same_thread=False)
cursor = conn.cursor()


def diario():
    cursor.execute("SELECT * FROM ventas WHERE DATE(fecha) = ?", (datetime.now().strftime("%Y-%m-%d"),))
    ventas = cursor.fetchall()
    total = 0
    total_bs = 0
    for venta in ventas:
        total += venta[2]
        total_bs += venta[3]
    return {"ventas": ventas, "total": total, "total_bs": total_bs}

def semanal():
    cursor.execute("SELECT * FROM ventas WHERE DATE(fecha) >= ?", (datetime.now() - timedelta(days=7),))
    ventas = cursor.fetchall()
    total = 0
    total_bs = 0
    for venta in ventas:
        total += venta[2]
        total_bs += venta[3]
    return {"ventas": ventas, "total": total, "total_bs": total_bs}

def mensual():
    cursor.execute("SELECT * FROM ventas WHERE DATE(fecha) >= ?", (datetime.now() - timedelta(days=30),))
    ventas = cursor.fetchall()
    total = 0
    total_bs = 0
    for venta in ventas:
        total += venta[2]
        total_bs += venta[3]
    return {"ventas": ventas, "total": total, "total_bs": total_bs}