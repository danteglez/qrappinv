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

def ver_qrs_alumnos():
    st.title("Códigos QR de Alumnos")
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
    opciones = ["Registrar Alumno", "Ver Asistencias", "Ver QRs de Alumnos"]
    seleccion = st.sidebar.selectbox("Menú", opciones)

    if seleccion == "Registrar Alumno":
        registrar_alumno()
    elif seleccion == "Ver Asistencias":
        ver_asistencias()
    elif seleccion == "Ver QRs de Alumnos":
        ver_qrs_alumnos()

if __name__ == "__main__":
    main()
