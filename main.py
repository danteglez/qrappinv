import streamlit as st
import pandas as pd
from supabase import create_client

# Configuración de Supabase
url = "https://avxyefrckoynbubddwhl.supabase.co"  # Este es tu Project URL
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF2eHllZnJja295bmJ1YmRkd2hsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODM4ODQ3MCwiZXhwIjoyMDYzOTY0NDcwfQ.WC0RvJyNlGM_yxXzmCo4BHBtxUiJMkesg1TbLyOCp_k"

supabase = create_client(url, key)

st.title("📋 Registro de Asistencias")

# Leer los datos de la tabla 'asistencias'
response = supabase.table("asistencias").select("*").order("timestamp", desc=True).execute()

if response.data:
    df = pd.DataFrame(response.data)
    st.dataframe(df[["id_qr", "timestamp"]])
else:
    st.info("No hay asistencias registradas aún.")
