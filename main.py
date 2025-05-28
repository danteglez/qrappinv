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
    st.title("Registrar Alumno")
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

def ver_asistencias():
    st.title("Lista de Asistencias")
    conn = connect_db()
    if conn:
        df = pd.read_sql("""
            SELECT a.nombre, a.matricula, s.fecha, s.hora
            FROM asistencias s
            JOIN alumnos a ON s.matricula = a.matricula
            ORDER BY s.fecha DESC, s.hora DESC
        """, conn)
        conn.close()
        st.dataframe(df)

def main():
    st.title("Sistema de Asistencia por QR")
    opciones = ["Tomar Asistencia", "Registrar Alumno", "Ver Asistencias"]
    seleccion = st.sidebar.selectbox("Menú", opciones)

    if seleccion == "Tomar Asistencia":
        tomar_asistencia_con_camara_simple()
    elif seleccion == "Registrar Alumno":
        registrar_alumno()
    elif seleccion == "Ver Asistencias":
        ver_asistencias()

if __name__ == "__main__":
    main()
