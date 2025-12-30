import streamlit as st
import google.generativeai as genai
import requests

# 1. TRADUCCIONES Y FRONTEND MULTILINGÜE
TRADUCCIONES = {
    "Español": {
        "sidebar": "🏛️ Configuración", "header": "P. Vergili Maronis: Aeneis (I, 1-11)",
        "welcome": "### 🏛️ Salve!\n¿Qué palabra o verso deseas analizar?",
        "input": "Pregúntale a la IA (ej. cano, arma, virum...)", "spinner": "Analizando...",
        "sticky": "📍 Texto fijo."
    },
    "繁體中文 (Taiwan)": {
        "sidebar": "🏛️ 設定", "header": "維吉爾：《埃涅阿斯紀》(I, 1-11)",
        "welcome": "### 🏛️ 您好！\n您想分析文中的哪個詞或哪一行？",
        "input": "詢問 AI 關於此文本的問題...", "spinner": "分析中...",
        "sticky": "📍 文本已固定。"
    } # Puedes añadir English y Latine siguiendo este esquema
}

st.set_page_config(page_title="Aeneis Tutor AI", layout="wide")

# CSS para Scroll Independiente y Columna Fija
st.markdown("""
    <style>
    [data-testid="column"]:nth-of-type(1) { position: sticky; top: 2rem; align-self: flex-start; }
    .verse-line { font-family: 'Times New Roman', serif; font-size: 1.4rem; line-height: 1.7; color: #2c3e50; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    idioma = st.selectbox("Language / Idioma", list(TRADUCCIONES.keys()))
    t = TRADUCCIONES[idioma]
    if st.button("🔄 Reset"):
        st.session_state.messages = []
        st.rerun()

# 2. CONFIGURACIÓN DE IA
@st.cache_data
def load_prompt(url):
    try:
        r = requests.get(url)
        return r.text if r.status_code == 200 else "Expert Latin Philologist."
    except: return "Expert Latin Philologist."

PROMPT_URL = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/prompt_maestro.txt"
sys_prompt = load_prompt(PROMPT_URL)

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-lite-preview-02-05", #
        system_instruction=sys_prompt
    )
else:
    st.error("API KEY missing.")
    st.stop()

# 3. INTERFAZ DIVIDIDA
col_txt, col_chat = st.columns([1, 1], gap="large")

with col_txt:
    st.markdown(f"### {t['header']}")
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
    for v in versos: st.markdown(f'<p class="verse-line">{v}</p>', unsafe_allow_html=True)
    st.caption(t["sticky"])

with col_chat:
    chat_container = st.container(height=600, border=True)
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": t["welcome"]}]

    with chat_container:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

    if user_input := st.chat_input(t["input"]):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user"): st.markdown(user_input)
            with st.chat_message("assistant"):
                # INYECCIÓN DE REFUERZO: Obligamos a la IA a recordar el contexto latino y brevedad
                context_injection = f"[Idioma: {idioma}] [MANDATO: Ignora español. Solo Latín de Virgilio. Sé breve.] {user_input}"
                
                history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                try:
                    with st.spinner(t["spinner"]):
                        response = chat.send_message(context_injection)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception:
                    st.error("Rate Limit reached.")
        st.rerun()
