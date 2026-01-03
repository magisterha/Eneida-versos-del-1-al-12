import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import traceback

st.title("🔍 Ultra-Diagnóstico de Errores")

URL = "https://docs.google.com/spreadsheets/d/1022thHT1sGmNBhYdty1lXLELSK6MYQWc1GaMILlzZtQ/edit?usp=sharing"

try:
    st.info("Intentando conectar con Google Sheets...")
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Intentamos leer la hoja completa para ver qué columnas detecta Python
    df = conn.read(spreadsheet=URL, ttl=0)
    
    st.success("✅ ¡Conexión establecida! Puedo leer la hoja.")
    st.write("Columnas que detecto en tu Excel:", df.columns.tolist())
    st.dataframe(df.head())

except Exception as e:
    st.error("❌ SE DETECTÓ UN ERROR TÉCNICO")
    # Esto mostrará el error real (si es de clave, de permisos o de red)
    st.exception(e) 
    st.write("---")
    st.write("Detalle completo para el desarrollador:")
    st.code(traceback.format_exc())
