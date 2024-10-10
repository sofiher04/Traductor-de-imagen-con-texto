import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator
import base64

st.title("Reconocimiento Óptico de Caracteres con Traducción y Audio")
st.subheader("Sube una imagen o toma una foto y traduce el texto detectado")

# Crear carpeta "temp" si no existe
try:
    os.mkdir("temp")
except FileExistsError:
    pass

# Opción para tomar una foto o cargar una imagen
cam_option = st.radio("Selecciona una opción", ("Tomar Foto", "Subir Archivo"))

if cam_option == "Tomar Foto":
    img_file_buffer = st.camera_input("Toma una Foto")
else:
    img_file_buffer = st.file_uploader("Cargar Imagen:", type=["png", "jpg", "jpeg"])

# Opción de aplicar filtro
if img_file_buffer is not None:
    # Leer imagen desde buffer
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    # Opción de filtro en la barra lateral
    apply_filter = st.sidebar.checkbox("Aplicar Filtro")
    if apply_filter:
        cv2_img = cv2.bitwise_not(cv2_img)

    # Mostrar la imagen procesada
    st.image(cv2_img, caption='Imagen Procesada', use_column_width=True)

    # Realizar OCR en la imagen
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    detected_text = pytesseract.image_to_string(img_rgb)
    st.markdown("### Texto Detectado:")
    st.write(detected_text)

    # Opciones de idioma de entrada y salida
    st.sidebar.subheader("Opciones de Traducción")
    translator = Translator()

    input_language = st.sidebar.selectbox("Idioma de Entrada", ["Inglés", "Español", "Francés", "Alemán", "Italiano"])
    lang_dict = {"Inglés": "en", "Español": "es", "Francés": "fr", "Alemán": "de", "Italiano": "it"}
    input_lang_code = lang_dict[input_language]

    output_language = st.sidebar.selectbox("Idioma de Salida", ["Inglés", "Español", "Francés", "Alemán", "Italiano"])
    output_lang_code = lang_dict[output_language]

    # Convertir texto detectado a audio
    if st.button("Traducir y Convertir a Audio"):
        translated_text = translator.translate(detected_text, src=input_lang_code, dest=output_lang_code).text
        st.markdown("### Texto Traducido:")
        st.write(translated_text)

        tts = gTTS(translated_text, lang=output_lang_code)
        audio_file_name = "audio_output.mp3"
        tts.save(f"temp/{audio_file_name}")

        # Reproducir el archivo de audio
        audio_file = open(f"temp/{audio_file_name}", "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3")

        # Opción de descarga del archivo de audio
        b64 = base64.b64encode(audio_bytes).decode()
        download_link = f'<a href="data:audio/mp3;base64,{b64}" download="{audio_file_name}">Descargar archivo de audio</a>'
        st.markdown(download_link, unsafe_allow_html=True)

# Función para eliminar archivos antiguos
def remove_old_files(folder, days):
    now = time.time()
    cutoff = now - (days * 86400)
    files = glob.glob(os.path.join(folder, "*"))
    for file in files:
        if os.path.getmtime(file) < cutoff:
            os.remove(file)
            print(f"Deleted old file: {file}")

# Eliminar archivos en la carpeta "temp" después de 7 días
remove_old_files("temp", 7)
