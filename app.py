import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Aeneis Tutor AI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 🚨 CONFIGURACIÓN DE LA BASE DE DATOS
# ---------------------------------------------------------
URL_HOJA_CALCULO = "https://docs.google.com/spreadsheets/d/1022thHT1sGmNBhYdty1lXLELSK6MYQWc1GaMILlzZtQ/edit?usp=sharing"

# --- 2. DICCIONARIO DE TRADUCCIONES ---
TRADUCCIONES = {
    "Español": {
        "sidebar_title": "🏛️ Configuración",
        "lang_label": "Idioma del Tutor:",
        "reset_btn": "🔄 Reiniciar Consulta",
        "header": "P. Vergili Maronis: Aeneis (I, 1-11)",
        "chat_header": "💬 Consulta Filológica Libre",
        "welcome": "### 🏛️ ¡Salve!\nHe configurado mi sistema para ayudarte en **Español**. ¿Qué palabra o verso deseas analizar?",
        "input_placeholder": "Pregúntale a la IA (ej. cano, arma, virum...)",
        "spinner": "Analizando...",
        "error_api": "🏛️ El oráculo está saturado. Espera un momento.",
        "sticky_note": "📍 Texto fijo para consulta permanente.",
        "cta_btn": "🏛️ Reserva una clase con un profesor de latín"
    },
    # ... (Mantenemos el resto de idiomas igual para ahorrar espacio) ...
    "English": {"sidebar_title": "Settings", "lang_label": "Language:", "reset_btn": "Reset", "header": "Aeneid (I, 1-11)", "chat_header": "Consultation", "welcome": "### Salve!", "input_placeholder": "Ask...", "spinner": "...", "error_api": "Error", "sticky_note": "Note", "cta_btn": "Book Class"},
    "Latine": {"sidebar_title": "Configuratio", "lang_label": "Lingua:", "reset_btn": "Iterare", "header": "Aeneid (I, 1-11)", "chat_header": "Colloquium", "welcome": "### Salve!", "input_placeholder": "Interrogā...", "spinner": "...", "error_api": "Error", "sticky_note": "Nota", "cta_btn": "Schola"},
    "繁體中文 (Taiwan)": {"sidebar_title": "設定", "lang_label": "語言:", "reset_btn": "重置", "header": "埃涅阿斯紀", "chat_header": "諮詢", "welcome": "### 您好!", "input_placeholder": "詢問...", "spinner": "...", "error_api": "錯誤", "sticky_note": "備註", "cta_btn": "預約"}
}

# --- 3. FUNCIONES DE MEMORIA (CORREGIDAS) ---

def buscar_en_base_datos(pregunta_usuario):
    """Busca coincidencias flexibles en ambas direcciones."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # ttl=0 es vital para que no lea datos viejos
        df = conn.read(spreadsheet=URL_HOJA_CALCULO, usecols=[0, 1], ttl=0)
        df = df.dropna(how="all") # Limpiamos filas vacías
        
        pregunta_usuario = pregunta_usuario.lower().strip()
        
        for index, row in df.iterrows():
            pregunta_db = str(row.iloc[0]).lower().strip()
            respuesta_db = str(row.iloc[1])
            
            # --- CORRECCIÓN LÓGICA ---
            # Miramos si A está en B ... O SI ... B está en A
            # Esto soluciona el problema de "cano" vs "¿Qué significa cano?"
            if (pregunta_usuario in pregunta_db) or (pregunta_db in pregunta_usuario):
                return respuesta_db
                
        return None
    except Exception as e:
        print(f"Error lectura: {e}") # Esto sale en la consola del desarrollador
        return None

def guardar_nueva_entrada(pregunta, respuesta):
    """Guarda datos y maneja errores de permisos."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=URL_HOJA_CALCULO, usecols=[0, 1], ttl=0)
        df = df.dropna(how="all")
        
        # Preparamos la nueva fila asegurando que coincida con las columnas existentes
        nueva_fila = pd.DataFrame([[pregunta, respuesta]], columns=df.columns)
        df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
        
        # Intentamos actualizar
        conn.update(spreadsheet=URL_HOJA_CALCULO, data=df_actualizado)
        return True
    except Exception as e:
        st.error(f"❌ Error CRÍTICO al guardar: {e}")
        st.info("💡 PISTA: Verifica que el email del robot tenga permiso de 'EDITOR' en la hoja de cálculo.")
        return False

