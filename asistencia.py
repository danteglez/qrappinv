import streamlit as st
import psycopg2
import cv2
import numpy as np
from PIL import Image
import io

DB_URL = "postgresql://postgres.avxyefrckoynbubddwhl:Dokiringuillas1@aws-0-us-east-2.pooler.supabase.com:6543/postgres"

def connect_db():
    try:
        return psycopg2.connect(DB_URL)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def leer_qr_opencv(image_file):
    try:
        image = Image.open(image_file).convert("RGB")
        image_np = np.array(image)
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(image_bgr)
        return data if data else None
    except Exception as e:
        st.error(f"Error al procesar la imagen: {e}")
        return None

def tomar_asistencia_con_camara_simple():
    st.title("Tomar Asistencia Automática con Cámara")

    foto = st.camera_input("Toma una foto del código QR")

    if foto:
        st.image(foto, caption="Imagen capturada")
        codigo = leer_qr_opencv(foto)

        if codigo:
            conn = connect_db()
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT nombre FROM alumnos WHERE matricula = %s", (codigo,))
                alumno = cur.fetchone()
                if alumno:
                    cur.execute("INSERT INTO asistencias (matricula) VALUES (%s)", (codigo,))
                    conn.commit()
                    st.success(f"Asistencia registrada automáticamente para {alumno[0]} ({codigo})")
                else:
                    st.error("Matrícula no registrada")
                cur.close()
                conn.close()
        else:
            st.warning("No se detectó ningún código QR en la imagen.")

if __name__ == "__main__":
    tomar_asistencia_con_camara_simple()
