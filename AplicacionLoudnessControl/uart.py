import serial
import threading
#import main
import serial.tools.list_ports



class HandlderUART:
    def __init__(self, callback):
        self.thread_rx_uart = None
        self.serial_port = None
        self.cadenaRecibida = []
        self.callback = callback
    
    def portInit(self, port, baudrate):
        self.serial_port = serial.Serial(port, baudrate)
        self.serial_port.timeout = 0.1
        self.thread_rx_uart = threading.Thread(target=self.escuchar_uart)
        self.thread_rx_uart.daemon = True
        self.thread_rx_uart.start()

    def portClose(self):
        self.serial_port.close()

    def obtener_puertos_disponibles(self):
        puertos_disponibles = [port.device for port in serial.tools.list_ports.comports()]
        return puertos_disponibles

    def enviar_uart(self, valor):
        if 0 <= valor <= 99:
            msg = f"{int(valor)}"
            self.serial_port.write(msg.encode())

    def escuchar_uart(self):
        while True:
            data = self.serial_port.read().decode("utf-8")
            if 1:
                # Llego dato
                self.cadenaRecibida.append(data)

                # Me fijo que el primero sea un inciio de trama
                if (self.cadenaRecibida[0] != "$"):
                    self.cadenaRecibida.clear()
                    continue

                # Si solo llego el inicio de cadena salgo y espero a que lleguen más datos
                if len(self.cadenaRecibida) == 1:
                    continue

                # Me fijo que todos los demas sean un numero
                errorTrama = False
                largo = len(self.cadenaRecibida)

                for i in range(1, largo):
                    if self.cadenaRecibida[i].isdigit():
                        continue
                    elif self.cadenaRecibida[i] == "$":
                        self.cadenaRecibida.clear()
                        self.cadenaRecibida.append("$")
                        errorTrama = True
                        break
                    else:
                        self.cadenaRecibida.clear()
                        errorTrama = True
                        break
                if errorTrama:
                    continue

                # Si llegaron todos los caracteres bien devuelvo el dato y limpio registro
                if largo == 6:
                    # Extraer el valor numérico de la cadena
                    del self.cadenaRecibida[0]
                    numero = int(''.join(self.cadenaRecibida))
                    valor_float = float(numero / 1000.0)
                    self.cadenaRecibida.clear()
                    self.callback(valor_float)

    def cerrar_puerto(self):
        self.serial_port.close()