# --- 4. DISEÑO ---
st.markdown("""
    <style>
    [data-testid="column"]:nth-of-type(1) { position: sticky; top: 2rem; align-self: flex-start; }
    .verse-line { font-family: 'Times New Roman', serif; font-size: 1.4rem; line-height: 1.7; color: #2c3e50; }
    .main-header { color: #8e44ad; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    idioma_app = st.selectbox("Language / Idioma / 語言", list(TRADUCCIONES.keys()))
    t = TRADUCCIONES[idioma_app]
    st.title(t["sidebar_title"])
    if st.button(t["reset_btn"]):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    with st.expander("💾 Estado del Sistema"):
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            # Solo leemos para ver si conecta
            test_df = conn.read(spreadsheet=URL_HOJA_CALCULO, usecols=[0,1], ttl=0)
            st.success(f"✅ Conectado a DB ({len(test_df)} entradas)")
        except Exception as e:
            st.error("❌ Error de Conexión")
            st.caption(f"Detalle: {e}")

# --- 6. CONFIGURACIÓN GEMINI ---
@st.cache_data
def load_prompt(url):
    try:
        r = requests.get(url)
        return r.text if r.status_code == 200 else "Expert Latin Philologist Role."
    except: return "Expert Latin Philologist Role."

PROMPT_URL = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/prompt_maestro.txt"
sys_instruction = load_prompt(PROMPT_URL)

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-lite-preview-02-05",
        system_instruction=sys_instruction
    )
else:
    st.error("⚠️ Falta la API KEY en Secrets.")
    st.stop()

# --- 7. INTERFAZ ---
col_txt, col_chat = st.columns([1, 1], gap="large")

with col_txt:
    st.markdown(f"<h2 class='main-header'>{t['header']}</h2>", unsafe_allow_html=True)
    st.write("---")
    versos = ["1. Arma virumque canō, Trōiae quī prīmus ab ōrīs", "2. Ītaliam, fātō profugus, Lāvīniaque vēnit", "3. lītora, multum ille et terrīs iactātus et altō", "4. vī superum saevae memorem Iūnōnis ob īram;", "5. multa quoque et bellō passus, dum conderet urbem,", "6. inferretque deōs Latiō, genus unde Latīnum,", "7. Albānīque patrēs, atque altae moenia Rōmae.", "8. Mūsa, mihī causās memorā, quō nūmine laesō,", "9. quidve dolēns, rēgīna deum tot volvere cāsūs", "10. īnsīgnem pietāte virum, tot adīre labōrēs", "11. impulerit. Tantaene animīs caelestibus īrae?"]
    for v in versos: st.markdown(f'<p class="verse-line">{v}</p>', unsafe_allow_html=True)
    st.caption(t["sticky_note"])

with col_chat:
    st.subheader(t["chat_header"])
    chat_container = st.container(height=550, border=True)

    if "messages" not in st.session_state or len(st.session_state.messages) == 0:
        st.session_state.messages = [{"role": "assistant", "content": t["welcome"]}]

    with chat_container:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

    # --- 8. LÓGICA PRINCIPAL ---
    if prompt := st.chat_input(t["input_placeholder"]):
        # 1. Mostrar usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                # A) INTENTO DE MEMORIA
                respuesta_db = buscar_en_base_datos(prompt)
                
                if respuesta_db:
                    st.success("📚 Respuesta recuperada de tu Base de Conocimiento")
                    st.markdown(respuesta_db)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta_db})
                
                else:
                    # B) INTENTO DE IA
                    try:
                        # Historial corto
                        history = [{"role": "model" if m["role"]=="assistant" else "user", "parts": [m["content"]]} 
                                   for m in st.session_state.messages[-6:-1]]
                        
                        full_query = f"[Language: {idioma_app}] [Context: Latin Aeneid] {prompt}"
                        
                        chat = model.start_chat(history=history)
                        with st.spinner(t["spinner"]):
                            response = chat.send_message(full_query)
                            texto_ia = response.text
                            
                            st.markdown(texto_ia)
                            st.session_state.messages.append({"role": "assistant", "content": texto_ia})
                            
                            # C) GUARDADO AUTOMÁTICO
                            with st.status("📝 Aprendiendo...", expanded=False) as status:
                                exito = guardar_nueva_entrada(prompt, texto_ia)
                                if exito:
                                    status.update(label="¡Guardado en memoria!", state="complete", expanded=False)
                                else:
                                    status.update(label="No se pudo guardar (revisa permisos)", state="error")
                                    
                    except Exception as e:
                        st.error(f"{t['error_api']} ({str(e)})")
        
        st.rerun()

    st.divider()
    st.link_button(t["cta_btn"], "https://docs.google.com/forms/...", use_container_width=True, type="primary")
