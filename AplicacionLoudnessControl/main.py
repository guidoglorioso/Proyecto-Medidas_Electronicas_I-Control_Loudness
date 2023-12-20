import threading
import time
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import csv
from uart import HandlderUART

MAX_LEN = 75

BAUDRATE = 115200

NOMBRE_ARCHIVO_LOUDNESS_UC = "loudnessESP.csv"

threadsToKill = []


class InterfazGrafica:
    def __init__(self, ventana):
        # UI
        self.ventana = ventana
        self.ventana.title("App - Medición Loudness")

        # Estado del ploteo
        self.registro_activado = False

        # ESP
        self.handlerUart = HandlderUART(self.callbackRx)
        self.conectado = False
        self.listaLoudnessESP = []
        self.listaLoudnessTiempo = []

        ################################
        # Sección 0: Selección de puerto COM
        ################################
        self.frame_seccion0 = ttk.Frame(self.ventana, padding="10")
        self.frame_seccion0.grid(row=0, column=0, columnspan=1, padx=10, pady=10, sticky="nsew")

        self.label_puerto_com = ttk.Label(self.frame_seccion0, text="Seleccionar Puerto COM:")
        self.label_puerto_com.grid(row=0, column=0, padx=5, pady=5)

        self.puertos_com = self.handlerUart.obtener_puertos_disponibles()
        self.puerto_com_seleccionado = tk.StringVar()
        self.combobox_puertos = ttk.Combobox(self.frame_seccion0, textvariable=self.puerto_com_seleccionado,
                                             values=self.puertos_com)
        self.combobox_puertos.grid(row=1, column=0, padx=5, pady=5)

        self.boton_conectar = ttk.Button(self.frame_seccion0, text="Conectar", command=self.conectar_puerto)
        self.boton_conectar.grid(row=2, column=0, padx=5, pady=5)

        ################################
        # Sección 1: Seteo de Loudness Referencia
        ################################
        self.frame_seccion1 = ttk.Frame(self.ventana, padding="10")
        self.frame_seccion1.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.slider = ttk.Scale(self.frame_seccion1, from_=10, to=70, orient="horizontal", length=200)
        self.slider.grid(row=0, column=0, padx=5, pady=5)
        self.slider.bind("<Motion>", self.actualizar_label)
        self.slider.set(40)
        self.slider.config(state="disabled")

        self.label_valor = ttk.Label(self.frame_seccion1, text="Valor: 40 LFKS")
        self.label_valor.grid(row=1, column=0, padx=5, pady=5)

        self.pulsadorSetpoint = ttk.Button(self.frame_seccion1, text="Cambiar Setpoint", command=self.enviar_por_uart)
        self.pulsadorSetpoint.grid(row=2, column=0, padx=5, pady=5)
        self.pulsadorSetpoint.config(state="disabled")

        ################################
        # Sección 2: Ploteo de informacion que tiene el micro vs mediciones
        ################################
        self.frame_seccion2 = ttk.Frame(self.ventana, padding="10")
        self.frame_seccion2.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        # Botón para Iniciar/Parar Ploteo
        self.boton_iniciar_parar = ttk.Button(self.ventana, text="Iniciar Ploteo", command=self.iniciar_parar_registro)
        self.boton_iniciar_parar.grid(row=1, column=2, columnspan=2, pady=10)
        self.boton_iniciar_parar.config(state="disabled")

        ################################
        # Tiempos para el grafico
        ################################
        self.tiempoRef = None
        self.lastTime = None

        ####################################
        # Inicializo gráfico
        ####################################
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_seccion2)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.generar_grafico()
        self.habPlot = False
        self.threadGrafico = threading.Thread(target=self.actualizar_grafico)
        threadsToKill.append(self.threadGrafico)
        self.threadGrafico.start()

    #######################################
    # Slot para botones de conectar UART
    #######################################
    def conectar_puerto(self):
        if not self.conectado:
            self.conectado = True
            puerto_seleccionado = self.puerto_com_seleccionado.get()
            self.handlerUart.portInit(puerto_seleccionado, BAUDRATE)
            self.boton_iniciar_parar.config(state="enabled")
            self.pulsadorSetpoint.config(state="enabled")
            self.combobox_puertos.config(state="disabled")
            self.boton_conectar.config(text="desconectar")
            self.slider.config(state="enabled")

        else:
            self.conectado = False
            self.handlerUart.portClose()
            self.boton_iniciar_parar.config(state="disabled")
            self.pulsadorSetpoint.config(state="disabled")
            self.combobox_puertos.config(state="enabled")
            self.slider.config(state="disabled")
            self.boton_conectar.config(text="conectar")



    #######################################
    # Callback Uart
    #######################################
    def callbackRx(self, data):
        if self.registro_activado:
            if len(self.listaLoudnessESP) == 0:
                self.tiempoRef = time.time()
            currentTime = time.time()

            tiempoMuestra = currentTime - self.tiempoRef

            self.lastTime = tiempoMuestra
            self.listaLoudnessESP.append(data)
            self.listaLoudnessTiempo.append(tiempoMuestra)

    #######################################
    # Métodos sección 1
    #######################################
    def enviar_por_uart(self):
        valor = self.slider.get()
        self.handlerUart.enviar_uart(valor)

    def actualizar_label(self, event):
        valor = self.slider.get()
        self.label_valor.config(text=f"Valor: {int(valor)} LFKS")

    #######################################
    # Métodos sección 2
    #######################################
    def iniciar_parar_registro(self):
        if not self.registro_activado:
            self.registro_activado = True
            self.boton_iniciar_parar.config(text="Parar Ploteo")
            self.listaLoudnessESP.clear()
            self.listaLoudnessTiempo.clear()

        else:
            self.registro_activado = False
            self.boton_iniciar_parar.config(text="Iniciar Ploteo")
            self.escribir_csv_LoudnessESP()

    def actualizar_grafico(self):
        while True:
            copiaArrayLoudness = self.listaLoudnessESP
            ejeTiempo = self.listaLoudnessTiempo
            tiempoActual = self.lastTime
            i = 0
            for tiempo in ejeTiempo:
                # Si abarca mas de 30seg sigo
                if tiempoActual - tiempo > 30:
                    i += 1
                    continue
                # Si abarca menos salgo
                break

            copiaArrayLoudness = copiaArrayLoudness[i::]
            ejeTiempo = ejeTiempo[i::]

            self.ax.clear()
            self.ax.plot(ejeTiempo, copiaArrayLoudness, label="Loudness ESP")
            self.ax.set_title('Loudness ESP')
            self.ax.set_xlabel('Tiempo[seg]')
            self.ax.set_ylabel('Loudness[LKFS]')
            self.ax.legend()
            self.canvas.draw()
            time.sleep(0.5)

    def generar_grafico(self):
        self.ax.clear()
        self.ax.set_title('Loudness ESP')
        self.ax.set_xlabel('Tiempo[seg]')
        self.ax.set_ylabel('Loudness[LKFS]')
        self.canvas.draw()

    def escribir_csv_LoudnessESP(self):
        ejeTiempo = self.listaLoudnessTiempo
        ejeLoudness = self.listaLoudnessESP
        datos = list(zip(ejeTiempo,ejeLoudness))
        with open(NOMBRE_ARCHIVO_LOUDNESS_UC, 'w', newline='') as archivo_csv:
            escritor = csv.writer(archivo_csv)
            escritor.writerow(['Tiempo', 'Loudness'])
            escritor.writerows(datos)

    def ajustar_longitud(self, lista):
        if len(lista) > MAX_LEN:
            exceso = len(lista) - MAX_LEN
            return lista[exceso:len(lista)]
        return lista


if __name__ == "__main__":
    ventana_principal = tk.Tk()
    ventana_principal.geometry("1200x600")
    ventana_principal.resizable(width=False, height=False)
    interfaz = InterfazGrafica(ventana_principal)
    ventana_principal.mainloop()

    # Elimino threads que quedaron
    for myThread in threadsToKill:
        myThread.join(0)
