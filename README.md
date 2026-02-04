# Envío de WhatsApp Automático

Este proyecto es una herramienta para enviar mensajes de WhatsApp automáticamente desde un archivo Excel. La aplicación proporciona una interfaz gráfica para: cargar un archivo Excel, definir mensajes (con soporte para placeholders {{A}}, {{B}}, ...), capturar la coordenada de la barra de mensajes en pantalla, y ejecutar el envío automático mediante la app de WhatsApp Desktop.

Contenido
- `frontend.py`: Interfaz gráfica (CustomTkinter). Permite capturar coordenadas y configurar mensajes y tiempos.
- `backend.py`: Lógica de envío: abre el chat de WhatsApp y pega el mensaje.
- `coordenada.py`: Utilidad CLI para capturar coordenadas desde la consola (presiona Ctrl+C para guardar la coordenada en `coords.json`).
- `coords.json`: Archivo JSON donde se guardan las coordenadas capturadas por la interfaz. (No debe versionarse si contiene datos sensibles).

Requisitos
- Python 3.10+ (se recomienda 3.11+)
- Windows (probado en Windows 10/11)

Dependencias
- customtkinter
- pyautogui
- pyperclip
- pandas

Sugerencia: crea un entorno virtual antes de instalar dependencias.

Instalación rápida (PowerShell)

```powershell
cd "C:\Users\..."
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Uso
1. Ejecuta la interfaz:

```powershell
python frontend.py
```

2. En la ventana principal:
- Pulsa "📍 Añadir coordenada de BARRA DE MENSAJE" y usa la ventana emergente para capturar la coordenada. Coloca el cursor sobre la barra de texto de WhatsApp y presiona el botón "Capturar en 10s" (o presiona F8/F9 para iniciar la cuenta regresiva).
- Carga tu archivo Excel con el botón "📁 Cargar Excel". Selecciona la columna que contiene los números (sin +54 9) en el dropdown.
- Escribe los mensajes en los textareas. Puedes usar placeholders: `{{A}}`, `{{B}}`, ... para sustituir por valores de columnas (A = primera columna, B = segunda, etc.).
- Define los retrasos (en segundos) en la sección "Segundos por mensaje". Puedes añadir varios valores para rotarlos y reducir detectabilidad.
- Pulsa "Iniciar envío". La app abrirá cada chat y enviará los mensajes.

Notas de seguridad y permisos
- `pyautogui` controla el ratón y teclado: evita mover accidentalmente el ratón mientras corre el envío. Considera ejecutar en una sesión dedicada.
- Windows puede solicitar permisos de control de entrada o UAC. Asegúrate de ejecutar con los permisos necesarios.

Formato del Excel
- La primera fila se interpreta como encabezados. Los placeholders `{{A}}`, `{{B}}`, ... reemplazarán con el valor de cada columna para cada fila.
- La columna de números debe contener números sin prefijo + o con el formato regional que prefieras; el script prepende `+54` si el número no comienza con `+`.

Archivo `coords.json`
- Contiene las coordenadas guardadas desde la interfaz. Ejemplo:

```json
{
  "message_bar": [587, 1013]
}
```

Troubleshooting (problemas comunes)
- Ventana emergente de captura vacía o sin widgets: asegúrate de tener la versión de `customtkinter` compatible y que la app no lance excepciones en el terminal. Revisa la salida de `python frontend.py` para tracebacks.
- `pyautogui` no funciona correctamente: instala las dependencias del sistema que `pyautogui` requiera y evita mover el ratón mientras se realiza la captura.
- Imports no resueltos en el editor: instala dependencias en el mismo intérprete que usa tu editor/IDE.

Mejoras sugeridas
- Implementar un placeholder visual robusto (overlay) para garantizar compatibilidad entre versiones de CustomTkinter.
- Añadir un test harness que simule envíos sin abrir WhatsApp para pruebas locales.

Licencia y uso
- Proyecto para uso personal/educativo. No incentivar spam ni usos maliciosos. Usa con responsabilidad.