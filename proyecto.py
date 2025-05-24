import mysql.connector
import json
from datetime import datetime

class Proyecto:
    def __init__(self, conexion):
        self.__conexion = conexion
        
    def __validar_fechas(self, fecha_inicio, fecha_fin):
        """Valida el formato de fechas"""
        try:
            inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            return inicio <= fin
        except ValueError:
            return False
            
    def crear_proyecto(self, datos_proyecto):
        """Crea un nuevo proyecto"""
        if not self.__validar_fechas(datos_proyecto['fecha_inicio'], datos_proyecto['fecha_fin']):
            print("Fechas inválidas")
            return False
            
        try:
            cursor = self.__conexion.cursor()
            cursor.execute('''
                INSERT INTO proyectos (nombre, descripcion, fecha_inicio, fecha_fin, estado)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                datos_proyecto['nombre'],
                datos_proyecto['descripcion'],
                datos_proyecto['fecha_inicio'],
                datos_proyecto['fecha_fin'],
                datos_proyecto['estado']
            ))
            self.__conexion.commit()
            print("Proyecto creado")
            return True
        except mysql.connector.Error as e:
            print(f"Error al crear proyecto: {e}")
            return False
            
    def obtener_proyectos(self):
        """Obtiene todos los proyectos"""
        try:
            cursor = self.__conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM proyectos")
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error al obtener proyectos: {e}")
            return []
            
    def actualizar_proyecto(self, id_proyecto, nuevos_datos):
        """Actualiza un proyecto existente"""
        try:
            cursor = self.__conexion.cursor()
            query = "UPDATE proyectos SET "
            params = []
            
            if 'nombre' in nuevos_datos:
                query += "nombre = %s, "
                params.append(nuevos_datos['nombre'])
                
            if 'descripcion' in nuevos_datos:
                query += "descripcion = %s, "
                params.append(nuevos_datos['descripcion'])
                
            if 'fecha_inicio' in nuevos_datos and 'fecha_fin' in nuevos_datos:
                if not self.__validar_fechas(nuevos_datos['fecha_inicio'], nuevos_datos['fecha_fin']):
                    print("Fechas inválidas")
                    return False
                query += "fecha_inicio = %s, fecha_fin = %s, "
                params.extend([nuevos_datos['fecha_inicio'], nuevos_datos['fecha_fin']])
                
            if 'estado' in nuevos_datos:
                query += "estado = %s, "
                params.append(nuevos_datos['estado'])
                
            query = query.rstrip(", ") + " WHERE id = %s"
            params.append(id_proyecto)
            
            cursor.execute(query, params)
            self.__conexion.commit()
            
            if cursor.rowcount > 0:
                print("Proyecto actualizado")
                return True
            print("No se encontró el proyecto")
            return False
        except mysql.connector.Error as e:
            print(f"Error al actualizar: {e}")
            return False
            
    def eliminar_proyecto(self, id_proyecto):
        """Elimina un proyecto"""
        try:
            cursor = self.__conexion.cursor()
            cursor.execute("DELETE FROM proyectos WHERE id = %s", (id_proyecto,))
            self.__conexion.commit()
            
            if cursor.rowcount > 0:
                print("Proyecto eliminado")
                return True
            print("No se encontró el proyecto")
            return False
        except mysql.connector.Error as e:
            print(f"Error al eliminar: {e}")
            return False
            
    def generar_respaldo(self, archivo_salida):
        """Genera un respaldo en JSON"""
        proyectos = self.obtener_proyectos()
        if not proyectos:
            print("No hay proyectos para respaldar")
            return False
            
        try:
            with open(archivo_salida, 'w') as f:
                json.dump(proyectos, f, indent=4)
            print(f"Respaldo guardado en {archivo_salida}")
            return True
        except Exception as e:
            print(f"Error al generar respaldo: {e}")
            return False