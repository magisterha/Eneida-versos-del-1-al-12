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

# 2. CSS PARA COLUMNA FIJA Y DISEÑO LIMPIO
# Implementamos 'sticky' para que el texto de Virgilio acompañe siempre al alumno.
st.markdown("""
    <style>
    /* Columna izquierda fija */
    [data-testid="column"]:nth-of-type(1) {
        position: sticky;
        top: 2rem;
        align-self: flex-start;
    }
    .main-header {
        color: #8e44ad;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .verse-line {
        font-family: 'Times New Roman', serif;
        font-size: 1.35rem;
        line-height: 1.6;
        color: #2c3e50;
        margin-bottom: 8px;
    }
    /* Estilo de los mensajes */
    .stChatMessage {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DICCIONARIO DE PROMPTS DE BLOQUE
# Inyecciones específicas para garantizar el rigor filológico en cada paso.
BLOQUES_PROMPTS = {
    1: "ANALIZA BLOQUE 1: 'Arma virumque canō'. Analiza 'canō' primero. Vocabulario: Arma, virum, -que. Transición: Pregunta por el referente de 'quī'.",
    2: "ANALIZA BLOQUE 2: 'Trōiae quī prīmus ab ōrīs / Ītaliam, fātō profugus, Lāvīniaque vēnit lītora'. Analiza 'vēnit' primero. Transición: Pregunta por 'ille'.",
    3: "ANALIZA BLOQUE 3: 'multum ille et terrīs iactātus et altō / vī superum saevae memorem Iūnōnis ob īram'. Analiza 'iactātus'. Transición: Identificar verbo en 'passus'.",
    4: "ANALIZA BLOQUE 4: 'multa quoque et bellō passus, dum conderet urbem / inferretque deōs Latiō'. Transición: Pregunta por 'unde'.",
    5: "ANALIZA BLOQUE 5: 'genus unde Latīnum...'. Explica la elipsis de 'est'. Transición: Identificar imperativo 'memorā'.",
    6: "ANALIZA BLOQUE 6: 'Mūsa, mihī causās memorā...'. Analiza 'memorā' e 'impulerit'. Transición: Tono de la interrogativa final.",
    7: "ANALIZA BLOQUE 7: 'Tantaene animīs caelestibus īrae?'. Ofrece informe final copiable."
}

# 4. CARGA DEL PROMPT BASE (SYSTEM INSTRUCTION)
@st.cache_data
def load_base_prompt(url):
    try:
        r = requests.get(url)
        return r.text if r.status_code == 200 else "Eres un tutor de latín conciso y socrático."
    except:
        return "Eres un tutor de latín conciso y socrático."

# URL RAW de GitHub para el prompt base
GITHUB_BASE_PROMPT_URL = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/prompt_base.txt"
base_instruction = load_base_prompt(GITHUB_BASE_PROMPT_URL)

# Configuración de Gemini 2.0 Flash Lite (Diciembre 2025)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-lite-preview-02-05",
        system_instruction=base_instruction
    )
else:
    st.error("⚠️ Configura la API KEY en los Secrets de Streamlit.")
    st.stop()

# 5. DISEÑO DE INTERFAZ DIVIDIDA
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
    for v in versos:
        st.markdown(f'<div class="verse-line">{v}</div>', unsafe_allow_html=True)
    
    st.divider()
    if st.button("🔄 Reiniciar Análisis", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

with col_chat:
    st.subheader("💬 Philologus AI")
    
    # Contenedor con scroll independiente
    chat_container = st.container(height=600, border=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []
        welcome = "### 🏛️ Salve!\nElige tu idioma para comenzar:\n* **Español** | **English** | **Latine**"
        st.session_state.messages.append({"role": "assistant", "content": welcome})

    with chat_container:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

    # Entrada de chat
    if prompt := st.chat_input("Escribe tu respuesta o idioma..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                # Inyección del Bloque 1 en el arranque
                if len(st.session_state.messages) <= 2:
                    input_final = f"El idioma es {prompt}. {BLOQUES_PROMPTS[1]}"
                else:
                    input_final = prompt

                # Gestión de historial para ventana de contexto
                history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                with st.spinner("Consultando al oráculo..."):
                    try:
                        response = chat.send_message(input_final)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        # Manejo del error de cuota agostada (ResourceExhausted)
                        if "429" in str(e) or "ResourceExhausted" in str(e):
                            st.error("🏛️ **El oráculo está saturado.** Se ha alcanzado el límite de consultas gratuitas. Por favor, espera un minuto o reinicia el análisis.")
                        else:
                            st.error(f"⚠️ Error inesperado: {e}")
        st.rerun()

    # Footer y CTA
    st.divider()
    st.link_button("🏛️ Reserva una clase con un profesor", "https://docs.google.com/forms/...", use_container_width=True, type="primary")
