import streamlit as st
import qrcode
import io
from PIL import Image
import numpy as np
import cv2
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
from supabase_client import supabase  # ← se importa desde archivo separado

st.set_page_config(page_title="QR Estudiantes", layout="centered")
st.title("🎓 QR Estudiantes")

# --- Generar QR ---
st.header("🔧 Generar código QR")
nombre_estudiante = st.text_input("Nombre del estudiante")

if st.button("Generar QR") and nombre_estudiante:
    qr = qrcode.make(nombre_estudiante)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)

    archivo_nombre = f"{nombre_estudiante.replace(' ', '_')}.png"
    st.image(buf, caption=f"Código QR de {nombre_estudiante}")

    # Subir a Supabase Storage
    supabase.storage.from_("qr_codes").upload(
        archivo_nombre, buf, file_options={"content-type": "image/png"}
    )

    # URL pública del QR
    public_url = f"https://avxyefrckoynbubddwhl.supabase.co/storage/v1/object/public/qr_codes/{archivo_nombre}"

    # Insertar en base de datos
    supabase.table("qr_estudiantes").insert({
        "nombre": nombre_estudiante,
        "archivo_qr": archivo_nombre,
        "url_qr": public_url
    }).execute()

    st.success("✅ QR generado y guardado en Supabase")

# --- Escanear QR desde cámara ---
st.header("📷 Escanear QR en tiempo real")

class QRScanner(VideoTransformerBase):
    def __init__(self):
        self.detector = cv2.QRCodeDetector()
        self.last_data = ""

    def transform(self, frame: av.VideoFrame):
        image = frame.to_ndarray(format="bgr24")
        data, bbox, _ = self.detector.detectAndDecode(image)

        if data:
            self.last_data = data
            cv2.putText(image, f"{data}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return image

ctx = webrtc_streamer(
    key="qr-scan",
    video_transformer_factory=QRScanner,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

if ctx.video_transformer and ctx.video_transformer.last_data:
    st.success(f"🔍 Código QR detectado: **{ctx.video_transformer.last_data}**")
