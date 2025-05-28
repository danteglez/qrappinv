import streamlit as st
import psycopg2
import pandas as pd
import qrcode
import io
from PIL import Image

DB_URL = "postgresql://postgres.avxyefrckoynbubddwhl:Dokiringuillas1@aws-0-us-east-2.pooler.supabase.com:6543/postgres"

def connect_db():
    try:
        return psycopg2.connect(DB_URL)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def tomar_asistencia_con_camara_simple():
    st.title("Tomar Asistencia con Cámara")
    st.write("Toma una foto del código QR del alumno. Luego ingresa manualmente el código leído.")

    foto = st.camera_input("Tomar foto del QR")

    if foto:
        st.image(foto, caption="Imagen capturada")
        st.info("Ahora escribe el código que aparece en el QR de la imagen (ej. matrícula):")

    codigo = st.text_input("Código leído del QR")

    if st.button("Registrar Asistencia"):
        if codigo:
            conn = connect_db()
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT nombre FROM alumnos WHERE matricula = %s", (codigo,))
                alumno = cur.fetchone()
                if alumno:
                    cur.execute("INSERT INTO asistencias (matricula) VALUES (%s)", (codigo,))
                    conn.commit()
                    st.success(f"Asistencia registrada para {alumno[0]} ({codigo})")
                else:
                    st.error("Matrícula no registrada")
                cur.close()
                conn.close()