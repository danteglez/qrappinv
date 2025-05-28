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

# Input para QR
input_qr = st.text_input("🔤 Código único del QR (por ejemplo: Evento123):", value="Evento123")
descripcion = st.text_input("📝 Descripción del QR (opcional):", value="Clase de Matemáticas")

if st.button("Generar y guardar QR"):
    # Guarda en Supabase la info del QR
    result = supabase.table("codigos_qr").insert({
        "id_qr": input_qr,
        "descripcion": descripcion
    }).execute()

    if result.data:
        # Genera el QR con el link para registrar asistencia
        qr_url = f"https://TU_BACKEND_URL.com/registrar?id_qr={input_qr}"
        qr = qrcode.make(qr_url)
        buf = BytesIO()
        qr.save(buf)
        st.image(buf.getvalue(), caption=f"QR para: {input_qr}")
        st.success("✅ QR guardado y generado con éxito")
    else:
        st.error("⚠️ Ya existe un QR con ese código.")