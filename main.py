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

def generar_qr_bytes(codigo):
    qr = qrcode.make(codigo)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    return buffer.getvalue()

def registrar_alumno():
    st.header("Registrar Alumno")
    matricula = st.text_input("Matrícula del alumno:")
    nombre = st.text_input("Nombre del alumno:")

    if st.button("Guardar Alumno"):
        if matricula and nombre:
            conn = connect_db()
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT matricula FROM alumnos WHERE matricula = %s", (matricula,))
                if cur.fetchone():
                    st.error("La matrícula ya está registrada.")
                else:
                    qr_bytes = generar_qr_bytes(matricula)
                    cur.execute("INSERT INTO alumnos (matricula, nombre, qr) VALUES (%s, %s, %s)",
                                (matricula, nombre, psycopg2.Binary(qr_bytes)))
                    conn.commit()
                    st.success("Alumno registrado exitosamente")
                    st.image(qr_bytes, caption="Código QR del alumno")
                cur.close()
                conn.close()

def tomar_asistencia_con_camara_simple():
    st.header("Tomar Asistencia")
    st.info("Toma una foto del código QR del alumno y escribe el código leído.")
    foto = st.camera_input("Tomar foto del QR")

    if foto:
        st.image(foto, caption="Imagen capturada")
        st.info("Escribe el código que aparece en el QR (ej. matrícula):")

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

def ver_qrs_alumnos():
    st.header("Códigos QR de Alumnos")
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT matricula, nombre, qr FROM alumnos ORDER BY nombre")
        alumnos = cur.fetchall()
        cur.close()
        conn.close()

        if alumnos:
            for matricula, nombre, qr_bytes in alumnos:
                with st.expander(f"{nombre} ({matricula})"):
                    if qr_bytes:
                        try:
                            img = Image.open(io.BytesIO(qr_bytes))
                            st.image(img, caption=f"QR de {nombre}", width=150)
                        except:
                            st.warning("No se pudo mostrar el QR.")
                    else:
                        st.warning("No hay QR disponible para este alumno.")
        else:
            st.info("No hay alumnos registrados.")

def main():
    st.title("Sistema de Asistencia por QR")

    # Leer parámetros de la URL
    query_params = st.query_params
    page = query_params.get("page", ["registrar"])[0]  # por defecto: registrar

    # Mostrar navegación básica
    st.markdown("""
    ### Navegación
    [Registrar Alumno](?page=registrar) | 
    [Tomar Asistencia](?page=asistencia) | 
    [Ver QRs](?page=qrs)
    """)

    # Navegación basada en URL
    if page == "registrar":
        registrar_alumno()
    elif page == "asistencia":
        tomar_asistencia_con_camara_simple()
    elif page == "qrs":
        ver_qrs_alumnos()
    else:
        st.warning("Página no encontrada")

if __name__ == "__main__":
    main()
