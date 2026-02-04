import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
import os
import threading
import time
import json
import pyautogui
from backend import leer_excel, enviar_mensajes, get_coords_path

# Configuramos tema oscuro global
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")  # tema base, se puede personalizar luego

class WhatsAppBotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Envío de WhatsApp Automático")
        self.geometry("700x900")
        self.minsize(600, 500)

        self.df = None
        self.delay_inputs = []
        self.message_bar_coord = None
        # Placeholder para las cajas de mensaje
        self.message_placeholder = "También puedes usar campos/datos de las COLUMNAS usando {{A}}, {{B}}, Excluyendo la fila 1(Encabezados)."

        # Colores estilo WhatsApp
        self.color_btn = "#237942"
        self.color_btn_hover = "#1ebe57"
        self.color_btn_pressed = "#127065"

        self.setup_ui()

    def setup_ui(self):
        # Contenedor principal con scroll vertical
        self.main_scroll = ctk.CTkScrollableFrame(master=self, width=660, height=780)
        self.main_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        # Botón cargar Excel
        self.btn_excel = ctk.CTkButton(
            master=self.main_scroll,
            text="📁 Cargar Excel",
            fg_color=self.color_btn,
            hover_color=self.color_btn_hover,
            corner_radius=15,
            font=("Segoe UI", 14, "bold"),
            command=self.cargar_excel
        )
        self.btn_excel.pack(pady=(20, 10), padx=20)

        # Label archivo cargado
        self.lbl_excel = ctk.CTkLabel(
            master=self.main_scroll,
            text="Ningún archivo seleccionado.",
            font=("Segoe UI", 12)
        )
        self.lbl_excel.pack()

        # Label y caja mensaje
        self.lbl_mensaje = ctk.CTkLabel(
            master=self.main_scroll,
            text="✍️ Escribe el/los mensaje(s):",
            font=("Segoe UI", 13)
        )

        # Scrollable frame para los mensajes y el botón +
        self.frame_mensajes = ctk.CTkScrollableFrame(master=self.main_scroll, width=640, height=220)
        self.frame_mensajes.pack(padx=20, fill="x", pady=(0, 10))

        self.text_mensajes = []
        self.btn_agregar_mensaje = ctk.CTkButton(
            master=self.frame_mensajes,
            text="+",
            width=30,
            height=30,
            fg_color=self.color_btn,
            hover_color=self.color_btn_hover,
            corner_radius=10,
            font=("Segoe UI", 18, "bold"),
            command=self.agregar_textarea_mensaje
        )
        self.lbl_mensaje.pack(pady=(10, 5), padx=20)
        self.agregar_textarea_mensaje()  # Agrega el primer textarea

        # Frame para delays
        self.frame_delays = ctk.CTkFrame(master=self.main_scroll)
        self.frame_delays.pack(pady=15, fill="x", padx=20)

        self.lbl_delays = ctk.CTkLabel(
            master=self.frame_delays,
            text="⏱️ Segundos por mensaje:",
            font=("Segoe UI", 12)
        )
        self.lbl_delays.grid(row=0, column=0, sticky="w", padx=(5, 15))

        self.btn_agregar_delay = ctk.CTkButton(
            master=self.frame_delays,
            text="+",
            width=30,
            height=30,
            fg_color=self.color_btn,
            hover_color=self.color_btn_hover,
            corner_radius=10,
            font=("Segoe UI", 18, "bold"),
            command=self.agregar_input_delay
        )
        self.btn_agregar_delay.grid(row=0, column=99, sticky="e", padx=5)

        self.delay_inputs = []

        # Añadir tooltip helpers
        def _add_tooltip(widget, text):
            tip = {"win": None}
            def show(e):
                if tip["win"]:
                    return
                x = widget.winfo_rootx() + 20
                y = widget.winfo_rooty() + widget.winfo_height() + 6
                tip["win"] = ctk.CTkToplevel(self)
                tip["win"].overrideredirect(True)
                tip["win"].attributes("-topmost", True)
                lbl = ctk.CTkLabel(tip["win"], text=text, font=("Segoe UI", 10))
                lbl.pack(padx=6, pady=3)
                tip["win"].geometry(f"+{x}+{y}")
            def hide(e):
                if tip["win"]:
                    try:
                        tip["win"].destroy()
                    except Exception:
                        pass
                    tip["win"] = None
            widget.bind("<Enter>", show)
            widget.bind("<Leave>", hide)

        # Tooltip para botón delays
        _add_tooltip(self.btn_agregar_delay, "Cuando más intervalos tenga, más indetectable será el programa y reducirá el riesgo de bloqueo por spam.")

    # Empacar el botón de enviar debajo de los segundos por mensaje
        self.btn_enviar = ctk.CTkButton(
            master=self.main_scroll,
            text="� Iniciar envío",
            fg_color=self.color_btn,
            hover_color=self.color_btn_hover,
            corner_radius=15,
            font=("Segoe UI", 16, "bold"),
            command=self.iniciar_envio
        )
        self.btn_enviar.pack(pady=12, padx=20)

        # Validación de coordenadas: si faltan, deshabilitar botón de envío
        def coords_exist():
            try:
                path = get_coords_path()
                if not os.path.exists(path):
                    return False
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                mb = data.get("message_bar")
                if not (mb and isinstance(mb, (list, tuple)) and len(mb) >= 2):
                    return False
                return True
            except Exception:
                return False

        if not coords_exist():
            self.btn_enviar.configure(state="disabled")


        # Tooltip para botón agregar mensaje
        _add_tooltip(self.btn_agregar_mensaje, "Agregar más mensajes diferentes ayuda a evitar la detección de spam y reduce el riesgo de bloqueo del número.")

        # Botón para añadir coordenada de la barra de mensaje
        self.btn_coordenada = ctk.CTkButton(
            master=self.main_scroll,
            text="📍 Añadir coordenada de BARRA DE MENSAJE",
            fg_color="#4a4a4a",
            hover_color="#5a5a5a",
            corner_radius=12,
            font=("Segoe UI", 12, "bold"),
            command=lambda: self.abrir_ventana_coordenada(key="message_bar", label_widget=self.lbl_coord, title="Capturar coordenada de BARRA DE MENSAJE")
        )
        self.btn_coordenada.pack(pady=(5, 15), padx=20)

        # Label para mostrar coordenada seleccionada
        self.lbl_coord = ctk.CTkLabel(master=self.main_scroll, text="Coordenada: (no definida)", font=("Segoe UI", 11))
        self.lbl_coord.pack()

    def agregar_textarea_mensaje(self):
        # Crea un nuevo textarea y lo agrega al frame
        textarea = ctk.CTkTextbox(
            master=self.frame_mensajes,
            height=80,
            font=("Segoe UI Emoji", 12)
        )
        textarea.pack(pady=5, fill="x")
        # insertar placeholder y vincular eventos para comportamiento tipo placeholder
        textarea.insert("1.0", self.message_placeholder)
        # intentar aplicar color gris para placeholder (si CTkTextbox soporta text_color)
        try:
            textarea.configure(text_color="#9e9e9e")
        except Exception:
            pass

        def on_focus_in(event, box=textarea):
            text = box.get("1.0", "end-1c")
            if text.strip() == self.message_placeholder:
                box.delete("1.0", "end")
                try:
                    box.configure(text_color="#ffffff")
                except Exception:
                    pass

        def on_focus_out(event, box=textarea):
            text = box.get("1.0", "end-1c")
            if not text.strip():
                box.delete("1.0", "end")
                box.insert("1.0", self.message_placeholder)
                try:
                    box.configure(text_color="#9e9e9e")
                except Exception:
                    pass

        # Bindings de foco
        textarea.bind("<FocusIn>", on_focus_in)
        textarea.bind("<FocusOut>", on_focus_out)

        self.text_mensajes.append(textarea)
        # Mueve el botón "+" al final
        self.btn_agregar_mensaje.pack_forget()
        self.btn_agregar_mensaje.pack(pady=5)

    def cargar_excel(self):
        archivo = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not archivo:
            return

        try:
            self.df = leer_excel(archivo)
            self.lbl_excel.configure(text=f"✅ Cargado: {os.path.basename(archivo)}", text_color="#2ecc71")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        columnas = list(self.df.columns)
        self.selected_columna.set(columnas[0])

        if self.columnas_dropdown:
            self.columnas_dropdown.destroy()

        # Dropdown adaptado a customtkinter: colocarlo debajo del area de mensajes con etiqueta explicativa
        frame_col = ctk.CTkFrame(master=self.main_scroll)
        frame_col.pack(pady=10, padx=20, fill="x")

        lbl_help = ctk.CTkLabel(master=frame_col, text='Selecciona la columna de Telefono (Formato: Sin "+54 9")', font=("Segoe UI", 11))
        lbl_help.pack(side="left", padx=(0, 12))

        self.columnas_dropdown = ctk.CTkOptionMenu(
            master=frame_col,
            values=columnas,
            variable=self.selected_columna,
            font=("Segoe UI", 12),
            dropdown_font=("Segoe UI", 12)
        )
        self.columnas_dropdown.pack(side="left")

        self.lbl_mensaje.pack(pady=(10, 5), padx=20)
        self.frame_mensajes.pack(padx=20, fill="x")
        # Limpiar textareas previos y agregar uno nuevo
        for t in self.text_mensajes:
            t.destroy()
        self.text_mensajes.clear()
        self.agregar_textarea_mensaje()

    def agregar_input_delay(self):
        entry = ctk.CTkEntry(
            master=self.frame_delays,
            width=50,
            font=("Segoe UI", 12),
            justify="center"
        )
        entry.insert(0, "60")
        col_index = len(self.delay_inputs) + 1
        entry.grid(row=0, column=col_index, padx=5, pady=5)
        self.delay_inputs.append(entry)

    def abrir_ventana_coordenada(self, key="message_bar", label_widget=None, title="Capturar coordenada"):
        """Abre una ventana que muestra la posición del mouse en vivo y permite capturarla.
        Guarda la coordenada en coords.json bajo la llave `key` y actualiza la label pasada en `label_widget`.
        """
        top = ctk.CTkToplevel(self)
        top.title(title)
        top.geometry("460x180")
        # Hacer la ventana topmost para sobreponerse a otras ventanas
        try:
            top.attributes("-topmost", True)
        except Exception:
            pass

        # No usar grab_set para permitir que el usuario haga click en otras ventanas

        lbl_inst = ctk.CTkLabel(top, text="Mueve el mouse hasta el objetivo.\nAl seleccionar 'Capturar en 10s' colocar el cursor en la correspondiente sección.",
                    font=("Segoe UI", 11), justify="left")
        lbl_inst.pack(pady=(10, 5), padx=10)

        lbl_pos = ctk.CTkLabel(top, text="Posición: - , -", font=("Segoe UI", 12, "bold"))
        lbl_pos.pack(pady=(0, 10))

        stop_event = threading.Event()

        def actualizar():
            while not stop_event.is_set():
                x, y = pyautogui.position()
                lbl_pos.configure(text=f"Posición: {x}, {y}")
                time.sleep(0.08)

        def capturar(event=None):
            stop_event.set()
            x, y = pyautogui.position()
            # guardar en coords.json en el directorio del script
            try:
                path = get_coords_path()
                data = {}
                if os.path.exists(path):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                    except Exception:
                        data = {}
                data[key] = [int(x), int(y)]
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la coordenada: {e}")
            if label_widget is not None:
                # marcar en verde para indicar confirmación
                try:
                    label_widget.configure(text=f"{title}: {(int(x), int(y))}", text_color="#2ecc71")
                except Exception:
                    label_widget.configure(text=f"{title}: {(int(x), int(y))}")
            # si ya existe message_bar, habilitar el botón de envío
            try:
                path = get_coords_path()
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                mb = data.get("message_bar")
                if mb and isinstance(mb, (list, tuple)) and len(mb) >= 2:
                    try:
                        self.btn_enviar.configure(state="normal")
                    except Exception:
                        pass
            except Exception:
                pass
            top.destroy()

        def cancelar():
            stop_event.set()
            top.destroy()

        # Botones
        btn_frame = ctk.CTkFrame(top)
        btn_frame.pack(pady=(0, 8))
        # label para mostrar countdown / estado
        lbl_count = ctk.CTkLabel(btn_frame, text="", font=("Segoe UI", 12, "bold"))
        lbl_count.grid(row=0, column=0, padx=8)
        btn_cancel = ctk.CTkButton(btn_frame, text="Cancelar", fg_color="#a33", command=cancelar, width=100)
        btn_cancel.grid(row=0, column=1, padx=8)

        # Botón: captura con cuenta regresiva (10s) para permitir interaccion fuera de la ventana
        def captura_con_delay(sec=10):
            def worker():
                for i in range(sec, 0, -1):
                    try:
                        lbl_count.configure(text=f"Capturando en: {i}s")
                    except Exception:
                        pass
                    time.sleep(1)
                try:
                    lbl_count.configure(text="Capturando...")
                except Exception:
                    pass
                capturar()
                try:
                    lbl_count.configure(text="Coordenada capturada")
                except Exception:
                    pass
            t = threading.Thread(target=worker, daemon=True)
            t.start()

        btn_delay = ctk.CTkButton(btn_frame, text="Capturar en 10s", command=lambda: captura_con_delay(10), width=160)
        btn_delay.grid(row=0, column=2, padx=8)

        # vincular F8 y F9 para iniciar la captura con cuenta regresiva de 10s
        top.bind_all('<F8>', lambda e: captura_con_delay(10))
        top.bind_all('<F9>', lambda e: captura_con_delay(10))

        t = threading.Thread(target=actualizar, daemon=True)
        t.start()

    def iniciar_envio(self):
        if self.df is None:
            messagebox.showwarning("Atención", "Primero debes cargar un archivo Excel.")
            return

        columna = self.selected_columna.get()
        mensajes = []
        for t in self.text_mensajes:
            text = t.get("1.0", "end").strip()
            if not text:
                continue
            if text == self.message_placeholder:
                continue
            mensajes.append(text)
        if not mensajes:
            messagebox.showwarning("Atención", "Debes escribir al menos un mensaje.")
            return

        delays = []
        for d in self.delay_inputs:
            try:
                delays.append(int(d.get()))
            except ValueError:
                continue

        if not delays:
            messagebox.showwarning("Atención", "Debes ingresar al menos un tiempo válido de espera.")
            return

        enviar_mensajes(self.df, columna, mensajes, delays)
        messagebox.showinfo("Completado", "✅ Todos los mensajes fueron enviados.")

if __name__ == "__main__":
    app = WhatsAppBotApp()
    app.mainloop()
