import streamlit as st
import google.generativeai as genai
import requests

# 1. Configuración de página
st.set_page_config(page_title="Aeneis Tutor AI", layout="wide")

# 2. CSS AVANZADO: Columna izquierda fija (Sticky) y limpieza visual
st.markdown("""
    <style>
    /* Hace que la primera columna sea pegajosa (Sticky) */
    [data-testid="column"]:nth-of-type(1) {
        position: sticky;
        top: 2rem;
        align-self: flex-start;
    }
    
    .main-header {
        color: #8e44ad;
        margin-bottom: 10px;
        font-weight: bold;
    }
    
    .verse-line {
        font-family: 'serif';
        font-size: 1.3rem;
        line-height: 1.6;
        color: #2c3e50;
        margin-bottom: 5px;
    }
    
    /* Ajuste para que el chat no empuje toda la página */
    .stChatMessage {
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Carga del Prompt Maestro
@st.cache_data
def load_prompt(url):
    try:
        r = requests.get(url)
        return r.text if r.status_code == 200 else "Error cargando prompt."
    except:
        return "Error de conexión."

# --- CONFIGURACIÓN DE MODELO ---
# REEMPLAZA CON TU URL RAW DE GITHUB
PROMPT_URL = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/prompt_maestro.txt"
master_prompt = load_prompt(PROMPT_URL)

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-lite-preview-02-05", 
        system_instruction=master_prompt
    )
else:
    st.error("⚠️ Configura la API KEY en los Secrets de Streamlit.")
    st.stop()

# 4. Diseño de Pantalla Dividida
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
    
    # Contenedor para los versos
    for v in versos:
        st.markdown(f'<p class="verse-line">{v}</p>', unsafe_allow_html=True)
    
    st.write("---")
    st.info("📍 El texto permanecerá visible mientras te desplazas por el chat.")

with col_chat:
    st.subheader("💬 Guía Filológica Interactiva")
    
    if "messages" not in st.session_state:
        # Bienvenida multilingüe estática
        welcome = """
### 🏛️ Salve, discipule!
Por favor, elige tu idioma para comenzar / Choose your language:
* **Español** | **English** | **Latine** | **繁體中文**
        """
        st.session_state.messages = [{"role": "assistant", "content": welcome}]

    # Mostrar historial de chat
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Entrada de usuario
    if prompt := st.chat_input("Escribe tu idioma o respuesta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Lógica para forzar el inicio tras elegir idioma
            full_prompt = prompt
            if len(st.session_state.messages) <= 2:
                full_prompt = f"El idioma elegido es {prompt}. Comienza de inmediato con el análisis del Bloque 1."

            # Llamada a Gemini con historial
            history = [
                {"role": m["role"], "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ]
            chat = model.start_chat(history=history)
            
            with st.spinner("Analizando..."):
                response = chat.send_message(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

    # Botón de reserva al final de la columna de chat
    st.divider()
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdcEGs0k3eO1A3yDwwlRPZxM7RPpOPVD121J6GMUwAgbtbQ5w/viewform?usp=header"
    st.link_button("🏛️ Reserva una clase con un profesor de latín", form_url, use_container_width=True, type="primary")
