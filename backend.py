# backend.py
import pandas as pd
import pyautogui
import pyperclip
import webbrowser
import time
import os
import sys
import json


def get_coords_path():
    """Devuelve la ruta para coords.json en el directorio del script."""
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "coords.json")

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

def enviar_mensaje(numero, mensaje, delays):
    if not numero.startswith('+'):
        numero = '+54' + numero
    numero_sin_mas = numero.replace('+', '')

    print(f"Enviando a {numero}...")
    webbrowser.open(f"whatsapp://send?phone={numero_sin_mas}")
    time.sleep(3)  # Espera para que se abra el chat

    coords_path = get_coords_path()
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

def enviar_mensajes(df, columna_numeros, mensajes, delays):
    delay_index = 0
    num_mensajes = len(mensajes)
    for idx, (index, row) in enumerate(df.iterrows()):
        try:
            numero = str(row[columna_numeros]).strip()
            # Selecciona el mensaje correspondiente de la lista, en modo cíclico
            template = mensajes[idx % num_mensajes]
            mensaje = generar_mensaje(template, row)
            enviar_mensaje(numero, mensaje, delays)
            delay = delays[delay_index]
            print(f"Esperando {delay} segundos...")
            time.sleep(delay)
            delay_index = (delay_index + 1) % len(delays)
        except Exception as e:
            print(f"❌ Error con {numero}: {e}")
            continue
