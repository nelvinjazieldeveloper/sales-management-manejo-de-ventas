import clientes
import perfil
import inventario
import sqlite3
import flet as ft
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Conectar a la base de datos (crear si no existe)
conn = sqlite3.connect('gestion_de_ventas.db', check_same_thread=False)
cursor = conn.cursor()


# Crear la tabla 'ventas' si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente INT(11),
    monto DECIMAL(10,2),
    monto_bs DECIMAL(10,2),
    fecha DATETIME,
    FOREIGN KEY (cliente) REFERENCES clientes(cedula)
)""")

conn.commit()

#BD del precio del dolar

cursor.execute("""
CREATE TABLE IF NOT EXISTS precio_dolar (
    precio DECIMAL(10,2)
)
            """)

conn.commit()

def precio_dolar():
    url = "https://www.bcv.org.ve/"
    
    response = requests.get(url, verify=False)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        precios_divisas = soup.find_all("div", class_=['col-sm-6 col-xs-6 centrado'])
        
        precio_dolar = precios_divisas[4].text
        
        precio_dolar = precio_dolar.replace(",",".").strip()
        
        precio_dolar = round(float(precio_dolar), 2)
        
        return precio_dolar

# Función para registrar una venta en la base de datos
def registrar_venta(productos: list):
    """Registra una venta en la base de datos.

    Args:
        productos (list): Una lista de diccionarios, cada uno representando un producto con
        los campos 'producto', 'precio', 'cantidad', 'monto' y 'monto_bs'.

    Returns:
        bool: True si la venta se registró correctamente, False en caso contrario.
    """

    # Calcular los totales de la venta
    total = sum(producto['monto'] for producto in productos)
    total_bs = sum(producto['monto_bs'] for producto in productos)

    # Insertar la venta en la base de datos
    cursor.execute("INSERT INTO ventas (cliente, monto, monto_bs, fecha) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (productos[0]['cliente'],total, total_bs))

    if cursor.rowcount == 1:
        print("Venta registrada exitosamente")
        for producto in productos:
            cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE producto = ?", (producto['cantidad'], producto['producto']))
        conn.commit()
        return True
    else:
        print("Error al registrar la venta")
        return False

def ventas_page(page= ft.Page):
    def factura(carrito, cliente_info):
        page.clean()  # Limpiar la página
        
        vendedor = perfil.obtener_informacion()  # Obtener información del vendedor
        
        # Datos del vendedor
        vendedor_nombre = vendedor[1]
        vendedor_rif = vendedor[2]
        vendedor_direccion = vendedor[3]
        vendedor_telefono = vendedor[4]

        # Buscar información del cliente
        cliente = clientes.buscar_cliente(cliente_info)
        cliente_rif = cliente[0]
        cliente_nombre = f"{cliente[1]} {cliente[2]}"
        cliente_direccion = cliente[3]
        cliente_telefono = cliente[4]

        # Generar número de factura
        numero_factura = "F-" + str(datetime.now().timestamp()).replace(".", "")
        fecha_emision = datetime.now().strftime("%d/%m/%Y")  # Fecha de emisión

        # Calcular subtotal, IVA y total
        subtotal = round(sum(item['monto_bs'] for item in carrito), 2)
        iva = round(subtotal * 0.16, 2)  # Suponiendo un IVA del 16%
        total = round(subtotal + iva, 2)

        # Generar contenido de la factura
        factura_content = f"""
        {'='*40}
        {'Factura':^40}
        {'='*40}
        Vendedor:
        Nombre: {vendedor_nombre}
        RIF: {vendedor_rif}
        Dirección: {vendedor_direccion}
        Teléfono: {vendedor_telefono}
        
        Cliente:
        Nombre: {cliente_nombre}
        RIF: {cliente_rif}
        Dirección: {cliente_direccion}
        Teléfono: {cliente_telefono}
        
        Número de Factura: {numero_factura}
        Fecha de Emisión: {fecha_emision}
        
        {'-'*40}
        Detalle de Productos:
        {'-'*40}
        """
        
        # Agregar cada producto del carrito a la factura
        for item in carrito:
            factura_content += f"{item['producto']}: {item['cantidad']} x {round(item['precio'], 2)} = {round(item['monto_bs'], 2)}\n"

        factura_content += f"""
        {'-'*40}
        Subtotal: {subtotal}
        IVA (16%): {iva}
        {'-'*40}
        Total: {total}
        {'='*40}
        """

        # Mostrar la factura en la página
        page.add(ft.Text(factura_content, size=12, weight="normal"))
        
        page.update()
        
    # Función para abastecer un producto en el inventario
    def abastecer_page(producto):
        page.clean()  # Limpiar la página
        cantidad = ft.TextField(label="Cantidad a añadir")  # Campo para ingresar la cantidad
        page.add(
            ft.Text(producto, size=20, weight="bold"),  # Mostrar el nombre del producto
            cantidad,
            ft.ElevatedButton(
                "Guardar",
                on_click=lambda _: page.add(ft.Text(inventario.abastecer_inventario(producto, cantidad.value), color="green", size=20, weight="bold"))
            )
        )
        page.update()
        # Función para validar si el cliente existe
        def validar_clientes_ventas(cedula):
            consulta = clientes.buscar_cliente(cedula)
            if not consulta:
                cliente_texto.value = "El cliente no existe"
            else:
                cliente_texto.value = ""
            page.update()
            
        # Función para validar y registrar la venta
        def validar_venta(carrito):
            if registrar_venta(carrito):
                page.add(ft.Text("Venta realizada con éxito", color="green", size=20, weight="bold"), ft.ElevatedButton("Imprimir Factura", on_click=lambda _: factura(carrito, carrito[0]["cliente"])))
            else:
                page.add(ft.Text("Error al registrar la venta", color="red", size=20, weight="bold"))

        # Función para actualizar el carrito de compras
        def actualizar_carrito(producto):
            if inventario.validar_stock(producto["producto"], producto["cantidad"]) == "":
                carrito.append(producto)  # Agregar producto al carrito
                monto = sum(item["monto"] for item in carrito)  # Calcular monto total
                monto_bs = sum(item["monto_bs"] for item in carrito)  # Calcular monto total en Bs
                monto_input.value = str(round(monto, 2))
                monto_bs_input.value = str(round(monto_bs, 2))

                # Actualizar la vista del carrito
                carrito_tabla.rows.clear()
                for item in carrito:
                    fila = ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(item['producto'])),
                            ft.DataCell(ft.Text(str(item['precio']))),
                            ft.DataCell(ft.Text(str(item['cantidad']))),
                            ft.DataCell(ft.Text(str(round(item['monto'], 2)))),
                            ft.DataCell(ft.Text(str(round(item['monto_bs'], 2))))
                        ]
                    )
                    carrito_tabla.rows.append(fila)

                # Agregar fila para total
                total_fila = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Total", weight="bold")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text(str(round(monto, 2) + (round(monto, 2) * 0.16)), weight="bold")),
                        ft.DataCell(ft.Text(str(round(monto_bs, 2) + (round(monto_bs * 0.16, 2))), weight="bold"))
                    ]
                )
                carrito_tabla.rows.append(total_fila)

                page.update()
            else:
                page.add(ft.Text(inventario.validar_stock(producto["producto"], producto["cantidad"])))

        carrito = []  # Inicializar el carrito de compras
        page.clean()  # Limpiar la página
        productos = inventario.obtener_inventario()  # Obtener productos del inventario

        # Crear campos para ingresar información de la venta
        cedula = ft.TextField(label="Cedula", on_change=lambda e: validar_clientes_ventas(e.control.value))
        cliente_texto = ft.Text("", color="red")
        productos_select = ft.Dropdown(
            label="Productos",
            options=[ft.dropdown.Option(producto[1]) for producto in productos]
        )
        cantidad = ft.TextField(label="Cantidad", keyboard_type=ft.KeyboardType.NUMBER)
        monto_input = ft.TextField(label="Monto", disabled=True, keyboard_type=ft.KeyboardType.NUMBER)
        monto_bs_input = ft.TextField(label="Monto en Bs", disabled=True, keyboard_type=ft.KeyboardType.NUMBER)
        carrito_tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Cantidad")),
                ft.DataColumn(ft.Text("Monto")),
                ft.DataColumn(ft.Text("Monto en Bs")),
            ],
            rows=[]
        )

        # Agregar elementos a la página para realizar la venta
        page.add(
            ft.Text("Realizar Venta", size=20, weight="bold"),
            cedula,
            cliente_texto,
            productos_select,
            cantidad,
            ft.ElevatedButton("Añadir Producto al Carrito", on_click=lambda _: actualizar_carrito({
                "producto": productos_select.value,
                "precio": inventario.obtener_producto(productos_select.value)[3],
                "cantidad": float(cantidad.value),
                "monto": inventario.obtener_producto(productos_select.value)[3] * float(cantidad.value),
                "monto_bs": inventario.obtener_producto(productos_select.value)[3] * float(cantidad.value),
                "cliente": cedula.value
            })),
            carrito_tabla,
            ft.ElevatedButton(
                "Realizar Venta",
                on_click=lambda _: validar_venta(carrito)
            )
        )
