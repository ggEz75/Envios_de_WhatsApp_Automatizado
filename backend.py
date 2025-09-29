# backend.py
import pandas as pd
import pyautogui
import pyperclip
import webbrowser
import time
import os
import json

def leer_excel(path):
    try:
        df = pd.read_excel(path)
        return df
    except Exception as e:
        raise Exception(f"No se pudo leer el Excel: {e}")

def generar_mensaje(template, row):
    mensaje = template
    for i, valor in enumerate(row):
        placeholder = f"{{{{{chr(65+i)}}}}}"  # {{A}}, {{B}}, ...
        mensaje = mensaje.replace(placeholder, str(valor))
    return mensaje

def enviar_mensaje(numero, mensaje, delays, archivo=None):
    if not numero.startswith('+'):
        numero = '+54' + numero
    numero_sin_mas = numero.replace('+', '')

    print(f"Enviando a {numero}...")
    webbrowser.open(f"whatsapp://send?phone={numero_sin_mas}")
    time.sleep(3)  # Espera para que se abra el chat

    # Haz clic en el área de texto para asegurar el foco
    # Intentar leer coordenada desde coords.json; si no existe, usar valor por defecto
    base = os.path.dirname(__file__)
    coords_path = os.path.join(base, "coords.json")
    # ahora las coordenadas deben ser manejadas por el usuario en coords.json
    if not os.path.exists(coords_path):
        raise Exception("coords.json no encontrado. Debes definir la coordenada 'message_bar' usando la interfaz.")
    with open(coords_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    mb = data.get("message_bar")
    if not (mb and isinstance(mb, (list, tuple)) and len(mb) >= 2):
        raise Exception("Coordenada 'message_bar' inválida o no encontrada en coords.json. Usa la interfaz para configurarla.")
    px, py = int(mb[0]), int(mb[1])

    pyautogui.click(x=px, y=py)
    time.sleep(3)  # Espera para que el cursor esté listo

    pyperclip.copy(mensaje)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(2)  # Espera para asegurar que el mensaje se pegó

    pyautogui.press("enter")

    if archivo:
        time.sleep(2)
        # Leer coordenadas del clip y del botón de archivo desde coords.json
        # Leer coordenadas del clip y del botón de archivo desde coords.json — el usuario las debe gestionar
        base = os.path.dirname(__file__)
        coords_path = os.path.join(base, "coords.json")
        if not os.path.exists(coords_path):
            raise Exception("coords.json no encontrado. Debes definir 'clip' y 'file_button' usando la interfaz.")
        with open(coords_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        c = data.get("clip")
        fbtn = data.get("file_button")
        if not (c and isinstance(c, (list, tuple)) and len(c) >= 2):
            raise Exception("Coordenada 'clip' inválida o no encontrada en coords.json. Usa la interfaz para configurarla.")
        if not (fbtn and isinstance(fbtn, (list, tuple)) and len(fbtn) >= 2):
            raise Exception("Coordenada 'file_button' inválida o no encontrada en coords.json. Usa la interfaz para configurarla.")
        clip_coord = (int(c[0]), int(c[1]))
        file_button_coord = (int(fbtn[0]), int(fbtn[1]))

        pyautogui.click(x=clip_coord[0], y=clip_coord[1])  # Coordenadas del clip
        time.sleep(1)
        # Hacer DOS clics en el botón de archivo (para probar doble-clic)
        try:
            pyautogui.click(x=file_button_coord[0], y=file_button_coord[1], clicks=2, interval=0.2)
        except TypeError:
            # Si la versión de pyautogui no soporta clicks arg, hacer dos clicks manuales
            pyautogui.click(x=file_button_coord[0], y=file_button_coord[1])
            time.sleep(0.2)
            pyautogui.click(x=file_button_coord[0], y=file_button_coord[1])
        time.sleep(2)

        pyperclip.copy(os.path.basename(archivo))
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(1)
        pyautogui.press("enter")

def enviar_mensajes(df, columna_numeros, mensajes, delays, archivo=None):
    delay_index = 0
    num_mensajes = len(mensajes)
    for idx, (index, row) in enumerate(df.iterrows()):
        try:
            numero = str(row[columna_numeros]).strip()
            # Selecciona el mensaje correspondiente de la lista, en modo cíclico
            template = mensajes[idx % num_mensajes]
            mensaje = generar_mensaje(template, row)
            enviar_mensaje(numero, mensaje, delays, archivo)
            delay = delays[delay_index]
            print(f"Esperando {delay} segundos...")
            time.sleep(delay)
            delay_index = (delay_index + 1) % len(delays)
        except Exception as e:
            print(f"❌ Error con {numero}: {e}")
            continue
