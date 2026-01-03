import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.title("🕵️‍♂️ Diagnóstico de Conexión Google Sheets")

# 1. VERIFICACIÓN DE IDENTIDAD
st.header("1. ¿Quién soy?")
try:
    # Intentamos leer el email del robot desde los Secretos
    # Nota: Dependiendo de cómo copiaste el TOML, puede estar en [connections.gsheets] o suelto.
    email_robot = st.secrets.get("connections", {}).get("gsheets", {}).get("client_email")
    
    if not email_robot:
        # Intento alternativo por si el formato TOML es distinto
        email_robot = st.secrets.get("client_email")
        
    if email_robot:
        st.success(f"🤖 El Robot se identifica como:\n\n`{email_robot}`")
        st.info("👉 **ACCIÓN REQUERIDA:** Ve a tu Google Sheet > Compartir. ¿Está ESTE correo exacto en la lista como **EDITOR**?")
    else:
        st.error("❌ No encuentro el 'client_email' en tus Secrets. Revisa el formato TOML.")
except Exception as e:
    st.error(f"Error leyendo secrets: {e}")

# 2. VERIFICACIÓN DE LECTURA
st.header("2. Prueba de Lectura")
URL_HOJA = "https://docs.google.com/spreadsheets/d/1022thHT1sGmNBhYdty1lXLELSK6MYQWc1GaMILlzZtQ/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=URL_HOJA, ttl=0) # ttl=0 fuerza lectura real
    
    st.write("✅ **Lectura Exitosa.** Así ve Python tu hoja ahora mismo:")
    st.dataframe(df)
    
    # Análisis de Columnas
    cols = df.columns.tolist()
    st.write(f"Columnas detectadas: `{cols}`")
    
    if len(cols) < 2:
        st.warning("⚠️ Veo menos de 2 columnas. Necesitas 'Pregunta' y 'Respuesta'.")
    else:
        st.success("Estuctura de columnas correcta.")

except Exception as e:
    st.error(f"❌ FALLO DE LECTURA: {e}")
    st.stop() # Si no lee, no intentamos escribir

# 3. VERIFICACIÓN DE ESCRITURA
st.header("3. Prueba de Escritura")
if st.button("🔴 Intentar Escribir una Fila de Prueba"):
    try:
        # Preparamos datos de prueba
        fecha = datetime.now().strftime("%H:%M:%S")
        nueva_fila = pd.DataFrame([["TEST_PREGUNTA_" + fecha, "TEST_RESPUESTA_" + fecha]], columns=df.columns[:2])
        
        # Unimos
        df_nuevo = pd.concat([df, nueva_fila], ignore_index=True)
        
        # Escribimos
        conn.update(spreadsheet=URL_HOJA, data=df_nuevo)
        st.success("🎉 ¡ÉXITO! Se ha escrito una fila en tu hoja. El sistema funciona.")
        st.balloons()
    except Exception as e:
        st.error("❌ FALLO DE ESCRITURA (CRÍTICO)")
        st.error(f"El error exacto es: {e}")
        st.markdown("""
        **Causas probables:**
        1. El robot (email de arriba) está como **Lector** y no como **Editor**.
        2. Has superado la cuota de la API (raro).
        3. El formato de columnas no coincide.
        """)
