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

# 2. ESTILO CSS PERSONALIZADO (Look & Feel de Filología Clásica)
st.markdown("""
    <style>
    .latin-container {
        background-color: #fdfaf3;
        padding: 30px;
        border-radius: 15px;
        border-left: 8px solid #8e44ad;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        font-family: 'serif';
    }
    .verse-line {
        font-size: 1.25rem;
        line-height: 1.8;
        color: #2c3e50;
        margin-bottom: 5px;
    }
    .main-header {
        color: #8e44ad;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CARGA DEL PROMPT MAESTRO DESDE GITHUB
@st.cache_data
def load_master_prompt(url):
    try:
        # Reemplaza esta URL con tu enlace "Raw" real de GitHub
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return "Error: No se pudo cargar el Prompt Maestro."
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# --- CONFIGURACIÓN DE URL Y API ---
# SUSTITUYE POR TU URL REAL
GITHUB_RAW_URL = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/prompt_maestro.txt"
master_prompt_content = load_master_prompt(GITHUB_RAW_URL)

# Configuración de Gemini
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Usando el modelo Flash Lite disponible a finales de 2025
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-lite-preview-02-05",
        system_instruction=master_prompt_content
    )
else:
    st.error("⚠️ Configura tu GEMINI_API_KEY en los Secrets de Streamlit.")
    st.stop()

# 4. INTERFAZ DE USUARIO (DASHBOARD)
st.markdown("<h1 class='main-header'>🏛️ Proyecto Eneida: Tutoría Socrática</h1>", unsafe_allow_html=True)
st.divider()

col_texto, col_chat = st.columns([1, 1], gap="large")

# --- COLUMNA IZQUIERDA: EL TEXTO ---
with col_texto:
    st.subheader("P. Vergili Maronis: Aeneis (I, 1-11)")
    
    texto_latino = [
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
    
    with st.container():
        st.markdown('<div class="latin-container">', unsafe_allow_html=True)
        for line in texto_latino:
            st.markdown(f'<div class="verse-line">{line}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.info("💡 **Consejo:** Empieza saludando en el chat para definir el idioma de la tutoría.")

# --- COLUMNA DERECHA: EL CHAT ---
with col_chat:
    st.subheader("💬 Guía Filológica Interactiva")
    
    # Inicialización del historial
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Ejecución del protocolo inicial (saludo en latín y pregunta de idioma)
        try:
            initial_response = model.generate_content("EJECUTA PROTOCOLO INICIAL.")
            st.session_state.messages.append({"role": "assistant", "content": initial_response.text})
        except Exception as e:
            st.error(f"Error al conectar con Gemini: {e}")

    # Mostrar mensajes del historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input de chat
    if prompt := st.chat_input("Escribe tu duda o respuesta..."):
        # Guardar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta de la IA
        with st.chat_message("assistant"):
            # Pasamos el historial completo para mantener la lógica de bloques y transiciones
            history = [
                {"role": m["role"], "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ]
            chat = model.start_chat(history=history)
            
            with st.spinner("Analizando sintaxis..."):
                response = chat.send_message(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

    # BOTÓN DE RESERVA (Footer del chat)
    st.divider()
    form_link = "https://docs.google.com/forms/d/e/1FAIpQLSdcEGs0k3eO1A3yDwwlRPZxM7RPpOPVD121J6GMUwAgbtbQ5w/viewform?usp=header"
    st.link_button("🏫 Reserva una clase con un profesor de latín", form_link, use_container_width=True, type="primary")
