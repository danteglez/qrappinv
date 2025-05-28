import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from supabase import create_client

# Supabase setup
url = "https://avxyefrckoynbubddwhl.supabase.co"  # Este es tu Project URL
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF2eHllZnJja295bmJ1YmRkd2hsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODM4ODQ3MCwiZXhwIjoyMDYzOTY0NDcwfQ.WC0RvJyNlGM_yxXzmCo4BHBtxUiJMkesg1TbLyOCp_k"

supabase = create_client(url, key)

st.title("🎟️ Generador de QR para Asistencias")

# Input para generar QR
input_text = st.text_input("🔤 Ingrese el ID del evento/código:", value="Evento123")

if st.button("Generar QR"):
    qr_url = f"https://TU_BACKEND_URL.com/registrar?id_qr={input_text}"
    qr = qrcode.make(qr_url)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), caption=qr_url)

st.divider()

st.title("📋 Registros de Asistencia")
response = supabase.table("asistencias").select("*").order("timestamp", desc=True).execute()

if response.data:
    df = pd.DataFrame(response.data)
    st.dataframe(df[["id_qr", "timestamp"]])
else:
    st.info("No hay asistencias registradas aún.")
