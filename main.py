import sqlite3
from datetime import datetime
import crear_pdf
import ventas
import clientes
import inventario
import reporte
import perfil
import cobros
import flet as ft
import os

# Conectar a la base de datos con check_same_thread=False para permitir múltiples hilos
conn = sqlite3.connect("gestion_de_ventas.db", check_same_thread=False)
cursor = conn.cursor()

dolar = ventas.precio_dolar()

def main(page: ft.Page):
    # Configuración inicial de la página
    page.title = "Gestion de Ventas"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.ALWAYS
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    

    
    # Función para mostrar la página de cobros
    def cobros_page():
        page.clean()  # Limpiar la página
        clientes_tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Cedula")),
                ft.DataColumn(ft.Text("Monto")),
                ft.DataColumn(ft.Text("Monto en Bs")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Pagar"))
            ],
            rows=[

            ]
        )
        def mostrar_cobros_pendientes(clientes):
            cobros_pendientes = cobros.obtener_deudas(clientes)
            # Limpiar las filas existentes antes de agregar las nuevas
            clientes_tabla.rows = []

            for cobro in cobros_pendientes:
                # Agregar una fila al DataTable usando el método add_row
                clientes_tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(cobro[1])),
                        ft.DataCell(ft.Text(cobro[2])),
                        ft.DataCell(ft.Text(cobro[4])),
                        ft.DataCell(ft.ElevatedButton("Pagar", on_click=lambda _, id = cobro[0]: page.add(ft.Text(cobros.pagar(id), color="green", size=20, weight="bold"))))
                    ]
                )
                )

            # Actualizar la página para reflejar los cambios
            page.update()
    
        page.add(
            ft.Text("Cobros", size=20, weight="bold"),
            ft.TextField(label="Filtrar por cedula de cliente", on_change=lambda e: mostrar_cobros_pendientes(e.data)),
            clientes_tabla
            )
        
    
    # Función para mostrar la página de reportes
    def reporte_page():
        page.clean()  # Limpiar la página actual
        tipo_reporte_select = ft.Dropdown(
            label="Tipo de Reporte",
            options=[
                ft.dropdown.Option("Diario"),
                ft.dropdown.Option("Semanal"),
                ft.dropdown.Option("Mensual")
            ],
            on_change=lambda e: movimientos()  # Actualizar movimientos al cambiar el tipo de reporte
        )
        ventas = []  # Inicializar la lista de ventas
        def movimientos():
            page.clean()  # Limpiar la página
            # Obtener las ventas según el tipo de reporte seleccionado
            if tipo_reporte_select.value == "Diario":
                ventas = reporte.diario()
            elif tipo_reporte_select.value == "Semanal":
                ventas = reporte.semanal()
            elif tipo_reporte_select.value == "Mensual":
                ventas = reporte.mensual()
            
            # Crear una tabla para mostrar las ventas
            ventas_tabla = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("N° de Venta")),
                    ft.DataColumn(ft.Text("Fecha")),
                    ft.DataColumn(ft.Text("Cliente")),
                    ft.DataColumn(ft.Text("Monto en $")),
                    ft.DataColumn(ft.Text("Monto en Bs")),
                    ft.DataColumn(ft.Text("IVA a declarar"))
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(venta[0])),
                            ft.DataCell(ft.Text(venta[4])),
                            ft.DataCell(ft.Text(venta[1])),
                            ft.DataCell(ft.Text(round(venta[2], 2))),
                            ft.DataCell(ft.Text(round(venta[3], 2))),
                            ft.DataCell(ft.Text(round(venta[3] * 0.16, 2)))
                        ]
                    )
                    for venta in ventas["ventas"]
                ]
            )
            # Agregar elementos a la página
            page.add(
                tipo_reporte_select,
                ft.Text("Reporte de Ventas", size=20, weight="bold"),
                ft.Text(f"Total $: {round(ventas['total'], 2)}"),
                ft.Text(f"Total Bs: {round(ventas['total_bs'], 2)}"),
                ft.Text(f"IVA a declarar: {round(ventas['total_bs'] * 0.16, 2)}"),
                ventas_tabla
            )
        
        page.add(tipo_reporte_select)  # Agregar el selector de tipo de reporte a la página
    
    # Función para mostrar la página de perfil
    def perfil_page():
        page.clean()  # Limpiar la página
        # Crear campos de texto para la información de la empresa
        empresa = ft.TextField(label="Empresa")
        rif = ft.TextField(label="RIF")
        direccion = ft.TextField(label="Direccion")
        telefono = ft.TextField(label="Telefono")
        # Agregar campos y botón para guardar la información
        page.add(
            empresa,
            rif,
            direccion,
            telefono,
            ft.ElevatedButton(
                "Guardar", on_click=lambda _: page.add(ft.Text(perfil.guardar_informacion(empresa.value, rif.value, direccion.value, telefono.value)))
            )
        )
    
    # Función para ver la lista de clientes
    def ver_clientes_page():
        page.clean()  # Limpiar la página
        # Crear tabla para mostrar los clientes
        clientes_tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Cedula")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Apellido")),
                ft.DataColumn(ft.Text("Direccion")),
                ft.DataColumn(ft.Text("Telefono")),
            ],
            rows=[]
        )
        # Agregar cada cliente a la tabla
        for cliente in clientes.obtener_clientes():
            fila = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(cliente[0])),
                    ft.DataCell(ft.Text(cliente[1])),
                    ft.DataCell(ft.Text(cliente[2])),
                    ft.DataCell(ft.Text(cliente[3])),
                    ft.DataCell(ft.Text(cliente[4])),
                ]
            )
            clientes_tabla.rows.append(fila)
        page.add(clientes_tabla)  # Agregar la tabla a la página
    
    # Función para registrar un nuevo cliente
    def clientes_page():
        page.clean()  # Limpiar la página
        # Crear campos de texto para la información del cliente
        cedula = ft.TextField(label="Cedula")
        nombre = ft.TextField(label="Nombre")
        apellido = ft.TextField(label="Apellido")
        direccion = ft.TextField(label="Direccion")
        telefono = ft.TextField(label="Telefono")
        # Agregar campos y botones para guardar o ver clientes
        page.add(
            cedula,
            nombre,
            apellido,
            direccion,
            telefono,
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Guardar",
                        on_click=lambda _: page.add(ft.Text(clientes.registrar_cliente(cedula.value, nombre.value, apellido.value, direccion.value, telefono.value), color="green", size=20, weight="bold"))
                    ),
                    ft.ElevatedButton(
                        "Ver Clientes",
                        on_click=lambda _: ver_clientes_page()
                    )
                ]
            )
        )
    
    # Función para generar y mostrar la factura
    def factura(carrito, cliente_info):
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
        
        # Guardar la factura en un archivo
        crear_pdf.crear_pdf("factura.pdf", "", None, [{'title': '', 'body': factura_content}])
        
        #abrir el archivo
        os.startfile("factura.pdf")
        
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

    # Función para realizar una venta
    def ventas_page():
        # Función para validar si el cliente existe
        def validar_clientes_ventas(cedula):
            consulta = clientes.buscar_cliente(cedula)
            if not consulta:
                cliente_texto.value = "El cliente no existe"
            else:
                cliente_texto.value = ""
            page.update()
            
        # Función para validar y registrar la venta
        def validar_venta(carrito, tipo_de_venta):
            print(tipo_de_venta)
            if tipo_de_venta == "Credito":
                monto_deuda = sum(item["monto"] for item in carrito)
                monto_deuda_bs = sum(item["monto_bs"] for item in carrito)
                if cobros.registrar_deuda(carrito[0]["cliente"], monto_deuda, monto_deuda_bs) == "Deuda registrada exitosamente":
                    page.add(
                            ft.Text("Venta a credito realizada con éxito", color="green", size=20, weight="bold"),
                            ft.ElevatedButton("Imprimir Factura", on_click=lambda _: factura(carrito, carrito[0]["cliente"]))
                            )
            else:
                if ventas.registrar_venta(carrito):
                    page.add(
                            ft.Text("Venta realizada con éxito", color="green", size=20, weight="bold"),
                            ft.ElevatedButton("Imprimir Factura", on_click=lambda _: factura(carrito, carrito[0]["cliente"]))
                            )
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

        tipo_de_venta = ft.Dropdown(
            label="Tipo de Venta",
            options=[
                ft.dropdown.Option("De contado"),
                ft.dropdown.Option("Credito")
            ]
        )
        # Agregar elementos a la página para realizar la venta
        page.add(
            ft.Text("Realizar Venta", size=20, weight="bold"),
            cedula,
            tipo_de_venta,
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
                on_click=lambda _: validar_venta(carrito, tipo_de_venta.value)
            )
        )

    # Función para añadir un nuevo producto al inventario
    def anadir_producto_page():
        page.clean()  # Limpiar la página
        producto = ft.TextField(label="Producto")  # Campo para el nombre del producto
        precio = ft.TextField(label="Precio")  # Campo para el precio del producto
        cantidad = ft.TextField(label="Cantidad")  # Campo para la cantidad del producto
        # Agregar campos y botón para guardar el producto
        page.add(
            producto,
            precio,
            cantidad,
            ft.ElevatedButton(
                "Guardar",
                on_click=lambda _: page.add(ft.Text(inventario.registrar_producto(producto.value, cantidad.value, precio.value), color="green", size=20, weight="bold"))
            )
        )

    # Función para mostrar la página de inventario
    def inventario_page():
        page.clean()  # Limpiar la página
        productos = inventario.obtener_inventario()  # Obtener productos del inventario

        # Agregar botón para añadir un nuevo producto
        page.add(
            ft.ElevatedButton(
                "Añadir Producto",
                on_click=lambda _: anadir_producto_page()
            )
        )

        # Crear la tabla para mostrar los productos
        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Cantidad")),
                ft.DataColumn(ft.Text("Abastecer"))
            ],
            rows=[]
        )

        # Agregar filas a la tabla para cada producto
        for producto in productos:
            fila = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(producto[1])),
                    ft.DataCell(ft.Text(producto[2])),
                    ft.DataCell(ft.Text(producto[3])),
                    ft.DataCell(ft.ElevatedButton(
                        "Abastecer",
                        on_click=lambda e, p=producto: abastecer_page(p[1])  # Llamar a la función de abastecer
                    ))
                ]
            )
            tabla.rows.append(fila)

        # Agregar la tabla a la página
        page.add(tabla)

    # Configuración de la barra de navegación
    page.appbar = ft.AppBar(
        title=ft.Text(f"Gestion de Inventarios - Precio dólar BCV: {dolar}", color=ft.Colors.BLUE, size=20),
        bgcolor=ft.Colors.BLUE_GREY_50,
        actions=[
            ft.IconButton(
                icon=ft.Icons.REPORT,
                tooltip="Reportes",
                on_click=lambda _: reporte_page()  # Navegar a la página de reportes
            ),
            ft.IconButton(
                icon=ft.Icons.SHOPPING_CART,
                tooltip="Inventario",
                on_click=lambda _: inventario_page()  # Navegar a la página de inventario
            ),
            ft.IconButton(
                icon=ft.Icons.PEOPLE,
                tooltip="Clientes",
                on_click=lambda _: clientes_page()  # Navegar a la página de clientes
            ),
            ft.IconButton(
                icon=ft.Icons.SELL,
                tooltip="Ventas",
                on_click=lambda _: ventas_page()  # Navegar a la página de ventas
            ),
            ft.IconButton(
                icon=ft.Icons .PERSON,
                tooltip="Perfil",
                on_click=lambda _: perfil_page()  # Navegar a la página de perfil
            ),
            ft.IconButton(
                icon=ft.Icons.MONEY,
                tooltip="Cobros",
                on_click=lambda _: cobros_page()  # Navegar a la página de cobros
            )
        ]
    )
    
    page.add(
        ft.TextField(label="Contraseña asignada", password=True),
        ft.ElevatedButton("Ingresar")
    )

# Iniciar la aplicación
target = ft.app(target=main)