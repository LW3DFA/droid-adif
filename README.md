# 📡 APRSDroid ADIF Converter

> **Convierte tus registros de APRSDroid en un archivo ADIF válido para QRZ.com, LoTW, Log de Argentina (LDA) y más.**

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
![Flet](https://img.shields.io/badge/UI-Flet_0.80.2-purple?style=for-the-badge)
![Platform](https://img.shields.io/badge/Plataforma-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Language](https://img.shields.io/badge/Idioma-Español-red?style=for-the-badge)

---

## 🛠️ Descripción

**APRSDroid-ADIF** es una herramienta de escritorio desarrollada en Python que permite procesar y filtrar el 
archivo de log generado por la aplicación APRSDroid, transformando paquetes TNC2 en bruto en un registro 
estándar ADIF listo para subir a plataformas de libro de guardia en línea.

El proyecto está diseñado pensando en la simplicidad: elimina datos duplicados, filtra balizas irrelevantes 
para dejar solo contactos válidos y ajusta automáticamente la zona horaria a UTC.

---

⚙️ Lógica de Conversión
Un registro típico de APRSDroid contiene marcas de tiempo seguidas del paquete TNC2:
2026-07-20 14:30:25 R: LU1ABC-9>APDR15,TCPIP*,qAC,T2ARG:=...

El programa procesa estas entradas aplicando los siguientes pasos:

🔍 Extracción (Regex): Parsea el log línea por línea capturando la fecha, hora e indicativo (callsign) emisor.

🧹 Filtrado de Mensajes (Opcional): Para evitar registrar meras balizas de posición como QSOs, el sistema incluye 
  un filtro opcional que solo captura paquetes con mensajes de texto (:: en el payload).

🔄 Deduplicación: Filtra redundancias de APRS conservando únicamente un contacto por estación por día.

🏷️ Limpieza de SSID: Remueve automáticamente los identificadores de SSID (ej. LU9DUV-5 se convierte en LU9DUV).

🕒 Conversión Local a UTC: Aplica el offset de zona horaria seleccionado para ajustar el timestamp a tiempo UTC 
   de forma automática.

📄 Formateo ADIF Estándar: Genera la sintaxis requerida (ej. <CALL:6>LU1ABC).

---

📖 Guía Paso a Paso  
1️⃣ Abre la aplicación y haz clic en Buscar para seleccionar tu archivo de log de APRSDroid.  
2️⃣ Ajusta la diferencia horaria (Offset). Por defecto es 3 (UTC-3 / Argentina).  
3️⃣ Selecciona la frecuencia de operación (144.390 MHz o 430.930 MHz).  
4️⃣ Presiona Convertir a ADIF.  


Al finalizar, la aplicación generará automáticamente un archivo .adi en el mismo directorio con el resumen de 
registros procesados y QSOs válidos.

---

## 🚀 Instalación y Uso Rápido

### Opción 1: Ejecutable (Sin instalación)
1️⃣ Descarga la última versión de `aprsdroid-adif.exe`.  
2️⃣ Haz doble clic para ejecutar (compatible con Windows 7 en adelante).  

### Opción 2: Ejecutar desde el Código Fuente
**Pre-requisitos:** Tener instalado Python 3.x.

---

🚧 Estado del Proyecto
Interfaz de Usuario: En desarrollo activo.

🌎 Soporte de Idiomas:   
Actualmente disponible solo en Español.   
Soporte multi-idioma próximamente.

```bash
# Clonar o descargar el repositorio y ejecutar:
python aprsdroid-adif.py
