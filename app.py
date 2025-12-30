import streamlit as st
import google.generativeai as genai
import requests

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Aeneis Tutor AI", layout="wide")

# 2. CSS PARA COLUMNA FIJA Y ESTÉTICA
st.markdown("""
    <style>
    [data-testid="column"]:nth-of-type(1) {
        position: sticky;
        top: 2rem;
        align-self: flex-start;
    }
    .verse-line { font-family: 'serif'; font-size: 1.4rem; line-height: 1.7; color: #2c3e50; }
    .main-header { color: #8e44ad; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. SELECCIÓN DE IDIOMA EN EL FRONTEND
with st.sidebar:
    st.title("⚙️ Configuración")
    idioma_app = st.radio(
        "Selecciona el idioma del Tutor:",
        ["Español", "English", "Latine", "繁體中文 (Taiwan)"],
        index=0
    )
    st.info(f"El tutor responderá preferentemente en {idioma_app}.")
    if st.button("🔄 Reiniciar Chat"):
        st.session_state.messages = []
        st.rerun()

# 4. CONFIGURACIÓN DE AI
@st.cache_data
def load_prompt(url):
    try:
        r = requests.get(url)
        return r.text if r.status_code == 200 else "Eres un tutor de latín experto."
    except: return "Eres un tutor de latín experto."

# URL RAW de tu GitHub para el prompt maestro
PROMPT_URL = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/prompt_maestro.txt"
sys_instruction = load_prompt(PROMPT_URL)

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-lite-preview-02-05",
        system_instruction=sys_instruction
    )
else:
    st.error("⚠️ Configura la API KEY en Secrets.")
    st.stop()

# 5. DISEÑO DE PANTALLA DIVIDIDA
col_txt, col_chat = st.columns([1, 1], gap="large")

with col_txt:
    st.markdown("<h2 class='main-header'>P. Vergili Maronis: Aeneis (I, 1-11)</h2>", unsafe_allow_html=True)
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
    for v in versos: st.markdown(f'<p class="verse-line">{v}</p>', unsafe_allow_html=True)

with col_chat:
    st.subheader("💬 Consulta Filológica Libre")
    
    chat_container = st.container(height=600, border=True)

    if "messages" not in st.session_state or len(st.session_state.messages) == 0:
        welcome = f"### 🏛️ Salve!\nSoy tu tutor experto. He configurado mi respuesta en **{idioma_app}**.\n\n¿Qué te gustaría analizar de estos versos?"
        st.session_state.messages = [{"role": "assistant", "content": welcome}]

    with chat_container:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

    # LLAMADO A LA ACCIÓN (CTA) PERSONALIZADO
    if prompt := st.chat_input("Pregúntale cualquier cosa de este texto a la IA"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                # Enviamos el contexto del idioma seleccionado en el frontend
                context_msg = f"[Idioma de respuesta: {idioma_app}] {prompt}"
                
                history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                try:
                    with st.spinner("Analizando..."):
                        response = chat.send_message(context_msg)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error("🏛️ El oráculo está saturado. Intenta de nuevo en un minuto.")
        st.rerun()
