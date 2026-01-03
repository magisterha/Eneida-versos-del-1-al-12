import streamlit as st
import google.generativeai as genai
import requests
# --- NUEVA IMPORTACIÓN PARA LA BASE DE DATOS ---
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Aeneis Tutor AI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. DICCIONARIO DE TRADUCCIONES (Frontend) ---
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
    "English": {
        "sidebar_title": "🏛️ Settings",
        "lang_label": "Tutor Language:",
        "reset_btn": "🔄 Reset Chat",
        "header": "P. Vergili Maronis: Aeneis (I, 1-11)",
        "chat_header": "💬 Free Philological Consultation",
        "welcome": "### 🏛️ Salve!\nI have configured my system to help you in **English**. Which word or verse would you like to analyze?",
        "input_placeholder": "Ask the AI (e.g., cano, arma, virum...)",
        "spinner": "Analyzing...",
        "error_api": "🏛️ The oracle is busy. Please wait.",
        "sticky_note": "📍 Static text for permanent reference.",
        "cta_btn": "🏛️ Book a class with a Latin teacher"
    },
    "Latine": {
        "sidebar_title": "🏛️ Configuratio",
        "lang_label": "Lingua Tutoris:",
        "reset_btn": "🔄 Iterare Colloquium",
        "header": "P. Vergili Maronis: Aeneis (I, 1-11)",
        "chat_header": "💬 Colloquium Philologicum Liberum",
        "welcome": "### 🏛️ Salve!\nSīstēma meum parāvī ut **Latinē** tē adiuvārem. Quod verbum aut versum explōrāre vīs?",
        "input_placeholder": "Interrogā aliquid (ex. cano, arma, virum...)",
        "spinner": "Exquīrentem...",
        "error_api": "🏛️ Ōrāculum occupātum est. Paulō post sevērā.",
        "sticky_note": "📍 Textus fīxus.",
        "cta_btn": "🏛️ Scholam cum magistro linguae Latinae reserva"
    },
    "繁體中文 (Taiwan)": {
        "sidebar_title": "🏛️ 設定",
        "lang_label": "導師語言：",
        "reset_btn": "🔄 重置對話",
        "header": "維吉爾：《埃涅阿斯紀》(I, 1-11)",
        "chat_header": "💬 自由文獻學諮詢",
        "welcome": "### 🏛️ 您好！\n我已準備好以 **繁體中文** 為您提供幫助。您想分析文中的哪個詞或哪一行？",
        "input_placeholder": "向 AI 詢問（例如：cano, arma, virum...）",
        "spinner": "分析中...",
        "error_api": "🏛️ 神諭目前繁忙。請稍後再試。",
        "sticky_note": "📍 文本已固定。",
        "cta_btn": "🏛️ 與拉丁語老師預約課程"
    }
}

# --- 3. CSS PARA COLUMNA FIJA ---
st.markdown("""
    <style>
    [data-testid="column"]:nth-of-type(1) { position: sticky; top: 2rem; align-self: flex-start; }
    .verse-line { font-family: 'Times New Roman', serif; font-size: 1.4rem; line-height: 1.7; color: #2c3e50; }
    .main-header { color: #8e44ad; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR MULTILINGÜE ---
with st.sidebar:
    idioma_app = st.selectbox("Language / Idioma / 語言", list(TRADUCCIONES.keys()))
    t = TRADUCCIONES[idioma_app]
    st.title(t["sidebar_title"])
    if st.button(t["reset_btn"]):
        st.session_state.messages = []
        st.rerun()

    # --- NUEVO: DIAGNÓSTICO DE BASE DE DATOS EN SIDEBAR ---
    with st.expander("🕵️‍♂️ Estado de Base de Datos"):
        try:
            # Creamos la conexión
            conn = st.connection("gsheets", type=GSheetsConnection)
            
            # ⚠️ ¡CAMBIA ESTA LÍNEA POR TU ENLACE! ⚠️
            url_hoja = "https://docs.google.com/spreadsheets/d/TU_URL_AQUI/edit"
            
            # Leemos los datos
            df = conn.read(spreadsheet=url_hoja, usecols=[0,1]) # Leemos solo las 2 primeras columnas
            st.success("✅ Conectado")
            st.caption(f"Filas encontradas: {len(df)}")
        except Exception as e:
            st.error("❌ Desconectado")
            st.caption(str(e))

# --- 5. CONFIGURACIÓN DE GEMINI API ---
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
    st.error("⚠️ API KEY missing in Secrets.")
    st.stop()

# --- 6. DISEÑO DE PANTALLA DIVIDIDA ---
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
                # --- LÓGICA DE PODA (SLIDING WINDOW) ---
                LIMITE_MEMORIA = 6 
                mensajes_recientes = st.session_state.messages[-LIMITE_MEMORIA:]
                
                history_for_api = []
                for m in mensajes_recientes[:-1]: 
                    api_role = "model" if m["role"] == "assistant" else "user"
                    history_for_api.append({"role": api_role, "parts": [m["content"]]})
                
                # Inyección de mandato contextual
                full_query = (
                    f"[Language: {idioma_app}] "
                    f"[MANDATO: Ignora español para homógrafos. Solo Latín de Virgilio. "
                    f"Foco: Significado filológico contextual. Sé breve y directo.] "
                    f"{prompt}"
                )
                
                try:
                    chat = model.start_chat(history=history_for_api)
                    with st.spinner(t["spinner"]):
                        response = chat.send_message(full_query)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"{t['error_api']} ({str(e)})")
        st.rerun()

    st.divider()
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdcEGs0k3eO1A3yDwwlRPZxM7RPpOPVD121J6GMUwAgbtbQ5w/viewform?usp=header"
    st.link_button(t["cta_btn"], form_url, use_container_width=True, type="primary")
