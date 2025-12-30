import streamlit as st
import google.generativeai as genai
import requests

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Aeneis Tutor AI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. ESTILO CSS ACTUALIZADO (Eliminado el rectángulo de fondo)
st.markdown("""
    <style>
    .verse-line {
        font-family: 'Times New Roman', serif;
        font-size: 1.3rem;
        line-height: 1.6;
        color: #2c3e50;
        margin-bottom: 8px;
    }
    .main-header {
        color: #8e44ad;
        text-align: left;
        font-weight: bold;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    /* Estilo para el chat para que sea más legible */
    .stChatMessage {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CARGA DEL PROMPT MAESTRO
@st.cache_data
def load_master_prompt(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return "Error: No se pudo cargar el archivo de instrucciones."
    except:
        return "Error de conexión con el repositorio."

# --- CONFIGURACIÓN DE RECURSOS ---
# REEMPLAZA CON TU URL REAL DE GITHUB
GITHUB_RAW_URL = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/prompt_maestro.txt"
master_prompt = load_master_prompt(GITHUB_RAW_URL)

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-lite-preview-02-05",
        system_instruction=master_prompt
    )
else:
    st.error("Falta la API KEY en los secrets de Streamlit.")
    st.stop()

# 4. DISEÑO DE PANTALLA DIVIDIDA
col_texto, col_chat = st.columns([1, 1], gap="large")

with col_texto:
    st.markdown("<h2 class='main-header'>P. Vergili Maronis: Aeneis (I, 1-11)</h2>", unsafe_allow_html=True)
    # Espaciado mínimo para evitar el bloque visual anterior
    st.write("") 
    
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
    
    for verso in versos:
        st.markdown(f'<div class="verse-line">{verso}</div>', unsafe_allow_html=True)

with col_chat:
    st.subheader("💬 Guía Filológica Interactiva")
    
    if "messages" not in st.session_state:
        # LLAMAMIENTO A LA ACCIÓN MULTILINGÜE (Hardcoded para evitar el modo bot)
        welcome_text = """
### 🏛️ Salve, discipule!

Por favor, elige el idioma de tu tutor / Please choose your tutor's language:

* **Español:** ¿En qué idioma prefieres que realicemos nuestra tutoría?
* **English:** In which language would you prefer our tutoring?
* **Latine:** Qua lingua vis nōs colloqui?
* **繁體中文:** 您希望我們使用哪種語言進行輔導？
        """
        st.session_state.messages = [{"role": "assistant", "content": welcome_text}]

    # Mostrar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Lógica de Chat
    if prompt := st.chat_input("Escribe tu idioma o tu duda aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            chat = model.start_chat(history=[
                {"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]
            ])
            response = chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

    # BOTÓN DE RESERVA
    st.divider()
    cta_url = "https://docs.google.com/forms/d/e/1FAIpQLSdcEGs0k3eO1A3yDwwlRPZxM7RPpOPVD121J6GMUwAgbtbQ5w/viewform?usp=header"
    st.link_button("🏛️ Reserva una clase con un profesor de latín", cta_url, use_container_width=True, type="primary")
