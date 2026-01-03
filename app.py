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

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
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
    "English": {"sidebar_title": "Settings", "lang_label": "Language:", "reset_btn": "Reset", "header": "Aeneid (I, 1-11)", "chat_header": "Consultation", "welcome": "### Salve!", "input_placeholder": "Ask...", "spinner": "...", "error_api": "Error", "sticky_note": "Note", "cta_btn": "Book Class"},
    "Latine": {"sidebar_title": "Configuratio", "lang_label": "Lingua:", "reset_btn": "Iterare", "header": "Aeneid (I, 1-11)", "chat_header": "Colloquium", "welcome": "### Salve!", "input_placeholder": "Interrogā...", "spinner": "...", "error_api": "Error", "sticky_note": "Nota", "cta_btn": "Schola"},
    "繁體中文 (Taiwan)": {"sidebar_title": "設定", "lang_label": "語言:", "reset_btn": "重置", "header": "維吉爾：《埃涅阿斯紀》", "chat_header": "諮詢", "welcome": "### 您好!", "input_placeholder": "詢問...", "spinner": "...", "error_api": "錯誤", "sticky_note": "備註", "cta_btn": "預約"}
}

# --- 3. FUNCIONES DE MEMORIA (CEREBRO HÍBRIDO) ---

def buscar_en_base_datos(pregunta_usuario):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=URL_HOJA_CALCULO, ttl=0)
        df = df.dropna(how="all").fillna("")
        
        pregunta_usuario = pregunta_usuario.lower().strip()
        
        for index, row in df.iterrows():
            # Buscamos en la primera columna (Pregunta)
            pregunta_db = str(row.iloc[0]).lower().strip()
            respuesta_db = str(row.iloc[1])
            
            if not pregunta_db: continue
            
            # Búsqueda flexible
            if (pregunta_usuario in pregunta_db) or (pregunta_db in pregunta_usuario):
                return respuesta_db
        return None
    except: return None

def guardar_nueva_entrada(pregunta, respuesta):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=URL_HOJA_CALCULO, ttl=0)
        df = df.dropna(how="all")
        
        nueva_fila = pd.DataFrame([[pregunta, respuesta]], columns=df.columns)
        df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
        
        conn.update(spreadsheet=URL_HOJA_CALCULO, data=df_actualizado)
        return True
    except: return False

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
        st.cache_data.clear()
        st.rerun()

# --- 6. CONFIGURACIÓN GEMINI ---
@st.cache_data
def load_prompt(url):
    try:
        r = requests.get(url)
        return r.text if r.status_code == 200 else "Expert Latin Philologist."
    except: return "Expert Latin Philologist."

PROMPT_URL = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/prompt_maestro.txt"
sys_instruction = load_prompt(PROMPT_URL)

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite-preview-02-05", system_instruction=sys_instruction)
else:
    st.error("⚠️ API KEY missing.")
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

    if prompt := st.chat_input(t["input_placeholder"]):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                # BUSCAR EN DB
                respuesta_db = buscar_en_base_datos(prompt)
                
                if respuesta_db:
                    st.success("📚 Respuesta de la Base de Conocimiento")
                    st.markdown(respuesta_db)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta_db})
                else:
                    # CONSULTAR IA
                    try:
                        history = [{"role": "model" if m["role"]=="assistant" else "user", "parts": [m["content"]]} 
                                   for m in st.session_state.messages[-6:-1]]
                        full_query = f"[Language: {idioma_app}] {prompt}"
                        chat = model.start_chat(history=history)
                        with st.spinner(t["spinner"]):
                            response = chat.send_message(full_query)
                            texto_ia = response.text
                            st.markdown(texto_ia)
                            st.session_state.messages.append({"role": "assistant", "content": texto_ia})
                            # GUARDAR
                            with st.status("📝 Guardando...", expanded=False):
                                guardar_nueva_entrada(prompt, texto_ia)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        st.rerun()

    st.divider()
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdcEGs0k3eO1A3yDwwlRPZxM7RPpOPVD121J6GMUwAgbtbQ5w/viewform?usp=header"
    st.link_button(t["cta_btn"], form_url, use_container_width=True, type="primary")
