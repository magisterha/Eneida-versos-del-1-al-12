import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title("🔥 Prueba de Fuego: Escritura")

# URL de tu hoja (la he copiado de tu mensaje anterior)
URL = "https://docs.google.com/spreadsheets/d/1022thHT1sGmNBhYdty1lXLELSK6MYQWc1GaMILlzZtQ/edit?usp=sharing"

if st.button("ESCRIBIR DATO DE PRUEBA"):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # 1. Leemos lo que hay
        df = conn.read(spreadsheet=URL, usecols=[0, 1], ttl=0)
        st.write("✅ Lectura correcta. Filas actuales:", len(df))
        
        # 2. Preparamos dato nuevo
        nuevo_dato = pd.DataFrame([["PRUEBA_SISTEMA", "FUNCIONA"]], columns=df.columns)
        
        # 3. Pegamos y Guardamos
        df_final = pd.concat([df, nuevo_dato], ignore_index=True)
        conn.update(spreadsheet=URL, data=df_final)
        
        st.success("🎉 ¡EXITO! He escrito en la hoja. Ve a comprobarlo.")
        st.balloons()
        
    except Exception as e:
        st.error("❌ ERROR FATAL")
        st.code(str(e)) # Esto nos dirá EXACTAMENTE qué pasa
