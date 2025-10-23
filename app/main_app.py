# app/main_app.py
import os
from pathlib import Path
import sys
from dotenv import load_dotenv
import streamlit as st
import yaml

# --- sys.path para importar rag.core ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.core import RAGSystem

# --- CONFIGURACIÓN DE AUTENTICACIÓN ---
USER_ALLOWLIST_PATH = ROOT / "config" / "user_allowlist.yaml"

@st.cache_data
def load_allowlist():
    """Carga la lista de usuarios y dominios permitidos desde un archivo YAML."""
    if not USER_ALLOWLIST_PATH.exists():
        return {"authorized_domains": [], "authorized_users": []}
    with open(USER_ALLOWLIST_PATH, 'r') as f:
        return yaml.safe_load(f)

def is_authorized(email: str) -> bool:
    """Verifica si un email está autorizado."""
    if not email:
        return False
    allowlist = load_allowlist()
    # Comprobar si el email está en la lista de usuarios autorizados
    if email.lower() in allowlist.get("authorized_users", []):
        return True
    # Comprobar si el dominio del email está en la lista de dominios autorizados
    for domain in allowlist.get("authorized_domains", []):
        if email.lower().endswith(domain):
            return True
    return False

def login_form():
    """Muestra el formulario de login y maneja la lógica de autenticación."""
    st.header("Acceso al Chatbot")
    with st.form("login_form"):
        email = st.text_input("Ingresa tu correo electrónico para continuar")
        submitted = st.form_submit_button("Ingresar")
        if submitted:
            if is_authorized(email):
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Acceso denegado. Tu correo electrónico no está autorizado.")

# --- FIN DE LA CONFIGURACIÓN DE AUTENTICACIÓN ---


# Carga .env
load_dotenv(dotenv_path=str(ROOT / ".env"))

st.set_page_config(page_title="Chatbox Interno Labelix", layout="wide")
st.title('📚 Chatbox Interno "Labelix"')


# --- LÓGICA PRINCIPAL DE LA APP ---

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_form()
else:
    st.markdown("Responde preguntas de negocio, operativas y de onboarding en segundos.")

    @st.cache_resource
    def get_rag_system():
        # La única variable que necesitamos leer explícitamente es DATA_DIR
        data_dir = os.getenv("DATA_DIR", "./data")

        progress = st.progress(0)
        msg = st.empty()
        def cb(stage: str, i: int, n: int):
            perc = 0 if n == 0 else int((i / max(n, 1)) * 100)
            progress.progress(perc, text=f"{stage} ({i}/{n})")
            msg.write(f"**{stage}** ({i}/{n})")

        try:
            # La inicialización ahora es mucho más simple y usa los defaults de la clase
            return RAGSystem(
                data_dir=data_dir,
                progress_cb=cb,
            )
        except Exception as e:
            st.error(f"Error al inicializar el sistema RAG: {e}")
            st.warning("Revisa tus variables de entorno (.env) para Google y Pinecone, y las dependencias.")
            return None

    rag_system = get_rag_system()

    if rag_system:
        st.sidebar.header("Configuración Activa")
        st.sidebar.info(f"Usuario: {st.session_state.user_email}")
        mode = st.sidebar.radio("Selecciona un modo:", ("Consulta General", "Onboarding", "Fuentes (Próximamente)"))
        st.sidebar.markdown("---")
        st.sidebar.write("**Arquitectura RAG:**")
        st.sidebar.code(f"LLM: {rag_system.llm_model_name}")
        st.sidebar.code(f"Embeddings: {rag_system.embed_fn.model}")
        st.sidebar.code(f"Índice Pinecone: {rag_system.pinecone_index_name}")
        st.sidebar.code(f"Directorio de Datos: {rag_system.data_dir}")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
                if "sources" in m and m["sources"]:
                    st.caption(f"Fuentes: {', '.join(m['sources'])}")

        if prompt := st.chat_input("Haz tu pregunta aquí..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Buscando y generando respuesta..."):
                    try:
                        response = rag_system.query(prompt)
                    except Exception as e:
                        st.error(f"Error durante la consulta: {e}")
                        response = {"answer": "Error procesando tu consulta.", "sources": []}

                    st.markdown(response.get("answer", ""))
                    sources = response.get("sources", [])
                    if sources:
                        st.caption(f"Fuentes: {', '.join(sources)}")

                st.session_state.messages.append(
                    {"role": "assistant", "content": response.get("answer",""), "sources": sources}
                )

        if mode == "Onboarding":
            st.subheader("🚀 Modo Onboarding")
            st.info("Información clave para tu incorporación.")
            st.markdown("**Vídeos críticos:**")
            st.video("https://www.youtube.com/watch?v=mwPzdgYi5Vo")
            st.markdown("**FAQs:**")
            st.write("- ¿Cómo solicito vacaciones?")
            st.write("- ¿Dónde encuentro la política de gastos?")
        elif mode == "Fuentes (Próximamente)":
            st.subheader("📚 Fuentes de Conocimiento")
            st.info("Aquí listaremos las fuentes indexadas. Próximamente.")
    else:
        st.error("El sistema RAG no pudo inicializarse. Revisa los mensajes de error.")