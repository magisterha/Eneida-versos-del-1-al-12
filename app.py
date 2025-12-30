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

# 2. CSS PARA COLUMNA FIJA Y SCROLL INDEPENDIENTE
# Diseñado para un entorno de análisis filológico profesional.
st.markdown("""
    <style>
    /* Fijar la primera columna (Texto de la Eneida) para consulta permanente */
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
    /* Estilo para los mensajes del chat */
    .stChatMessage {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DICCIONARIO DE PROMPTS DE BLOQUE (INYECCIONES DINÁMICAS)
# Implementa la jerarquía verbal y las transiciones socráticas solicitadas.
BLOQUES_PROMPTS = {
    1: """
    ### INSTRUCCIÓN: BLOQUE 1
    **Texto**: "Arma virumque canō"
    **Protocolo**:
    1. Analiza el verbo **canō** primero (morfología y significado).
    2. Vocabulario: *Arma* (Ac. Pl. N.), *virum* (Ac. S. M.), *-que* (conjunción).
    3. **Transición**: Pregunta por el análisis de "**quī**" y su referente gramatical.
    """,
    2: """
    ### INSTRUCCIÓN: BLOQUE 2
    **Texto**: "Trōiae quī prīmus ab ōrīs / Ītaliam, fātō profugus, Lāvīniaque vēnit lītora"
    **Protocolo**:
    1. Analiza el verbo **vēnit** primero.
    2. Explica la oración de relativo sobre 'virum'.
    3. **Transición**: Analiza "**ille**" y pregunta por su referente en la narración.
    """,
    3: """
    ### INSTRUCCIÓN: BLOQUE 3
    **Texto**: "multum ille et terrīs iactātus et altō / vī superum saevae memorem Iūnōnis ob īram"
    **Protocolo**:
    1. Analiza el participio **iactātus**.
    2. **Transición**: Pide identificar el verbo en "multa quoque et bellō passus".
    """,
    4: """
    ### INSTRUCCIÓN: BLOQUE 4
    **Texto**: "multa quoque et bellō passus, dum conderet urbem / inferretque deōs Latiō"
    **Protocolo**:
    1. Diferencia la principal (*passus*) de la subordinada (*conderet*, *inferret*).
    2. **Transición**: Pregunta por el referente y significado de "**unde**".
    """,
    5: """
    ### INSTRUCCIÓN: BLOQUE 5
    **Texto**: "genus unde Latīnum, Albānīque patrēs, atque altae moenia Rōmae"
    **Protocolo**:
    1. Explica la elipsis del verbo 'est/sunt'.
    2. **Transición**: Pide identificar el imperativo en el verso 8 (*memorā*).
    """,
    6: """
    ### INSTRUCCIÓN: BLOQUE 6
    **Texto**: "Mūsa, mihī causās memorā... impulerit"
    **Protocolo**:
    1. Analiza **memorā** e **impulerit**.
    2. **Transición**: Pregunta sobre el tono de la interrogativa final.
    """,
    7: """
    ### INSTRUCCIÓN: BLOQUE 7
    **Texto**: "Tantaene animīs caelestibus īrae?"
    **Protocolo**:
    1. Analiza partícula **-ne** y dativo de posesión.
    2. Ofrece el **Informe Final** para copiar.
    """
}

# 4. CARGA DEL PROMPT BASE (SYSTEM INSTRUCTION)
@st.cache_data
def load_base_prompt(url):
    try:
        r = requests.get(url)
        return r.text if r.status_code == 200 else "Eres un tutor de latín conciso y socrático."
    except: return "Eres un tutor de latín conciso y socrático."

# REEMPLAZA CON LA URL "RAW" DE TU GITHUB
GITHUB_BASE_PROMPT_URL = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/prompt_base.txt"
base_instruction = load_base_prompt(GITHUB_BASE_PROMPT_URL)

# Configuración de Gemini 2.5 Flash Lite (Diciembre 2025)
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
    st.caption("📍 El texto permanece fijo para facilitar la consulta morfosintáctica.")

with col_chat:
    st.subheader("💬 Philologus AI")
    
    # Contenedor de chat con scroll independiente (600px de altura)
    chat_container = st.container(height=600, border=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []
        welcome = "### 🏛️ Salve!\nElige tu idioma para comenzar / Choose your language:\n* **Español** | **English** | **Latine**"
        st.session_state.messages.append({"role": "assistant", "content": welcome})

    # Renderizar mensajes en el contenedor con scroll
    with chat_container:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

    # Entrada de chat (Anclada al final de la columna derecha)
    if prompt := st.chat_input("Escribe tu idioma o respuesta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                # Lógica de arranque: Si es la primera respuesta, inyectamos el Bloque 1
                if len(st.session_state.messages) <= 2:
                    input_final = f"El idioma elegido es {prompt}. ANALIZA AHORA el {BLOQUES_PROMPTS[1]}"
                else:
                    input_final = prompt

                # Gestión del historial para la ventana de contexto activa
                history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                with st.spinner("Analizando..."):
                    response = chat.send_message(input_final)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.rerun()

    # BOTÓN DE CONVERSIÓN
    st.divider()
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdcEGs0k3eO1A3yDwwlRPZxM7RPpOPVD121J6GMUwAgbtbQ5w/viewform?usp=header"
    st.link_button("🏛️ Reserva una clase con un profesor de latín", form_url, use_container_width=True, type="primary")
