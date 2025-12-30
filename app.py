import streamlit as st
import google.generativeai as genai
import requests

# 1. Configuración de la página
st.set_page_config(
    page_title="Aeneis Tutor AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CSS AVANZADO: Fijación de columna (Sticky) y limpieza visual
# Este bloque elimina el rectángulo beige y asegura que la columna de texto no se mueva.
st.markdown("""
    <style>
    /* 1. Hacer que la primera columna sea pegajosa (Sticky) */
    [data-testid="column"]:nth-of-type(1) {
        position: sticky;
        top: 2rem;
        align-self: flex-start;
        height: fit-content;
    }

    /* 2. Estética de los versos (Sin fondos beige) */
    .main-header {
        color: #8e44ad;
        font-weight: bold;
        margin-bottom: 0px;
    }
    .verse-line {
        font-family: 'Times New Roman', serif;
        font-size: 1.35rem;
        line-height: 1.6;
        color: #2c3e50;
        margin-bottom: 8px;
    }

    /* 3. Ajuste de espaciado para evitar saltos visuales */
    .stApp {
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Función para cargar el Prompt Maestro desde GitHub
@st.cache_data
def load_prompt(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.text
        return "Error: No se pudo cargar el Prompt Maestro."
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# --- CONFIGURACIÓN DE RECURSOS ---
# REEMPLAZA CON TU URL REAL DE GITHUB
GITHUB_RAW_URL = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/prompt_maestro.txt"
master_prompt_content = load_prompt(GITHUB_RAW_URL)

# Inicialización de Gemini 2.5 Flash Lite (Diciembre 2025)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-lite-preview-02-05", 
        system_instruction=master_prompt_content
    )
else:
    st.error("⚠️ Configura la API KEY en los Secrets de Streamlit.")
    st.stop()

# 4. Diseño de Pantalla Dividida
col_texto, col_chat = st.columns([1, 1], gap="large")

with col_texto:
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
    
    # Renderizado de los versos (Limpio, sin cajas de color)
    for v in versos:
        st.markdown(f'<div class="verse-line">{v}</div>', unsafe_allow_html=True)
    
    st.write("---")
    st.caption("📍 El texto permanecerá fijo mientras el chat se desplaza.")

with col_chat:
    st.subheader("💬 Guía Filológica Interactiva")
    
    # Inicialización del chat
    if "messages" not in st.session_state:
        # Mensaje de bienvenida multilingüe directo
        welcome_text = """
### 🏛️ Salve, discipule!
Por favor, elige tu idioma para comenzar / Please choose your language:
* **Español** | **English** | **Latine** | **繁體中文**
        """
        st.session_state.messages = [{"role": "assistant", "content": welcome_text}]

    # Mostrar historial
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Entrada del usuario
    if prompt := st.chat_input("Escribe tu idioma o respuesta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Lógica para forzar el inicio del análisis tras la elección del idioma
            # Si solo hay un mensaje (la bienvenida), el siguiente input es el idioma.
            if len(st.session_state.messages) <= 2:
                command = f"El idioma elegido es {prompt}. ANALIZA AHORA el Bloque 1: 'Arma virumque canō' siguiendo estrictamente tu protocolo de Verbo Primero y análisis morfológico."
            else:
                command = prompt

            # Llamada a la API con historial
            history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat = model.start_chat(history=history)
            
            with st.spinner("Consultando al oráculo filológico..."):
                response = chat.send_message(command)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

    # BOTÓN DE RESERVA (Al final de la columna de chat)
    st.divider()
    cta_url = "https://docs.google.com/forms/d/e/1FAIpQLSdcEGs0k3eO1A3yDwwlRPZxM7RPpOPVD121J6GMUwAgbtbQ5w/viewform?usp=header"
    st.link_button("🏛️ Reserva una clase con un profesor de latín", cta_url, use_container_width=True, type="primary")
