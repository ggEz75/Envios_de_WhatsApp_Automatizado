import pandas as pd
import pyautogui
import pyperclip
import webbrowser
import time
import os
import json


# =========================
# Configuración
# =========================

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
IMG_NUMERO_NO_WHATSAPP = os.path.join(ASSETS_DIR, "numero_no_whatsapp.png")


# =========================
# Utilidades
# =========================

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
    # Usamos el orden real de las columnas para evitar errores silenciosos
    for i, col in enumerate(row.index):
        placeholder = f"{{{{{chr(65+i)}}}}}"  # {{A}}, {{B}}, ...
        mensaje = mensaje.replace(placeholder, str(row[col]))
    return mensaje


# =========================
# Detección visual
# =========================

def numero_no_existe():
    """
    Devuelve True si aparece el popup de
    'El número no está en WhatsApp'
    """
    try:
        return pyautogui.locateOnScreen(
            IMG_NUMERO_NO_WHATSAPP,
            confidence=0.8
        ) is not None
    except Exception:
        return False


# =========================
# Envío de mensajes
# =========================

def enviar_mensaje(numero, mensaje, delays):
    if not numero.startswith('+'):
        numero = '+54' + numero

    numero_sin_mas = numero.replace('+', '')
    print(f"📨 Intentando enviar a {numero}...")

    # Abrir chat
    webbrowser.open(f"whatsapp://send?phone={numero_sin_mas}")
    time.sleep(3)

    # ⛔ Detección de número inexistente
    if numero_no_existe():
        print(f"❌ El número {numero} no tiene WhatsApp. Se omite.")
        # cerrar popup (Enter equivale a OK)
        pyautogui.press("enter")
        time.sleep(1)
        return

    # Cargar coordenadas
    coords_path = get_coords_path()
    if not os.path.exists(coords_path):
        raise Exception(
            "coords.json no encontrado. Debes definir la coordenada 'message_bar' usando la interfaz."
        )

    with open(coords_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    mb = data.get("message_bar")
    if not (mb and isinstance(mb, (list, tuple)) and len(mb) >= 2):
        raise Exception(
            "Coordenada 'message_bar' inválida o no encontrada en coords.json."
        )

    px, py = int(mb[0]), int(mb[1])

    # Click en la barra de mensaje
    pyautogui.click(x=px, y=py)
    time.sleep(2)

    # Escribir y enviar mensaje
    pyperclip.copy(mensaje)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)
    pyautogui.press("enter")

    print(f"✅ Mensaje enviado a {numero}")


def enviar_mensajes(df, columna_numeros, mensajes, delays):
    delay_index = 0
    num_mensajes = len(mensajes)

    for idx, (_, row) in enumerate(df.iterrows()):
        try:
            numero = str(row[columna_numeros]).strip()
            template = mensajes[idx % num_mensajes]
            mensaje = generar_mensaje(template, row)

            enviar_mensaje(numero, mensaje, delays)

            delay = delays[delay_index]
            print(f"⏳ Esperando {delay} segundos...\n")
            time.sleep(delay)

            delay_index = (delay_index + 1) % len(delays)

        except Exception as e:
            print(f"❌ Error con {numero}: {e}\n")
            continue
