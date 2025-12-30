import streamlit as st
import google.generativeai as genai
import requests

# 1. DICCIONARIO DE TRADUCCIONES INTEGRAL
# Incluye el texto del botón de reserva para cada idioma.
TRADUCCIONES = {
    "Español": {
        "sidebar_title": "🏛️ Configuración",
        "lang_label": "Idioma del Tutor:",
        "reset_btn": "🔄 Reiniciar Consulta",
        "header": "P. Vergili Maronis: Aeneis (I, 1-11)",
        "chat_header": "💬 Consulta Filológica Libre",
        "welcome": "### 🏛️ ¡Salve!\nHe configurado mi sistema para ayudarte en **Español**. ¿Qué palabra o verso deseas analizar?",
        "input_placeholder": "Pregúntale a la IA (ej. cano, arma, virum...)",
        "spinner": "Analizando bajo contexto...",
        "error_api": "🏛️ El oráculo está saturado. Reintenta en breve.",
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
        "spinner": "Analyzing contextually...",
        "error_api": "🏛️ The oracle is busy. Please try again in a moment.",
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
        "sticky_note": "📍 Textus fīxus ad perpetuam cōnsultātiōnem.",
        "cta_btn": "🏛️ Scholam cum magistro linguae Latinae reserva"
    },
    "繁體中文 (Taiwan)": {
        "sidebar_title": "🏛️ 設定",
        "lang_label": "導師語言：",
        "reset_btn": "🔄 重置對話",
        "header": "維吉爾：《埃涅阿斯紀》(I, 1-11)",
        "chat_header": "💬 自由文獻學諮詢",
        "welcome": "### 🏛️ 您好 (Salve)！\n我已準備好以 **繁體中文** 為您提供幫助。您想分析文中的哪個詞或哪一行？",
        "input_placeholder": "向 AI 詢問（例如：cano, arma, virum...）",
        "spinner": "正在進行語境分析...",
        "error_api": "🏛️ 神諭目前繁忙。請稍後再試。",
        "sticky_note": "📍 文本已固定，方便隨時查閱。",
        "cta_btn": "🏛️ 與拉丁語老師預約課程"
    }
}

# 2. CONFIGURACIÓN DE PÁGINA Y CSS (Columna Fija)
st.set_page_config(page_title="Aeneis Tutor AI", layout="wide")

st.markdown("""
    <style>
    [data-testid="column"]:nth-of-type(1) {
        position: sticky;
        top: 2rem;
        align-self: flex-start;
    }
    .verse-line {
        font-family: 'Times New Roman', serif;
        font-size: 1.4rem;
        line-height: 1.7;
        color: #2c3e50;
        margin-bottom: 5px;
    }
    .main-header {
        color: #8e44ad;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SIDEBAR MULTILINGÜE
with st.sidebar:
    idioma_app = st.selectbox("Language / Idioma / 語言", list(TRADUCCIONES.keys()))
    t = TRADUCCIONES[idioma_app]
    
    st.title(t["sidebar_title"])
    if st.button(t["reset_btn"]):
        st.session_state.messages = []
        st.rerun()

# 4. CONFIGURACIÓN DE IA
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

# 5. DISEÑO DE PANTALLA DIVIDIDA
col_txt, col_chat = st.columns([1, 1], gap="large")

with col_txt:
    st.markdown(f"<h2 class='main-header'>{t['header']}</h2>", unsafe_allow_html=True)
    st.write("---")
    versos = [
        "1. Arma virumque canō, Trōiae quī prīmus ab ōrīs",
        "2. Ītaliam, fātō profugus, Lāvīniaque vēnit",
        "3. lītora, multum ille et terrīs iactātus et altō",
        "4. vī superum saevae memorem Iūnōnis ob īram;",
        "5. multa quoque et bellō passus, dum conderet urbem,",
        "6. inferretque deōs Latiō, genus unde Latīnum,",
        "7. Albānīque patrēs, atque altae moenia Rōmae.",
        "8. Mūsa, mihī causās memorā, quō nūmine laesō,",
        "9. quidve dolēns, rēgīna deum tot volvere cāsūs",
        "10. īnsīgnem pietāte virum, tot adīre labōrēs",
        "11. impulerit. Tantaene animīs caelestibus īrae?"
    ]
    for v in versos:
        st.markdown(f'<p class="verse-line">{v}</p>', unsafe_allow_html=True)
    st.caption(t["sticky_note"])

with col_chat:
    st.subheader(t["chat_header"])
    chat_container = st.container(height=550, border=True)

    if "messages" not in st.session_state or len(st.session_state.messages) == 0:
        st.session_state.messages = [{"role": "assistant", "content": t["welcome"]}]

    with chat_container:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

    if prompt := st.chat_input(t["input_placeholder"]):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                # REFUERZO DE CONTEXTO Y IDIOMA
                full_query = (
                    f"[Language: {idioma_app}] "
                    f"[MANDATO: Ignora español. Solo Latín de Virgilio. "
                    f"Foco: Significado filológico contextual. Sé breve.] "
                    f"{prompt}"
                )
                
                history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                try:
                    with st.spinner(t["spinner"]):
                        response = chat.send_message(full_query)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception:
                    st.error(t["error_api"])
        st.rerun()

    # --- ENLACE PARA CLASE CON PROFESOR (CTA) ---
    st.divider()
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdcEGs0k3eO1A3yDwwlRPZxM7RPpOPVD121J6GMUwAgbtbQ5w/viewform?usp=header"
    st.link_button(t["cta_btn"], form_url, use_container_width=True, type="primary")
