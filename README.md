📲 Envios de WhatsApp Automatizado

Aplicación de escritorio para enviar mensajes personalizados de WhatsApp Desktop a partir de un archivo Excel, con validación automática de números inexistentes y comportamiento diseñado para simular interacción humana.

🚀 Características

📄 Carga de contactos desde Excel

✍️ Mensajes dinámicos con placeholders {{A}}, {{B}}, {{C}}

🔍 Detección automática de números sin WhatsApp

🌗 Compatible con modo claro y oscuro

⏳ Sistema de delays rotativos (anti-spam)

📍 Captura interactiva de coordenadas

📝 Registro automático de números inválidos

🖥️ Generación de ejecutable portable (.exe)

🗂 Estructura del Proyecto
frontend.py      → Interfaz gráfica (CustomTkinter)
backend.py       → Lógica principal de envío y validación
coordenada.py    → Captura manual de coordenadas por consola
coords.json      → Guarda posición de la barra de mensaje
icono.ico        → Icono de la aplicación
requirements.txt → Dependencias del proyecto
assets/          → Imágenes de detección visual

⚙️ Requisitos

Python 3.10 o superior

Windows 10 / 11

WhatsApp Desktop instalado

Escala de pantalla recomendada: 100%

📦 Instalación

Se recomienda usar entorno virtual:

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

▶️ Uso

Ejecutar la aplicación:

python frontend.py

Flujo de trabajo

📍 Capturar coordenada de la barra de mensaje.

📁 Cargar archivo Excel.

🔢 Seleccionar columna de números.

✍️ Escribir mensajes con placeholders.

⏳ Configurar tiempos de espera.

▶️ Iniciar envío.

🧩 Sistema de Placeholders

Los mensajes permiten sustitución dinámica basada en columnas del Excel:

{{A}} → Primera columna
{{B}} → Segunda columna
{{C}} → Tercera columna


Ejemplo:

Hola {{A}}, tu pedido estará listo el {{B}}.

🔍 Validación de Números Inexistentes

El sistema:

Abre el chat en WhatsApp Desktop.

Espera carga natural (~3 segundos).

Analiza la pantalla.

Compara con imágenes de referencia (assets/).

Si detecta número inválido:

Cancela envío

Registra en archivo de log

Continúa con el siguiente contacto

Esto evita enviar mensajes al último chat abierto.

📄 Formato del Excel

Primera fila: encabezados.

Columna de números: sin símbolos obligatorios.

El sistema:

Elimina espacios y guiones

Normaliza el número

Añade prefijo +54 si no existe

📦 Generar Ejecutable (.exe)

Instalar PyInstaller:

pip install pyinstaller


Generar versión portable:

pyinstaller --onefile --noconsole --name "EnvioWhatsApp" --icon=icono.ico --add-data "assets;assets" frontend.py


El ejecutable se generará en:

dist/EnvioWhatsApp.exe

🛡 Consideraciones de Seguridad

No mover el mouse durante el envío.

Mantener WhatsApp visible.

No minimizar la ventana.

Evitar envíos masivos en corto tiempo.

Usar delays variables para reducir detección automatizada.

El sistema prioriza comportamiento humano sobre velocidad.

⚠️ Uso Responsable

Este proyecto está destinado a:

Automatización personal

Comunicación controlada

Uso educativo

No se promueve spam ni uso indebido de la plataforma.

El uso es responsabilidad del usuario.