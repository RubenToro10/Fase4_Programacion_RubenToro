# ==========================================================
# FASE 4: PROGRAMACIÓN - UNAD
# SISTEMA INTEGRAL DE GESTIÓN DE CLIENTES, SERVICIOS Y RESERVAS
# Empresa: Software FJ
# Autor: Ruben Dario Toro Sandoval (Código: 1.090.422.381)
# ==========================================================

import logging

# Configuración básica del archivo de registro de errores (logs)
logging.basicConfig(
    filename="sistema_errores.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==========================================
# 1. EXCEPCIONES PERSONALIZADAS
# ==========================================
class ErrorDatoInvalido(Exception):
    pass

class ErrorServicioNoDisponible(Exception):
    pass

class ErrorReserva(Exception):
    pass


# ==========================================
# 2. CLASE BASE CLIENTE
# ==========================================
class Cliente:
    def __init__(self, cedula, nombre, correo):
        self.cedula = cedula
        self.nombre = nombre
        # Validación sencilla del correo
        if "@" not in correo or "." not in correo:
            msg = f"Correo inválido para el cliente {nombre}: {correo}"
            logging.error(msg)
            raise ErrorDatoInvalido(msg)
        self.correo = correo

    def ver_info(self):
        return f"Cliente: {self.nombre} | Cédula: {self.cedula} | Correo: {self.correo}"


# ==========================================
# 3. CLASES DE SERVICIOS (HERENCIA Y POLIMORFISMO)
# ==========================================
class ServicioBase:
    def __init__(self, id_servicio, nombre, costo_base):
        self.id_servicio = id_servicio
        self.nombre = nombre
        self.costo_base = costo_base
        self.activo = True

    def calcular_costo(self, cantidad):
        pass

    def descripcion(self):
        pass


class ReservaSalas(ServicioBase):
    def __init__(self, id_servicio, nombre, costo_base, capacidad):
        super().__init__(id_servicio, nombre, costo_base)
        self.capacidad = capacidad

    def calcular_costo(self, horas):
        if horas <= 0:
            raise ValueError("Las horas deben ser mayores a cero.")
        return self.costo_base * horas

    def descripcion(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"[Sala] {self.nombre} | Capacidad: {self.capacidad} personas | Costo/Hora: ${self.costo_base} | Estado: {estado}"


class AlquilerEquipos(ServicioBase):
    def __init__(self, id_servicio, nombre, costo_base, tipo):
        super().__init__(id_servicio, nombre, costo_base)
        self.tipo = tipo

    def calcular_costo(self, dias):
        if dias <= 0:
            raise ValueError("Los días deben ser mayores a cero.")
        return self.costo_base * dias

    def descripcion(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"[Equipo] {self.nombre} ({self.tipo}) | Costo/Día: ${self.costo_base} | Estado: {estado}"


class AsesoriaEspecializada(ServicioBase):
    def __init__(self, id_servicio, nombre, costo_base, area):
        super().__init__(id_servicio, nombre, costo_base)
        self.area = area

    def calcular_costo(self, sesiones):
        if sesiones <= 0:
            raise ValueError("Las sesiones deben ser mayores a cero.")
        # Se incluye un impuesto del 19%
        return (self.costo_base * sesiones) * 1.19

    def descripcion(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"[Asesoría] {self.nombre} - Área: {self.area} | Tarifa Base: ${self.costo_base} | Estado: {estado}"


# ==========================================
# 4. CLASE RESERVA CON MANEJO DE EXCEPCIONES
# ==========================================
class Reserva:
    def __init__(self, id_reserva, cliente, servicio, cantidad):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad = cantidad
        self.estado = "Pendiente"
        self.total_pagar = 0.0

    def procesar(self):
        print(f"\n--- Procesando Reserva ID: {self.id_reserva} ---")
        try:
            # Validar si el servicio está activo
            if not self.servicio.activo:
                raise ErrorServicioNoDisponible(f"El servicio '{self.servicio.nombre}' no está disponible.")
            
            # Calcular costo (polimorfismo)
            self.total_pagar = self.servicio.calcular_costo(self.cantidad)
            self.estado = "Aprobada"

        except ErrorServicioNoDisponible as e:
            self.estado = "Cancelada"
            print(f"[Aviso]: {e}")
            logging.warning(f"Reserva {self.id_reserva} cancelada: {e}")
        except ValueError as e:
            self.estado = "Fallida"
            print(f"[Error de Cantidad]: {e}")
            logging.error(f"Reserva {self.id_reserva} fallida por valor: {e}")
        except Exception as e:
            self.estado = "Error"
            print(f"[Error Inesperado]: {e}")
            logging.critical(f"Error crítico en reserva {self.id_reserva}: {e}")
        else:
            # Se ejecuta si todo sale bien
            print(f"¡Reserva exitosa para {self.cliente.nombre}!")
            print(f"Detalle: {self.servicio.descripcion()}")
            print(f"Total a pagar: ${self.total_pagar:.2f}")
        finally:
            # Se ejecuta siempre al final de la operación
            print(f"Estado final de la reserva: [{self.estado}]")
            print("-" * 45)


# ==========================================
# 5. BLOQUE PRINCIPAL (SIMULACIÓN DE 10 OPERACIONES)
# ==========================================
if __name__ == "__main__":
    print("=== SISTEMA DE GESTIÓN SOFTWARE FJ ===\n")

    # Creamos algunos servicios de prueba
    sala = ReservaSalas("S1", "Sala de Juntas Norte", 100000.0, 15)
    equipo = AlquilerEquipos("E1", "Proyector Láser 4K", 45000.0, "Audiovisual")
    asesoria = AsesoriaEspecializada("A1", "Consultoría en Bases de Datos", 150000.0, "Sistemas")

    # Desactivamos un equipo para probar excepciones de servicios inactivos
    equipo.activo = False

    lista_operaciones = []

    # Operación 1: Reserva de sala correcta
    try:
        cli1 = Cliente("109042", "Ana Gómez", "ana.gomez@unad.edu.co")
        lista_operaciones.append(Reserva("R01", cli1, sala, 3))
    except Exception as ex:
        print(f"Error en operación 1: {ex}")

    # Operación 2: Intento con correo inválido (dispara excepción personalizada)
    try:
        cli_malo = Cliente("109043", "Carlos Pérez", "correo-sin-formato")
    except ErrorDatoInvalido as err:
        print(f"Excepción controlada en cliente: {err}\n")

    # Operación 3: Reserva de asesoría correcta
    try:
        cli2 = Cliente("109044", "Luis Torres", "luis.torres@gmail.com")
        lista_operaciones.append(Reserva("R03", cli2, asesoria, 2))
    except Exception as ex:
        print(f"Error en operación 3: {ex}")

    # Operación 4: Intento de reservar equipo inactivo
    try:
        cli3 = Cliente("109045", "Diana Rojas", "diana.rojas@unad.edu.co")
        lista_operaciones.append(Reserva("R04", cli3, equipo, 4))
    except Exception as ex:
        print(f"Error en operación 4: {ex}")

    # Operación 5: Reserva con cantidad negativa (genera error de valor)
    try:
        cli4 = Cliente("109046", "Jorge Rueda", "jorge.rueda@hotmail.com")
        lista_operaciones.append(Reserva("R05", cli4, sala, -5))
    except Exception as ex:
        print(f"Error en operación 5: {ex}")

    # Operación 6: Otra reserva de sala válida
    try:
        cli5 = Cliente("109047", "Sofía Meza", "sofia.meza@unad.edu.co")
        lista_operaciones.append(Reserva("R06", cli5, sala, 2))
    except Exception as ex:
        print(f"Error en operación 6: {ex}")

    # Operación 7: Segunda reserva de asesoría válida
    try:
        cli6 = Cliente("109048", "Mateo Castro", "mateo.castro@empresa.com")
        lista_operaciones.append(Reserva("R07", cli6, asesoria, 1))
    except Exception as ex:
        print(f"Error en operación 7: {ex}")

    # Operación 8: Intento de reserva con 0 horas (genera error)
    try:
        cli7 = Cliente("109049", "Valeria Rios", "valeria.rios@gmail.com")
        lista_operaciones.append(Reserva("R08", cli7, sala, 0))
    except Exception as ex:
        print(f"Error en operación 8: {ex}")

    # Operación 9: Reserva de asesoría con múltiples sesiones
    try:
        cli8 = Cliente("109050", "Andrés Parra", "andres.parra@unad.edu.co")
        lista_operaciones.append(Reserva("R09", cli8, asesoria, 3))
    except Exception as ex:
        print(f"Error en operación 9: {ex}")

    # Operación 10: Reserva de sala por jornada completa (8 horas)
    try:
        cli9 = Cliente("109051", "Lucía Morales", "lucia.morales@gmail.com")
        lista_operaciones.append(Reserva("R10", cli9, sala, 8))
    except Exception as ex:
        print(f"Error en operación 10: {ex}")

    # Ejecutamos todas las operaciones acumuladas de forma iterativa y polimórfica
    print("\n" + "="*15 + " EJECUTANDO PROCESAMIENTO DE RESERVAS " + "="*15)
    for operacion in lista_operaciones:
        operacion.procesar()

    print("\nSimulación completada con éxito. Revisa el archivo 'sistema_errores.log' para ver el registro de eventos y errores.")