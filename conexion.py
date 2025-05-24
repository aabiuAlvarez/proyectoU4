import mysql.connector
import json
from mysql.connector import Error

class Conexion:
    def __init__(self):
        self.__host = "localhost"
        self.__usuario = "root"
        self.__contrasena = ""  # Contraseña de XAMPP (vacía por defecto)
        self.__base_datos = "gestion_proyectos"
        self.__conexion = None
        
    def conectar(self):
        """Establece conexión con MySQL con verificación de servidor"""
        try:
            # Primero probamos conexión básica al servidor
            test_conn = mysql.connector.connect(
                host=self.__host,
                user=self.__usuario,
                password=self.__contrasena
            )
            test_conn.close()
            
            # Ahora conectamos para uso real
            self.__conexion = mysql.connector.connect(
                host=self.__host,
                user=self.__usuario,
                password=self.__contrasena,
                database=self.__base_datos if self.__verificar_bd_existe() else None
            )
            print("✅ Conexión exitosa a MySQL")
            return True
        except Error as e:
            print(f"❌ Error al conectar a MySQL: {e}")
            print("Verifica que:")
            print("1. XAMPP esté corriendo con MySQL activo")
            print("2. Las credenciales sean correctas")
            print(f"3. La base de datos '{self.__base_datos}' exista (o déjalo que se cree automáticamente)")
            return False
            
    def __verificar_bd_existe(self):
        """Verifica si la base de datos existe"""
        try:
            temp_conn = mysql.connector.connect(
                host=self.__host,
                user=self.__usuario,
                password=self.__contrasena
            )
            cursor = temp_conn.cursor()
            cursor.execute(f"SHOW DATABASES LIKE '{self.__base_datos}'")
            existe = cursor.fetchone() is not None
            temp_conn.close()
            return existe
        except:
            return False
            
    def desconectar(self):
        """Cierra la conexión de manera segura"""
        if self.__conexion and self.__conexion.is_connected():
            self.__conexion.close()
            print("🔌 Conexión MySQL cerrada")
            
    def get_conexion(self):
        """Obtiene la conexión actual con verificación"""
        if self.__conexion and self.__conexion.is_connected():
            return self.__conexion
        print("⚠️ No hay conexión activa")
        return None
        
    def __crear_base_datos(self):
        """Crea la base de datos con verificación de errores"""
        try:
            cursor = self.__conexion.cursor()
            
            # Crear base de datos con collation UTF-8
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS `{self.__base_datos}`
                CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
            """)
            
            # Seleccionar la base de datos
            cursor.execute(f"USE `{self.__base_datos}`")
            
            print(f"✅ Base de datos '{self.__base_datos}' lista")
            return True
        except Error as e:
            print(f"❌ Error al crear base de datos: {e}")
            return False
            
    def crear_tablas(self):
        """Crea las tablas con estructura mejorada"""
        if not self.__crear_base_datos():
            return False
            
        try:
            cursor = self.__conexion.cursor()
            
            # Tabla proyectos con índices mejorados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS `proyectos` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `nombre` VARCHAR(100) NOT NULL,
                    `descripcion` TEXT,
                    `fecha_inicio` DATE NOT NULL,
                    `fecha_fin` DATE NOT NULL,
                    `estado` ENUM('Planificado', 'En progreso', 'Completado', 'Cancelado') NOT NULL DEFAULT 'Planificado',
                    `fecha_creacion` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    `fecha_actualizacion` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_estado` (`estado`),
                    INDEX `idx_fechas` (`fecha_inicio`, `fecha_fin`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            # Tabla usuarios con seguridad mejorada
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS `usuarios` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `usuario` VARCHAR(50) UNIQUE NOT NULL,
                    `contrasena` VARCHAR(255) NOT NULL,  # Para almacenar hashes
                    `rol` ENUM('admin', 'usuario') NOT NULL DEFAULT 'usuario',
                    `correo` VARCHAR(100) UNIQUE NOT NULL,
                    `activo` BOOLEAN DEFAULT TRUE,
                    `fecha_creacion` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    `ultimo_login` DATETIME NULL,
                    INDEX `idx_usuario` (`usuario`),
                    INDEX `idx_rol` (`rol`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            self.__conexion.commit()
            print("✅ Tablas creadas correctamente con estructura mejorada")
            return True
        except Error as e:
            print(f"❌ Error al crear tablas: {e}")
            print("Posibles causas:")
            print("- La base de datos no existe")
            print("- Problemas de permisos")
            print("- Sintaxis SQL inválida")
            return False
            
    def insertar_datos_iniciales(self, archivo_json="datos_iniciales.json"):
        """Inserta datos iniciales con transacción segura"""
        if not self.__conexion or not self.__conexion.is_connected():
            print("⚠️ No hay conexión activa")
            return False
            
        try:
            # Leer archivo JSON con manejo de encoding
            with open(archivo_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                
            cursor = self.__conexion.cursor()
            
            # Iniciar transacción
            self.__conexion.start_transaction()
            
            # 1. Insertar proyectos
            proyectos_insertados = 0
            for proyecto in datos.get('proyectos', []):
                cursor.execute('''
                    INSERT INTO `proyectos` 
                    (`nombre`, `descripcion`, `fecha_inicio`, `fecha_fin`, `estado`)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (
                    proyecto.get('nombre', 'Sin nombre'),
                    proyecto.get('descripcion', ''),
                    proyecto.get('fecha_inicio', '2023-01-01'),
                    proyecto.get('fecha_fin', '2023-12-31'),
                    proyecto.get('estado', 'Planificado')
                ))
                proyectos_insertados += 1
                
            # 2. Insertar usuario admin por defecto (si no existe)
            cursor.execute('''
                INSERT IGNORE INTO `usuarios` 
                (`usuario`, `contrasena`, `rol`, `correo`)
                VALUES (%s, %s, %s, %s)
            ''', (
                'admin',
                'admin123',  # IMPORTANTE: En producción usar bcrypt o similar
                'admin',
                'admin@example.com'
            ))
            
            # Confirmar transacción
            self.__conexion.commit()
            
            print(f"✅ Datos iniciales insertados: {proyectos_insertados} proyectos")
            print("   Usuario admin creado (usuario: admin, contraseña: admin123)")
            return True
            
        except FileNotFoundError:
            print(f"⚠️ Archivo {archivo_json} no encontrado")
            self.__conexion.rollback()
            return False
        except json.JSONDecodeError:
            print("⚠️ Error al leer el archivo JSON (formato inválido)")
            self.__conexion.rollback()
            return False
        except Error as e:
            print(f"❌ Error al insertar datos: {e}")
            self.__conexion.rollback()
            return False