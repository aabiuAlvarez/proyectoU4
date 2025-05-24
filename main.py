from conexion import Conexion
from proyecto import Proyecto
from login import Login
import json
import os

def mostrar_menu_principal():
    print("\n=== SISTEMA DE GESTIÓN ===")
    print("1. Iniciar sesión")
    print("2. Registrar usuario")
    print("3. Salir")
    return input("Seleccione una opción: ").strip()

def mostrar_menu_usuario(login, proyecto):
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Ver proyectos")
        print("2. Buscar proyecto")
        print("3. Cerrar sesión")
        
        if login.tiene_permiso('admin'):
            print("\n--- ADMINISTRACIÓN ---")
            print("4. Crear proyecto")
            print("5. Actualizar proyecto")
            print("6. Eliminar proyecto")
            print("7. Generar respaldo")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '1':
            proyectos = proyecto.obtener_proyectos()
            if proyectos:
                print("\n--- LISTA DE PROYECTOS ---")
                for p in proyectos:
                    print(f"\nID: {p['id']}")
                    print(f"Nombre: {p['nombre']}")
                    print(f"Estado: {p['estado']}")
                    print(f"Fechas: {p['fecha_inicio']} a {p['fecha_fin']}")
            else:
                print("No hay proyectos registrados")
                
        elif opcion == '2':
            id_proyecto = input("ID del proyecto: ")
            proyectos = proyecto.obtener_proyectos()
            encontrado = next((p for p in proyectos if str(p['id']) == id_proyecto), None)
            if encontrado:
                print("\n--- DETALLE DEL PROYECTO ---")
                print(f"Nombre: {encontrado['nombre']}")
                print(f"Descripción: {encontrado['descripcion']}")
                print(f"Estado: {encontrado['estado']}")
                print(f"Fechas: {encontrado['fecha_inicio']} a {encontrado['fecha_fin']}")
            else:
                print("Proyecto no encontrado")
                
        elif opcion == '3':
            login.cerrar_sesion()
            break
            
        elif opcion == '4' and login.tiene_permiso('admin'):
            print("\n--- NUEVO PROYECTO ---")
            nuevo = {
                'nombre': input("Nombre: "),
                'descripcion': input("Descripción: "),
                'fecha_inicio': input("Fecha inicio (YYYY-MM-DD): "),
                'fecha_fin': input("Fecha fin (YYYY-MM-DD): "),
                'estado': input("Estado: ")
            }
            if proyecto.crear_proyecto(nuevo):
                print("Proyecto creado exitosamente")
                
        elif opcion == '5' and login.tiene_permiso('admin'):
            print("\n--- ACTUALIZAR PROYECTO ---")
            id_proyecto = input("ID del proyecto: ")
            actualizacion = {}
            
            campo = input("Campo a actualizar (nombre/descripcion/fechas/estado): ").lower()
            if campo == 'nombre':
                actualizacion['nombre'] = input("Nuevo nombre: ")
            elif campo == 'descripcion':
                actualizacion['descripcion'] = input("Nueva descripción: ")
            elif campo == 'fechas':
                actualizacion['fecha_inicio'] = input("Nueva fecha inicio (YYYY-MM-DD): ")
                actualizacion['fecha_fin'] = input("Nueva fecha fin (YYYY-MM-DD): ")
            elif campo == 'estado':
                actualizacion['estado'] = input("Nuevo estado: ")
                
            if actualizacion and proyecto.actualizar_proyecto(id_proyecto, actualizacion):
                print("Proyecto actualizado")
                
        elif opcion == '6' and login.tiene_permiso('admin'):
            print("\n--- ELIMINAR PROYECTO ---")
            id_proyecto = input("ID del proyecto: ")
            if input("¿Confirmar eliminación? (s/n): ").lower() == 's':
                if proyecto.eliminar_proyecto(id_proyecto):
                    print("Proyecto eliminado")
                    
        elif opcion == '7' and login.tiene_permiso('admin'):
            print("\n--- GENERAR RESPALDO ---")
            archivo = input("Nombre del archivo (ej: respaldo.json): ") or "respaldo.json"
            if proyecto.generar_respaldo(archivo):
                print(f"Respaldo generado en {archivo}")
                
        else:
            print("Opción no válida")
            
        input("\nPresione Enter para continuar...")

def main():
    # Configuración inicial
    conexion = Conexion()
    if not conexion.conectar():
        return
        
    # Crear tablas
    if input("¿Crear tablas? (s/n): ").lower() == 's':
        conexion.crear_tablas()
        
        # Insertar datos iniciales
        if input("¿Cargar datos iniciales? (s/n): ").lower() == 's':
            conexion.insertar_datos_iniciales('datos_iniciales.json')
    
    # Inicializar componentes
    proyecto = Proyecto(conexion.get_conexion())
    login = Login(conexion.get_conexion())
    
    # Menú principal
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        opcion = mostrar_menu_principal()
        
        if opcion == '1':
            if login.iniciar_sesion():
                mostrar_menu_usuario(login, proyecto)
                
        elif opcion == '2':
            if login.registrar_usuario():
                input("Usuario registrado. Presione Enter para continuar...")
                
        elif opcion == '3':
            print("Saliendo del sistema...")
            break
            
        else:
            print("Opción no válida")
            input("Presione Enter para continuar...")
            
    conexion.desconectar()

if __name__ == "__main__":
    main()