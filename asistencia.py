import streamlit as st
import psycopg2
from PIL import Image
import cv2
import numpy as np

DB_URL = "postgresql://postgres.avxyefrckoynbubddwhl:Dokiringuillas1@aws-0-us-east-2.pooler.supabase.com:6543/postgres"

def connect_db():
    try:
        return psycopg2.connect(DB_URL)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def escanear_qr_desde_imagen(img):
    detector = cv2.QRCodeDetector()
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    data, bbox, _ = detector.detectAndDecode(img_cv)
    return data if data else None

def tomar_asistencia_con_camara_simple():
    st.title("Tomar Asistencia Automática con Cámara")
    st.write("Toma una foto del código QR del alumno para registrar su asistencia automáticamente.")

    foto = st.camera_input("Tomar o subir imagen del QR")

    if foto:
        img = Image.open(foto)
        codigo = escanear_qr_desde_imagen(img)

        if codigo:
            conn = connect_db()
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT nombre FROM alumnos WHERE matricula = %s", (codigo,))
                alumno = cur.fetchone()
                if alumno:
                    st.success(f"Alumno detectado: {alumno[0]} ({codigo})")

                    # Mostrar campo de comentario
                    comentario = st.text_area("Comentario (opcional):", key="comentario_texto")

                    if st.button("Registrar asistencia"):
                        try:
                            # Insertar asistencia
                            cur.execute("INSERT INTO asistencias (matricula) VALUES (%s) RETURNING id", (codigo,))
                            asistencia_id = cur.fetchone()[0]

                            # Insertar comentario si existe
                            if comentario.strip():
                                cur.execute(
                                    "INSERT INTO comentarios_asistencia (asistencia_id, comentario) VALUES (%s, %s)",
                                    (asistencia_id, comentario.strip())
                                )

                            conn.commit()
                            st.success("Asistencia y comentario registrados correctamente.")
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Error al registrar la asistencia: {e}")
                        finally:
                            cur.close()
                            conn.close()
                else:
                    st.error("Matrícula no registrada")
        else:
            st.error("No se detectó ningún código QR en la imagen.")

if __name__ == "__main__":
    tomar_asistencia_con_camara_simple()
