import pandas as pd
import pyautogui
import pyperclip
import webbrowser
import time
import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

IMG_REFERENCIAS = [
    os.path.join(ASSETS_DIR, "numero_no_whatsapp_light.png"),
    os.path.join(ASSETS_DIR, "numero_no_whatsapp_dark.png"),
]

INVALID_LOG = os.path.join(BASE_DIR, "numeros_invalidos.txt")


# =========================
# UTILIDADES
# =========================

def normalizar_numero(numero):
    numero = ''.join(filter(str.isdigit, numero))
    if not numero.startswith("54"):
        numero = "54" + numero
    return "+" + numero


def log_numero_invalido(numero):
    with open(INVALID_LOG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {numero}\n")


def get_coords_path():
    return os.path.join(BASE_DIR, "coords.json")


def leer_excel(path):
    return pd.read_excel(path)


def generar_mensaje(template, row):
    mensaje = template
    for i, col in enumerate(row.index):
        placeholder = f"{{{{{chr(65+i)}}}}}"
        mensaje = mensaje.replace(placeholder, str(row[col]))
    return mensaje


# =========================
# DETECCIÓN VISUAL CON ESPERA INTELIGENTE
# =========================

def esperar_y_detectar(timeout=5, confidence=0.7):
    """
    Espera hasta 'timeout' segundos buscando la imagen.
    Si la encuentra devuelve True.
    Si no aparece devuelve False.
    """
    start = time.time()

    while time.time() - start < timeout:
        for img in IMG_REFERENCIAS:
            if not os.path.exists(img):
                raise Exception(f"No se encontró imagen de referencia: {img}")

            try:
                location = pyautogui.locateOnScreen(img, confidence=confidence)
                if location is not None:
                    return True
            except:
                continue

        time.sleep(0.5)

    return False


# =========================
# ENVÍO
# =========================

def enviar_mensaje(numero, mensaje, delays):

    numero = normalizar_numero(numero)
    numero_sin_mas = numero.replace("+", "")

    print(f"📨 Intentando enviar a {numero}...")

    webbrowser.open(f"whatsapp://send?phone={numero_sin_mas}")
    time.sleep(3)  # ritmo humano

    # 🔍 Espera inteligente
    if esperar_y_detectar():
        print(f"❌ {numero} no tiene WhatsApp. Se omite.")
        log_numero_invalido(numero)
        pyautogui.press("enter")  # cerrar popup
        time.sleep(1)
        return

    # Fail safe: si no pudo validar referencias
    for img in IMG_REFERENCIAS:
        if not os.path.exists(img):
            print("⚠️ No se pudo validar imágenes. Cancelando envío por seguridad.")
            return

    coords_path = get_coords_path()
    if not os.path.exists(coords_path):
        raise Exception("coords.json no encontrado.")

    with open(coords_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    mb = data.get("message_bar")
    if not mb or len(mb) < 2:
        raise Exception("Coordenada 'message_bar' inválida.")

    px, py = int(mb[0]), int(mb[1])

    pyautogui.click(px, py)
    time.sleep(2)

    pyperclip.copy(mensaje)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)
    pyautogui.press("enter")

    print(f"✅ Mensaje enviado a {numero}")


def enviar_mensajes(df, columna_numeros, mensajes, delays):
    delay_index = 0

    for idx, (_, row) in enumerate(df.iterrows()):
        try:
            numero = str(row[columna_numeros]).strip()
            template = mensajes[idx % len(mensajes)]
            mensaje = generar_mensaje(template, row)

            enviar_mensaje(numero, mensaje, delays)

            delay = delays[delay_index]
            print(f"⏳ Esperando {delay} segundos...\n")
            time.sleep(delay)

            delay_index = (delay_index + 1) % len(delays)

        except Exception as e:
            print(f"❌ Error con {numero}: {e}\n")
            continue
