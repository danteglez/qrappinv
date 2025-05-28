import streamlit as st
import qrcode
from PIL import Image
import io
import cv2
import numpy as np
from supabase_client import supabase  # importa conexión

st.title("🎓 Generador y Lector de Códigos QR")

st.header("🔧 Generar código QR")
nombre_estudiante = st.text_input("Nombre del estudiante")

if st.button("Generar QR") and nombre_estudiante:
    qr = qrcode.make(nombre_estudiante)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)

    st.image(qr, caption=f"Código QR de {nombre_estudiante}")

    # Subir a Supabase Storage
    archivo_nombre = f"{nombre_estudiante.replace(' ', '_')}.png"
    supabase.storage.from_("qr_codes").upload(archivo_nombre, buf, file_options={"content-type": "image/png"})
    st.success("✅ QR guardado en Supabase")

st.header("📷 Leer código QR desde imagen")
imagen_qr = st.file_uploader("Sube una imagen con código QR", type=["png", "jpg", "jpeg"])

if imagen_qr is not None:
    file_bytes = np.asarray(bytearray(imagen_qr.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    qr_detector = cv2.QRCodeDetector()
    data, bbox, _ = qr_detector.detectAndDecode(img)

    if bbox is not None and data:
        st.success(f"Contenido del QR: **{data}**")
        st.image(imagen_qr, caption="Imagen subida")
    else:
        st.error("No se detectó ningún código QR válido.")