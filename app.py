import streamlit as st
import google.generativeai as genai
import requests

# 1. Configuración de la página (Layout ancho para dividir la pantalla)
st.set_page_config(
    page_title="Aeneis Tutor AI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CSS PERSONALIZADO: Estética y fijación de texto
st.markdown("""
    <style>
    /* Estilo para los versos de la Eneida */
    .verse-line {
        font-family: 'Times New Roman', serif;
        font-size: 1.4rem;
        line-height: 1.8;
        color: #2c3e50;
        margin-bottom: 5px;
    }
    .main-header {
        color: #8e44ad;
        font-weight: bold;
        margin-bottom: 20px;
    }
    /* Ocultar elementos innecesarios para máxima limpieza */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Carga del Prompt Maestro desde GitHub
@st.cache_data
def load_prompt(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.text
        return "Error: No se pudo cargar el Prompt Maestro."
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# REEMPLAZA CON TU URL REAL DE GITHUB
GITHUB_RAW_URL = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/prompt_maestro.txt"
master_prompt_content = load_prompt(GITHUB_RAW_URL)

# Inicialización de Gemini 2.5 Flash Lite (Configuración para diciembre 2025)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-lite-preview-02-05", 
        system_instruction=master_prompt_content
    )
else:
    st.error("⚠️ Configura la API KEY en los Secrets de Streamlit.")
    st.stop()

# 4. DISEÑO DE PANTALLA DIVIDIDA
col_texto, col_chat = st.columns([1, 1], gap="large")

# --- COLUMNA IZQUIERDA: TEXTO FIJO ---
with col_texto:
    st.markdown("<h2 class='main-header'>P. Vergili Maronis: Aeneis (I, 1-11)</h2>", unsafe_allow_html=True)
    
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
    
    # Renderizado estático
    for v in versos:
        st.markdown(f'<div class="verse-line">{v}</div>', unsafe_allow_html=True)
    
    st.divider()
    st.caption("📍 El texto de la Eneida permanece estático para facilitar su consulta.")

# --- COLUMNA DERECHA: CHAT CON SCROLL INDEPENDIENTE ---
with col_chat:
    st.subheader("💬 Guía Filológica Interactiva")
    
    # Contenedor de chat con altura fija para permitir scroll independiente
    chat_container = st.container(height=600, border=True)

    if "messages" not in st.session_state:
        welcome_text = "### 🏛️ Salve, discipule!\nPor favor, elige tu idioma para comenzar:\n* **Español** | **English** | **Latine** | **繁體中文**"
        st.session_state.messages = [{"role": "assistant", "content": welcome_text}]

    # Mostrar mensajes dentro del contenedor con scroll
    with chat_container:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

    # Entrada de chat (fuera del contenedor de mensajes para que siempre esté visible abajo)
    if prompt := st.chat_input("Escribe tu idioma o respuesta..."):
        # Guardar y mostrar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generar respuesta de la IA
            with st.chat_message("assistant"):
                if len(st.session_state.messages) <= 2:
                    command = f"El idioma elegido es {prompt}. ANALIZA AHORA el Bloque 1."
                else:
                    command = prompt

                history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                with st.spinner("Consultando al tutor..."):
                    response = chat.send_message(command)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
        
        # Forzar recarga para que el contenedor se deslice al final
        st.rerun()

    # Botón de reserva (Anclado al final de la columna de chat)
    st.divider()
    cta_url = "https://docs.google.com/forms/d/e/1FAIpQLSdcEGs0k3eO1A3yDwwlRPZxM7RPpOPVD121J6GMUwAgbtbQ5w/viewform?usp=header"
    st.link_button("🏛️ Reserva una clase con un profesor de latín", cta_url, use_container_width=True, type="primary")
