import mysql.connector
import getpass
from mysql.connector import Error

class Login:
    def __init__(self, conexion):
        self.__conexion = conexion
        self.__usuario_actual = None
        
    def __validar_credenciales(self, usuario, contrasena):
        """Valida usuario y contraseña"""
        try:
            cursor = self.__conexion.cursor(dictionary=True)
            cursor.execute('''
                SELECT * FROM usuarios 
                WHERE usuario = %s AND contrasena = %s
            ''', (usuario, contrasena))
            return cursor.fetchone()
        except Error as e:
            print(f"Error al validar: {e}")
            return None
            
    def registrar_usuario(self):
        """Registra un nuevo usuario"""
        print("\n--- Registro de usuario ---")
        usuario = input("Usuario: ").strip()
        contrasena = getpass.getpass("Contraseña: ")
        correo = input("Correo electrónico: ").strip()
        
        if not usuario or not contrasena or not correo:
            print("Todos los campos son obligatorios")
            return False
            
        try:
            cursor = self.__conexion.cursor()
            cursor.execute('''
                INSERT INTO usuarios (usuario, contrasena, rol, correo)
                VALUES (%s, %s, %s, %s)
            ''', (usuario, contrasena, 'usuario', correo))
            self.__conexion.commit()
            print("Usuario registrado exitosamente")
            return True
        except Error as e:
            print(f"Error al registrar: {e}")
            return False
            
    def iniciar_sesion(self):
        """Inicia sesión con un usuario"""
        print("\n--- Inicio de sesión ---")
        usuario = input("Usuario: ").strip()
        contrasena = getpass.getpass("Contraseña: ")
        
        usuario_db = self.__validar_credenciales(usuario, contrasena)
        if usuario_db:
            self.__usuario_actual = {
                'id': usuario_db['id'],
                'usuario': usuario_db['usuario'],
                'rol': usuario_db['rol'],
                'correo': usuario_db['correo']
            }
            print(f"Bienvenido, {usuario_db['usuario']}")
            return True
        print("Credenciales incorrectas")
        return False
        
    def cerrar_sesion(self):
        """Cierra la sesión actual"""
        if self.__usuario_actual:
            print(f"Cerrando sesión de {self.__usuario_actual['usuario']}")
            self.__usuario_actual = None
            return True
        print("No hay sesión activa")
        return False
        
    def obtener_usuario_actual(self):
        """Obtiene información del usuario actual"""
        return self.__usuario_actual
        
    def tiene_permiso(self, permiso):
        """Verifica permisos del usuario"""
        if not self.__usuario_actual:
            return False
        return self.__usuario_actual['rol'] == 'admin' or permiso == 'usuario'