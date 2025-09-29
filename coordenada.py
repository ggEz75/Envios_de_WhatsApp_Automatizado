import pyautogui
import time
import json
import os


def guardar_coordenada(x, y, key="message_bar"):
    base = os.path.dirname(__file__)
    path = os.path.join(base, "coords.json")
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


def captura_interactiva(poll_delay=0.1):
    """Muestra coordenadas en consola y guarda al presionar Ctrl+C."""
    print("Mueve el mouse. Presiona Ctrl+C para capturar y guardar la coordenada.")
    try:
        while True:
            x, y = pyautogui.position()
            print(f"Posición: {x}, {y}", end="\r")
            time.sleep(poll_delay)
    except KeyboardInterrupt:
        x, y = pyautogui.position()
        print(f"\nGuardando coordenada: {x}, {y}")
        guardar_coordenada(x, y)
        print("Listo.")


if __name__ == "__main__":
    captura_interactiva()