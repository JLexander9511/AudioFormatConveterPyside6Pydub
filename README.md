# 🔊 AudioFormatConverterPySide6Pydub

Un conversor de formatos de audio **multiplataforma** desarrollado con **PySide6** para la interfaz gráfica y **pydub** para el procesamiento de audio.

---

## 💻 Características Principales

* **Conversión de Formatos:** Soporta una amplia gama de formatos de audio (sujeto a las capacidades de **FFmpeg**).
* **Interfaz Gráfica (GUI):** Desarrollado con **PySide6** para una experiencia de usuario intuitiva.
* **Empaquetado Sencillo:** Puede ser empaquetado como un ejecutable independiente usando **PyInstaller**.

---

## 🛠️ Requisitos Obligatorios

Para que esta aplicación funcione correctamente, es **obligatorio** tener instalado el códec **FFmpeg** en tu sistema.

### **FFmpeg**

**FFmpeg** es la base para la codificación y decodificación de audio que utiliza `pydub`. 

[Image of FFmpeg logo]


* **Instalación en Linux (Ejemplo Debian/Ubuntu):**
    ```bash
    sudo apt update
    sudo apt install ffmpeg
    ```
* **Instalación en macOS (usando Homebrew):**
    ```bash
    brew install ffmpeg
    ```
* **Instalación en Windows:** Descarga los binarios desde el [sitio oficial de FFmpeg](https://ffmpeg.org/download.html) y asegúrate de añadir la carpeta `bin` a la variable de entorno **PATH** de tu sistema.

---

## 🚀 Instalación y Uso

### **1. Configuración del Entorno Virtual (Recomendado)**

```bash
python -m venv venv
source venv/bin/activate  # En Linux/macOS
# o
.\venv\Scripts\activate   # En Windows
```
## Creditos

Proyecto hecho como recurso didactico para la materia Lenguajes de programacion II, por el profesor Jesus Piñate

