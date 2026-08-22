# 📡 Convertidor Droid-ADIF.

> **Convierte tus registros de APRSDroid en un archivo ADIF válido para QRZ.com, LoTW, Log de Argentina (LDA) y más.**

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
![Flet](https://img.shields.io/badge/UI-Flet_0.80.2-purple?style=for-the-badge)
![Platform](https://img.shields.io/badge/Plataforma-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Language](https://img.shields.io/badge/Idioma-Español-red?style=for-the-badge)

---

## 🛠️ Descripción

**Droid-ADIF** es una herramienta de escritorio desarrollada en Python que permite procesar  
y filtrar el archivo de log generado por la aplicación APRSDroid, transformando los paquetes  
en un registro estándar ADIF listo para subir a plataformas.  
Compatible con QRZ / LDA / QSL WEB CREATOR y tantos otros

Elimina datos duplicados, filtra balizas irrelevantes para dejar solo contactos válidos y  
ajusta automáticamente la zona horaria a UTC de acuerdo a su elección.

---

⚙️ Lógica de Conversión
Un registro típico de APRSDroid contiene marcas de tiempo seguidas del paquete TNC2:
2026-07-20 14:30:25 R: LU1ABC-9>APDR15,TCPIP*,qAC,T2ARG:=...

El programa procesa estas entradas aplicando los siguientes pasos:

🔍 Extracción : Parseando el log línea por línea capturando la fecha, hora e indicativo (callsign) emisor.

🧹 Filtrado de Mensajes para evitar registrar balizas como QSOs.

🏷️ Limpieza de SSID: Remueve automáticamente los identificadores de SSID (ej. LU6EGD-10 se convierte en LU6EGD).

🕒 Conversión Local a UTC: Aplica el offset de la diferencia horaria seleccionado para a tiempo UTC. 
  
📄 Formato ADIF Estándar: Genera la sintaxis requerida (ej. <CALL:6>LU1ABC).

---

📖 Guía Paso a Paso  
1️⃣ Abre la aplicación y haz clic en Seleccionar para cargar tu log de APRSDroid.  
2️⃣ Ingresa tu Indicativo.  
3️⃣ Selecciona la frecuencia APRS (144.390 MHz o 430.930 MHz en Argentina).  
4️⃣ Ajusta la diferencia horaria (Offset). Por defecto es 3 (UTC-3 / Argentina).  
5️⃣ Presiona GENERAR ADIF.  


Al finalizar, la aplicación generará automáticamente un archivo de igual nombre.adi  
en el mismo directorio y mostrará en la pantalla de "Resultado de Proceso" el resumen  
de los registros procesados y QSOs válidos.

---

## 🚀 Instalación y Uso Rápido

### Opción 1: Ejecutable (Sin instalación)
1️⃣ Descarga la última versión de `droid-adif.exe`.  
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
python droid-adif.py
