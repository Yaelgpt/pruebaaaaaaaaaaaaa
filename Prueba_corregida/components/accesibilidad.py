# components/accesibilidad.py
# Sistema completo de accesibilidad con TTS, modo oscuro/claro, daltonismo, dislexia, etc.
import streamlit as st
import tempfile
import os
import json
import pandas as pd
from services.database import DatabaseService
from services.rbac import usuario_id

# ===== ESTADO POR DEFECTO =====
_DEF = {
    "a11y_contraste": False,
    "a11y_dyslexia": False,
    "a11y_enfoque": False,
    "a11y_resaltar_focus": False,
    "a11y_texto": 100,
    "a11y_texto_login": 100,
    "a11y_tts_activo": False,
    "a11y_tts_velocidad": 1.0,
    "a11y_tts_voz": "es-ES",
    "a11y_tts_leyendo": False,
    "a11y_tts_hover": False,  # Nueva opción: leer al pasar cursor
    "a11y_ultimo_contenido": "",
    "a11y_modo_oscuro": False,
    "a11y_modo_daltonismo": "ninguno",
    "a11y_modo_concentracion": False,
    "a11y_espaciado_letras": 0.02,
    "a11y_espaciado_palabras": 0.0,
    "a11y_espaciado_lineas": 1.6,
    "a11y_config_cargada": False,
}

def _init_state():
    """Inicializa el estado de accesibilidad"""
    for k, v in _DEF.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ===== GESTIÓN DE CONFIGURACIÓN POR USUARIO =====

def _resetear_configuracion_a_defaults():
    """Resetea todos los valores de accesibilidad a los valores por defecto"""
    for k, v in _DEF.items():
        # No resetear estados temporales como a11y_tts_leyendo o a11y_ultimo_contenido
        if k not in ["a11y_tts_leyendo", "a11y_ultimo_contenido", "a11y_config_cargada", "a11y_usuario_configurado"]:
            st.session_state[k] = v

def cargar_configuracion_usuario():
    """Carga la configuración de accesibilidad del usuario desde la base de datos"""
    user_id = usuario_id()
    if not user_id:
        # Si no hay usuario, resetear a defaults
        _resetear_configuracion_a_defaults()
        return
    
    # Verificar si ya cargamos la configuración para este usuario específico
    usuario_actual = st.session_state.get("a11y_usuario_configurado")
    if usuario_actual == user_id and st.session_state.get("a11y_config_cargada", False):
        return
    
    # Si cambió el usuario, resetear primero a defaults
    if usuario_actual is not None and usuario_actual != user_id:
        _resetear_configuracion_a_defaults()
    
    try:
        db = DatabaseService()
        res = db.supabase.table("configuracion_accesibilidad").select("*").eq("usuario_id", user_id).limit(1).execute()
        
        if res.data and len(res.data) > 0:
            # Hay configuración guardada, cargarla
            config = res.data[0]
            st.session_state["a11y_tts_activo"] = config.get("tts_activo", False)
            st.session_state["a11y_tts_velocidad"] = float(config.get("tts_velocidad", 1.0))
            st.session_state["a11y_tts_voz"] = config.get("tts_voz", "es-ES")
            st.session_state["a11y_tts_hover"] = config.get("tts_hover", False)  # Leer al pasar cursor
            st.session_state["a11y_modo_oscuro"] = config.get("modo_oscuro", False)
            st.session_state["a11y_contraste"] = config.get("alto_contraste", False)
            st.session_state["a11y_modo_daltonismo"] = config.get("modo_daltonismo", "ninguno")
            st.session_state["a11y_texto"] = int(config.get("tamanio_texto", 100))
            st.session_state["a11y_texto_login"] = int(config.get("tamanio_texto_login", 100))
            st.session_state["a11y_dyslexia"] = config.get("fuente_dislexia", False)
            st.session_state["a11y_espaciado_letras"] = float(config.get("espaciado_letras", 0.02))
            st.session_state["a11y_espaciado_palabras"] = float(config.get("espaciado_palabras", 0.0))
            st.session_state["a11y_espaciado_lineas"] = float(config.get("espaciado_lineas", 1.6))
            st.session_state["a11y_modo_concentracion"] = config.get("modo_concentracion", False)
            st.session_state["a11y_resaltar_focus"] = config.get("resaltar_focus", False)
            st.session_state["a11y_enfoque"] = config.get("modo_enfoque", False)
        else:
            # No hay configuración guardada, usar defaults (ya están en _DEF)
            # Asegurar que los valores por defecto estén aplicados
            _resetear_configuracion_a_defaults()
        
        # Inicializar valores previos para detectar cambios (guardado automático)
        st.session_state["a11y_tts_activo_previo"] = st.session_state.get("a11y_tts_activo", False)
        st.session_state["a11y_tts_velocidad_previo"] = st.session_state.get("a11y_tts_velocidad", 1.0)
        st.session_state["a11y_tts_voz_previo"] = st.session_state.get("a11y_tts_voz", "es-ES")
        st.session_state["a11y_tts_hover_previo"] = st.session_state.get("a11y_tts_hover", False)
        st.session_state["a11y_modo_oscuro_previo"] = st.session_state.get("a11y_modo_oscuro", False)
        st.session_state["a11y_contraste_previo"] = st.session_state.get("a11y_contraste", False)
        st.session_state["a11y_modo_daltonismo_previo"] = st.session_state.get("a11y_modo_daltonismo", "ninguno")
        st.session_state["a11y_texto_previo"] = st.session_state.get("a11y_texto", 100)
        st.session_state["a11y_texto_login_previo"] = st.session_state.get("a11y_texto_login", 100)
        st.session_state["a11y_dyslexia_previo"] = st.session_state.get("a11y_dyslexia", False)
        st.session_state["a11y_espaciado_letras_previo"] = st.session_state.get("a11y_espaciado_letras", 0.02)
        st.session_state["a11y_espaciado_palabras_previo"] = st.session_state.get("a11y_espaciado_palabras", 0.0)
        st.session_state["a11y_espaciado_lineas_previo"] = st.session_state.get("a11y_espaciado_lineas", 1.6)
        st.session_state["a11y_modo_concentracion_previo"] = st.session_state.get("a11y_modo_concentracion", False)
        st.session_state["a11y_resaltar_focus_previo"] = st.session_state.get("a11y_resaltar_focus", False)
        st.session_state["a11y_enfoque_previo"] = st.session_state.get("a11y_enfoque", False)
        
        # Marcar que la configuración está cargada para este usuario
        st.session_state["a11y_config_cargada"] = True
        st.session_state["a11y_usuario_configurado"] = user_id
    except Exception as e:
        st.warning(f"No se pudo cargar configuración: {e}")
        # Si hay error, usar defaults
        _resetear_configuracion_a_defaults()
        # Marcar como cargada incluso si falla para evitar intentos repetidos
        st.session_state["a11y_config_cargada"] = True
        st.session_state["a11y_usuario_configurado"] = user_id

def guardar_configuracion_usuario(silencioso=False):
    """Guarda la configuración de accesibilidad del usuario en la base de datos"""
    user_id = usuario_id()
    if not user_id:
        return False
    
    try:
        db = DatabaseService()
        config = {
            "usuario_id": user_id,
            "tts_activo": st.session_state.get("a11y_tts_activo", False),
            "tts_velocidad": float(st.session_state.get("a11y_tts_velocidad", 1.0)),
            "tts_voz": st.session_state.get("a11y_tts_voz", "es-ES"),
            "tts_hover": st.session_state.get("a11y_tts_hover", False),  # Leer al pasar cursor
            "modo_oscuro": st.session_state.get("a11y_modo_oscuro", False),
            "alto_contraste": st.session_state.get("a11y_contraste", False),
            "modo_daltonismo": st.session_state.get("a11y_modo_daltonismo", "ninguno"),
            "tamanio_texto": int(st.session_state.get("a11y_texto", 100)),
            "tamanio_texto_login": int(st.session_state.get("a11y_texto_login", 100)),
            "fuente_dislexia": st.session_state.get("a11y_dyslexia", False),
            "espaciado_letras": float(st.session_state.get("a11y_espaciado_letras", 0.02)),
            "espaciado_palabras": float(st.session_state.get("a11y_espaciado_palabras", 0.0)),
            "espaciado_lineas": float(st.session_state.get("a11y_espaciado_lineas", 1.6)),
            "modo_concentracion": st.session_state.get("a11y_modo_concentracion", False),
            "resaltar_focus": st.session_state.get("a11y_resaltar_focus", False),
            "modo_enfoque": st.session_state.get("a11y_enfoque", False),
        }
        
        # Upsert (insertar o actualizar)
        db.supabase.table("configuracion_accesibilidad").upsert(
            config,
            on_conflict="usuario_id"
        ).execute()
        
        st.session_state["a11y_config_cargada"] = True
        return True
    except Exception as e:
        if not silencioso:
            st.error(f"Error al guardar configuración: {e}")
        return False

def _guardar_si_cambio(campo, valor_actual, valor_anterior_key):
    """Guarda automáticamente si detecta un cambio en un campo"""
    if usuario_id():
        valor_anterior = st.session_state.get(valor_anterior_key)
        if valor_anterior != valor_actual:
            st.session_state[valor_anterior_key] = valor_actual
            guardar_configuracion_usuario(silencioso=True)

# ===== CSS Y ESTILOS =====

def _inject(css_or_html: str):
    """Inyecta CSS o HTML en la página"""
    if css_or_html:
        st.markdown(css_or_html, unsafe_allow_html=True)

def _css_base(text_scale: int) -> str:
    """CSS base para tamaño de texto"""
    return f"""
    <style>
      html {{ font-size: {text_scale}% !important; }}
      * {{ text-shadow: none !important; }}
    </style>
    """

def _css_login(text_scale: int) -> str:
    """CSS para aumentar tamaño de texto en login"""
    return f"""
    <style>
      [data-testid="stForm"] *,
      [data-testid="stForm"] input,
      [data-testid="stForm"] button,
      [data-testid="stForm"] label {{
        font-size: {text_scale}% !important;
      }}
      .login-card * {{
        font-size: {text_scale}% !important;
      }}
    </style>
    """

def _css_dyslexia(espaciado_letras: float, espaciado_palabras: float, espaciado_lineas: float) -> str:
    """CSS para tipografías legibles para dislexia con espaciado ajustable"""
    return f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600&display=swap');
      @import url('https://fonts.googleapis.com/css2?family=OpenDyslexic:wght@400;700&display=swap');
      @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@400;700&display=swap');

      /* Aplicar fuente para dislexia */
      [data-testid="stAppViewContainer"] h1,
      [data-testid="stAppViewContainer"] h2,
      [data-testid="stAppViewContainer"] h3,
      [data-testid="stAppViewContainer"] h4,
      [data-testid="stAppViewContainer"] h5,
      [data-testid="stAppViewContainer"] h6,
      [data-testid="stAppViewContainer"] p,
      [data-testid="stAppViewContainer"] li,
      [data-testid="stAppViewContainer"] label,
      [data-testid="stAppViewContainer"] th,
      [data-testid="stAppViewContainer"] td,
      [data-testid="stAppViewContainer"] button,
      [data-testid="stAppViewContainer"] input,
      [data-testid="stAppViewContainer"] select,
      [data-testid="stAppViewContainer"] textarea,
      [data-testid="stSidebarContent"] h1,
      [data-testid="stSidebarContent"] h2,
      [data-testid="stSidebarContent"] h3,
      [data-testid="stSidebarContent"] h4,
      [data-testid="stSidebarContent"] h5,
      [data-testid="stSidebarContent"] h6,
      [data-testid="stSidebarContent"] p,
      [data-testid="stSidebarContent"] li,
      [data-testid="stSidebarContent"] label,
      [data-testid="stSidebarContent"] th,
      [data-testid="stSidebarContent"] td,
      [data-testid="stSidebarContent"] button,
      [data-testid="stSidebarContent"] input,
      [data-testid="stSidebarContent"] select,
      [data-testid="stSidebarContent"] textarea {{
        font-family: 'Lexend', 'Comic Neue', system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif !important;
        line-height: {espaciado_lineas} !important;
        letter-spacing: {espaciado_letras}em !important;
        word-spacing: {espaciado_palabras}em !important;
      }}

      /* Protege iconos */
      .material-icons,
      [class^="material-icons"],
      [class*=" material-icons"],
      [aria-hidden="true"] {{
        font-family: inherit !important;
        letter-spacing: normal !important;
        word-spacing: normal !important;
      }}
    </style>
    """

def _css_modo_oscuro() -> str:
    """CSS para modo oscuro con mejor cobertura de elementos"""
    return """
    <style>
      :root {
        --a11y-bg-dark: #1a1a1a;
        --a11y-card-dark: #2d2d2d;
        --a11y-text-dark: #e0e0e0;
        --a11y-text-light: #ffffff;
        --a11y-border-dark: #4a4a4a;
        --a11y-accent-dark: #4a9eff;
      }
      
      /* Fondo principal */
      html, body, [data-testid="stAppViewContainer"] {
        background: var(--a11y-bg-dark) !important;
        color: var(--a11y-text-dark) !important;
      }
      
      /* Header, Sidebar, Toolbar */
      [data-testid="stHeader"],
      [data-testid="stSidebar"],
      [data-testid="stToolbar"] {
        background: var(--a11y-card-dark) !important;
        color: var(--a11y-text-dark) !important;
      }
      
      /* Todos los textos */
      p, span, div, label, li, td, th, caption, 
      [data-testid="stAppViewContainer"] *,
      [data-testid="stSidebar"] * {
        color: var(--a11y-text-dark) !important;
      }
      
      /* Títulos */
      h1, h2, h3, h4, h5, h6,
      .main-header, .sub-header,
      [data-testid="stAppViewContainer"] h1,
      [data-testid="stAppViewContainer"] h2,
      [data-testid="stAppViewContainer"] h3,
      [data-testid="stAppViewContainer"] h4,
      [data-testid="stAppViewContainer"] h5,
      [data-testid="stAppViewContainer"] h6 {
        color: var(--a11y-text-light) !important;
      }
      
      /* Controles de formulario */
      .stButton>button,
      .stDownloadButton>button,
      .stCheckbox, .stRadio, .stSelectbox, 
      .stTextInput, .stNumberInput, .stTextArea,
      [data-baseweb="select"] > div,
      input, textarea, select,
      [data-baseweb="input"] input {
        background: var(--a11y-card-dark) !important;
        color: var(--a11y-text-dark) !important;
        border: 1px solid var(--a11y-border-dark) !important;
      }
      
      /* Labels de controles */
      .stCheckbox label,
      .stRadio label,
      .stSelectbox label,
      .stTextInput label,
      .stNumberInput label,
      .stTextArea label,
      label[data-baseweb="label"] {
        color: var(--a11y-text-dark) !important;
      }
      
      /* Métricas */
      .stMetric {
        color: var(--a11y-text-light) !important;
      }
      .stMetric label {
        color: var(--a11y-text-dark) !important;
      }
      .stMetric [data-testid="stMetricValue"] {
        color: var(--a11y-text-light) !important;
      }
      
      /* DataFrames y tablas */
      .stDataFrame,
      table,
      .dataframe {
        color: var(--a11y-text-dark) !important;
        background: var(--a11y-card-dark) !important;
      }
      .stDataFrame th,
      table th,
      .dataframe th {
        background: var(--a11y-bg-dark) !important;
        color: var(--a11y-text-light) !important;
      }
      .stDataFrame td,
      table td,
      .dataframe td {
        color: var(--a11y-text-dark) !important;
        background: var(--a11y-card-dark) !important;
      }
      
      /* Enlaces */
      a {
        color: var(--a11y-accent-dark) !important;
      }
      
      /* Captions y textos pequeños */
      .stCaption,
      caption,
      small {
        color: var(--a11y-text-dark) !important;
      }
      
      /* Expanders */
      [data-testid="stExpander"] {
        background: var(--a11y-card-dark) !important;
        color: var(--a11y-text-dark) !important;
      }
      [data-testid="stExpander"] summary,
      [data-testid="stExpander"] label {
        color: var(--a11y-text-dark) !important;
      }
      
      /* Sliders */
      .stSlider label {
        color: var(--a11y-text-dark) !important;
      }
      .stSlider [data-baseweb="slider"] {
        color: var(--a11y-accent-dark) !important;
      }
      
      /* Tabs */
      [data-baseweb="tab"] {
        color: var(--a11y-text-dark) !important;
      }
      [data-baseweb="tab"][aria-selected="true"] {
        color: var(--a11y-text-light) !important;
      }
      
      /* Info, Success, Warning, Error boxes */
      .stInfo,
      .stSuccess,
      .stWarning,
      .stError {
        background: var(--a11y-card-dark) !important;
        color: var(--a11y-text-dark) !important;
      }
      
      /* Markdown */
      [data-testid="stMarkdownContainer"] {
        color: var(--a11y-text-dark) !important;
      }
      [data-testid="stMarkdownContainer"] p {
        color: var(--a11y-text-dark) !important;
      }
      
      /* Clases personalizadas del proyecto */
      .main-header,
      .sub-header {
        color: var(--a11y-text-light) !important;
      }
      .metric-card {
        background: var(--a11y-card-dark) !important;
        color: var(--a11y-text-dark) !important;
      }
      .success-text {
        color: #4ade80 !important;
      }
      .warning-text {
        color: #fbbf24 !important;
      }
      .danger-text {
        color: #f87171 !important;
      }
    </style>
    """

def _css_contraste_alto() -> str:
    """CSS para alto contraste en modo blanco"""
    return """
    <style>
      :root {
        --a11y-bg-hc: #ffffff;
        --a11y-card-hc: #f0f0f0;
        --a11y-text-hc: #000000;
        --a11y-accent-hc: #0000ff;
        --a11y-border-hc: #000000;
      }
      html, body, [data-testid="stAppViewContainer"] {
        background: var(--a11y-bg-hc) !important;
        color: var(--a11y-text-hc) !important;
      }
      [data-testid="stHeader"],
      [data-testid="stSidebar"],
      [data-testid="stToolbar"] {
        background: var(--a11y-card-hc) !important;
        color: var(--a11y-text-hc) !important;
        border: 2px solid var(--a11y-border-hc) !important;
      }
      .stButton>button,
      .stDownloadButton>button,
      .stCheckbox, .stRadio, .stSelectbox, .stTextInput, .stNumberInput, .stTextArea,
      [data-baseweb="select"] > div,
      input, textarea, select {
        background: var(--a11y-bg-hc) !important;
        color: var(--a11y-text-hc) !important;
        border: 3px solid var(--a11y-border-hc) !important;
      }
      a { color: var(--a11y-accent-hc) !important; text-decoration: underline !important; font-weight: bold !important; }
      .stDataFrame, .stMetric { 
        color: var(--a11y-text-hc) !important; 
        border: 2px solid var(--a11y-border-hc) !important;
      }
      h1, h2, h3, h4, h5, h6 { 
        color: var(--a11y-text-hc) !important; 
        border-bottom: 2px solid var(--a11y-border-hc) !important;
      }
    </style>
    """

def _css_contraste_alto_oscuro() -> str:
    """CSS para alto contraste en modo oscuro - máximo contraste en fondo negro"""
    return """
    <style>
      :root {
        --a11y-bg-hc-dark: #000000;
        --a11y-card-hc-dark: #1a1a1a;
        --a11y-text-hc-dark: #ffffff;
        --a11y-accent-hc-dark: #00ffff;
        --a11y-border-hc-dark: #ffffff;
        --a11y-warning-hc-dark: #ffff00;
        --a11y-success-hc-dark: #00ff00;
        --a11y-error-hc-dark: #ff0000;
      }
      html, body, [data-testid="stAppViewContainer"] {
        background: var(--a11y-bg-hc-dark) !important;
        color: var(--a11y-text-hc-dark) !important;
      }
      [data-testid="stHeader"],
      [data-testid="stToolbar"] {
        background: var(--a11y-bg-hc-dark) !important;
        color: var(--a11y-text-hc-dark) !important;
        border-bottom: 3px solid var(--a11y-border-hc-dark) !important;
      }
      [data-testid="stSidebar"] {
        background: var(--a11y-card-hc-dark) !important;
        color: var(--a11y-text-hc-dark) !important;
        border-right: 3px solid var(--a11y-border-hc-dark) !important;
      }
      /* Todos los textos blancos */
      p, span, div, label, li, td, th, caption, 
      [data-testid="stAppViewContainer"] *,
      [data-testid="stSidebar"] * {
        color: var(--a11y-text-hc-dark) !important;
      }
      /* Títulos con borde inferior */
      h1, h2, h3, h4, h5, h6 { 
        color: var(--a11y-text-hc-dark) !important; 
        border-bottom: 3px solid var(--a11y-accent-hc-dark) !important;
        padding-bottom: 5px !important;
      }
      /* Controles con bordes blancos gruesos */
      .stButton>button,
      .stDownloadButton>button {
        background: var(--a11y-card-hc-dark) !important;
        color: var(--a11y-text-hc-dark) !important;
        border: 3px solid var(--a11y-border-hc-dark) !important;
        font-weight: bold !important;
      }
      .stButton>button:hover,
      .stDownloadButton>button:hover {
        background: var(--a11y-accent-hc-dark) !important;
        color: var(--a11y-bg-hc-dark) !important;
      }
      .stCheckbox, .stRadio, .stSelectbox, .stTextInput, .stNumberInput, .stTextArea,
      [data-baseweb="select"] > div,
      input, textarea, select {
        background: var(--a11y-card-hc-dark) !important;
        color: var(--a11y-text-hc-dark) !important;
        border: 3px solid var(--a11y-border-hc-dark) !important;
      }
      /* Links cyan brillante */
      a { 
        color: var(--a11y-accent-hc-dark) !important; 
        text-decoration: underline !important; 
        font-weight: bold !important; 
      }
      /* Tablas con alto contraste */
      .stDataFrame, table {
        border: 3px solid var(--a11y-border-hc-dark) !important;
      }
      .stDataFrame th, table th {
        background: var(--a11y-accent-hc-dark) !important;
        color: var(--a11y-bg-hc-dark) !important;
        border: 2px solid var(--a11y-border-hc-dark) !important;
        font-weight: bold !important;
      }
      .stDataFrame td, table td {
        background: var(--a11y-card-hc-dark) !important;
        color: var(--a11y-text-hc-dark) !important;
        border: 1px solid var(--a11y-border-hc-dark) !important;
      }
      /* Métricas */
      .stMetric { 
        color: var(--a11y-text-hc-dark) !important; 
        border: 3px solid var(--a11y-accent-hc-dark) !important;
        padding: 10px !important;
        background: var(--a11y-card-hc-dark) !important;
      }
      [data-testid="stMetricValue"] {
        color: var(--a11y-accent-hc-dark) !important;
        font-weight: bold !important;
      }
      /* Alertas con colores brillantes */
      [data-testid="stAlert"][data-baseweb*="success"],
      .stSuccess {
        background: var(--a11y-card-hc-dark) !important;
        border: 3px solid var(--a11y-success-hc-dark) !important;
        color: var(--a11y-success-hc-dark) !important;
      }
      [data-testid="stAlert"][data-baseweb*="warning"],
      .stWarning {
        background: var(--a11y-card-hc-dark) !important;
        border: 3px solid var(--a11y-warning-hc-dark) !important;
        color: var(--a11y-warning-hc-dark) !important;
      }
      [data-testid="stAlert"][data-baseweb*="error"],
      .stError {
        background: var(--a11y-card-hc-dark) !important;
        border: 3px solid var(--a11y-error-hc-dark) !important;
        color: var(--a11y-error-hc-dark) !important;
      }
      /* Expanders */
      [data-testid="stExpander"] {
        border: 2px solid var(--a11y-border-hc-dark) !important;
        background: var(--a11y-card-hc-dark) !important;
      }
      [data-testid="stExpander"] summary {
        color: var(--a11y-text-hc-dark) !important;
        font-weight: bold !important;
      }
    </style>
    """

def _css_daltonismo(tipo: str) -> str:
    """CSS completo para modos de daltonismo - cubre TODA la interfaz"""
    if tipo == "ninguno":
        return ""
    
    # CSS base común para todos los modos de daltonismo
    css_base = """
      /* ===== ALERTAS Y NOTIFICACIONES ===== */
      [data-testid="stAlert"] {{
        border-left-width: 5px !important;
      }}
      
      /* ===== TABLAS ===== */
      [data-testid="stTable"] th,
      [data-testid="stDataFrame"] th,
      .stDataFrame th {{
        background-color: {table_header} !important;
        color: white !important;
      }}
      [data-testid="stTable"] tr:nth-child(even),
      [data-testid="stDataFrame"] tr:nth-child(even),
      .stDataFrame tr:nth-child(even) {{
        background-color: {table_stripe} !important;
      }}
      
      /* ===== CHECKBOXES Y RADIO ===== */
      [data-testid="stCheckbox"] input:checked + div {{
        background-color: {primary} !important;
        border-color: {primary} !important;
      }}
      [data-testid="stRadio"] input:checked + div {{
        border-color: {primary} !important;
      }}
      [data-testid="stRadio"] input:checked + div::before {{
        background-color: {primary} !important;
      }}
      
      /* ===== SLIDERS ===== */
      [data-testid="stSlider"] [data-testid="stThumbValue"] {{
        color: {primary} !important;
      }}
      .stSlider > div > div > div {{
        background-color: {primary} !important;
      }}
      
      /* ===== SELECTBOX ===== */
      [data-testid="stSelectbox"] > div > div {{
        border-color: {primary} !important;
      }}
      
      /* ===== MÉTRICAS ===== */
      [data-testid="stMetricValue"] {{
        color: {metric_value} !important;
      }}
      [data-testid="stMetricDelta"] svg {{
        fill: {metric_delta} !important;
      }}
      
      /* ===== TABS ===== */
      [data-testid="stTab"][aria-selected="true"] {{
        border-bottom-color: {primary} !important;
        color: {primary} !important;
      }}
      
      /* ===== EXPANDER ===== */
      [data-testid="stExpander"] summary {{
        color: {primary} !important;
      }}
      [data-testid="stExpander"] {{
        border-color: {border} !important;
      }}
      
      /* ===== PROGRESS BAR ===== */
      .stProgress > div > div {{
        background-color: {primary} !important;
      }}
      
      /* ===== SPINNER ===== */
      .stSpinner > div {{
        border-top-color: {primary} !important;
      }}
      
      /* ===== GRÁFICAS - Matplotlib/Plotly ===== */
      /* Forzar colores en SVG de gráficas */
      .stPlotlyChart svg .trace.bars .point {{
        fill: {chart_bar} !important;
      }}
      .stPlotlyChart svg .trace.scatter .point {{
        fill: {chart_scatter} !important;
      }}
      
      /* ===== LOGIN ===== */
      [data-testid="stForm"] {{
        border-color: {border} !important;
      }}
      [data-testid="stForm"] button[type="submit"] {{
        background-color: {primary} !important;
        border-color: {primary} !important;
      }}
      
      /* ===== SIDEBAR ===== */
      [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
      }}
      [data-testid="stSidebar"] [data-testid="stMarkdown"],
      [data-testid="stSidebar"] [data-testid="stMarkdown"] p,
      [data-testid="stSidebar"] [data-testid="stMarkdown"] span,
      [data-testid="stSidebar"] [data-testid="stMarkdown"] h1,
      [data-testid="stSidebar"] [data-testid="stMarkdown"] h2,
      [data-testid="stSidebar"] [data-testid="stMarkdown"] h3 {{
        color: {sidebar_text} !important;
      }}
      [data-testid="stSidebar"] label,
      [data-testid="stSidebar"] .stRadio label,
      [data-testid="stSidebar"] .stRadio label span,
      [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
      [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
        color: {sidebar_text} !important;
      }}
      /* Radio buttons en sidebar */
      [data-testid="stSidebar"] [role="radiogroup"] label,
      [data-testid="stSidebar"] [role="radiogroup"] label span,
      [data-testid="stSidebar"] [role="radiogroup"] label p,
      [data-testid="stSidebar"] [data-baseweb="radio"] label {{
        color: {sidebar_text} !important;
      }}
      /* Texto de caption en sidebar */
      [data-testid="stSidebar"] .stCaption,
      [data-testid="stSidebar"] small,
      [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
        color: {sidebar_text} !important;
        opacity: 0.9 !important;
      }}
      
      /* ===== BOTÓN COLAPSAR SIDEBAR ===== */
      [data-testid="collapsedControl"],
      [data-testid="stSidebarCollapseButton"],
      button[kind="header"],
      [data-testid="baseButton-header"] {{
        background-color: {sidebar_collapse_bg} !important;
        border: 2px solid {sidebar_collapse_border} !important;
        border-radius: 8px !important;
      }}
      [data-testid="collapsedControl"] svg,
      [data-testid="stSidebarCollapseButton"] svg,
      button[kind="header"] svg,
      [data-testid="baseButton-header"] svg {{
        fill: {sidebar_collapse_icon} !important;
        stroke: {sidebar_collapse_icon} !important;
        color: {sidebar_collapse_icon} !important;
      }}
      [data-testid="collapsedControl"]:hover,
      [data-testid="stSidebarCollapseButton"]:hover,
      button[kind="header"]:hover {{
        background-color: {sidebar_collapse_hover} !important;
      }}
      
      /* ===== BOTONES ===== */
      .stButton > button {{
        background-color: {primary} !important;
        border-color: {primary} !important;
        color: white !important;
      }}
      .stButton > button:hover {{
        background-color: {primary_hover} !important;
        border-color: {primary_hover} !important;
      }}
      .stButton > button[kind="secondary"] {{
        background-color: {secondary} !important;
        border-color: {secondary} !important;
      }}
      
      /* ===== HEADERS ===== */
      .main-header, h1 {{
        color: {header} !important;
      }}
      .sub-header, h2, h3 {{
        color: {subheader} !important;
      }}
      
      /* ===== LINKS ===== */
      a {{
        color: {link} !important;
      }}
      a:hover {{
        color: {link_hover} !important;
      }}
      
      /* ===== TEXTOS DE ESTADO ===== */
      .success-text {{ color: {success} !important; }}
      .warning-text {{ color: {warning} !important; }}
      .danger-text {{ color: {danger} !important; }}
      
      /* ===== ALERTAS STREAMLIT - COBERTURA COMPLETA ===== */
      /* Success alerts */
      [data-testid="stAlert"][data-baseweb="notification"][kind="success"],
      .stSuccess,
      div[data-testid="stNotification"][data-type="success"],
      [data-testid="stAlert"] div[role="alert"][data-baseweb="notification"]:has(svg[data-testid="stIconSuccess"]),
      div[data-baseweb="notification"][kind="positive"],
      .element-container:has([data-testid="stAlert"]) div[style*="background-color: rgb(212, 237, 218)"],
      .element-container:has([data-testid="stAlert"]) div[style*="background-color: rgba(212, 237, 218"],
      div[data-baseweb="notification"][style*="background-color: rgb(212, 237, 218)"],
      div[data-baseweb="notification"][style*="rgba(212, 237, 218"] {{
        background-color: {success_bg} !important;
        border-left-color: {success} !important;
        border-left-width: 5px !important;
        border-left-style: solid !important;
      }}
      /* Success text color */
      [data-testid="stAlert"][data-baseweb="notification"][kind="success"] p,
      .stSuccess p,
      div[data-baseweb="notification"][kind="positive"] p {{
        color: {success} !important;
      }}
      
      /* Warning alerts */
      [data-testid="stAlert"][data-baseweb="notification"][kind="warning"],
      .stWarning,
      div[data-testid="stNotification"][data-type="warning"],
      div[data-baseweb="notification"][kind="warning"] {{
        background-color: {warning_bg} !important;
        border-left-color: {warning} !important;
        border-left-width: 5px !important;
        border-left-style: solid !important;
      }}
      
      /* Error alerts */
      [data-testid="stAlert"][data-baseweb="notification"][kind="error"],
      .stError,
      div[data-testid="stNotification"][data-type="error"],
      div[data-baseweb="notification"][kind="negative"] {{
        background-color: {danger_bg} !important;
        border-left-color: {danger} !important;
        border-left-width: 5px !important;
        border-left-style: solid !important;
      }}
      
      /* Info alerts */
      [data-testid="stAlert"][data-baseweb="notification"][kind="info"],
      .stInfo,
      div[data-testid="stNotification"][data-type="info"],
      div[data-baseweb="notification"][kind="info"] {{
        background-color: {info_bg} !important;
        border-left-color: {info} !important;
        border-left-width: 5px !important;
        border-left-style: solid !important;
      }}
      
      /* ===== COBERTURA EXTRA PARA ALERTAS STREAMLIT ===== */
      /* Cualquier div con fondo verde claro (st.success) */
      div[style*="background-color: rgb(212, 237, 218)"],
      div[style*="background: rgb(212, 237, 218)"],
      div[style*="rgba(212, 237, 218"],
      div[style*="#d4edda"],
      div[style*="background-color: rgba(40, 167, 69"],
      [data-testid="stAlert"] > div,
      [data-testid="stAlert"] > div > div {{
        background-color: {success_bg} !important;
        border-left: 5px solid {success} !important;
      }}
      /* Texto dentro de success */
      [data-testid="stAlert"] p,
      [data-testid="stAlert"] span {{
        color: {success} !important;
      }}
      
      /* ===== METRIC CARDS ===== */
      .metric-card {{
        border-left-color: {primary} !important;
      }}
      
      /* ===== DATAFRAME COLORES ===== */
      [data-testid="stDataFrame"] [data-testid="StyledLinkIconContainer"] {{
        color: {primary} !important;
      }}
    """
    
    if tipo == "protanopia":
        # Protanopia: NO ve rojos - usar AZULES y AMARILLOS (sin rojos)
        colores = {
            "primary": "#0066CC",
            "primary_hover": "#004C99",
            "secondary": "#FFD700",
            "header": "#003366",
            "subheader": "#004080",
            "link": "#0055AA",
            "link_hover": "#003366",
            "success": "#0066CC",  # Azul en vez de verde
            "success_bg": "#D6EAFF",  # Fondo azul claro más visible
            "warning": "#CC9900",  # Amarillo oscuro
            "warning_bg": "#FFF8E6",
            "danger": "#660066",  # Púrpura en vez de rojo
            "danger_bg": "#F5E6F5",
            "info": "#0099CC",
            "info_bg": "#E6F7FF",
            "sidebar_bg": "#1a1a3a",
            "sidebar_text": "#FFFFFF",  # Blanco puro para máximo contraste
            "sidebar_collapse_bg": "#FFD700",  # Amarillo brillante para visibilidad
            "sidebar_collapse_border": "#CC9900",
            "sidebar_collapse_icon": "#003366",  # Azul oscuro para contraste
            "sidebar_collapse_hover": "#FFCC00",
            "border": "#0066CC",
            "table_header": "#003366",
            "table_stripe": "#F0F5FF",
            "metric_value": "#003366",
            "metric_delta": "#0066CC",
            "chart_bar": "#FFB800",  # Amarillo/dorado para barras (muy distinto al azul)
            "chart_scatter": "#7B2D8E",  # Púrpura para scatter
        }
    
    elif tipo == "deuteranopia":
        # Deuteranopia: NO ve verdes - usar AZULES y NARANJAS (sin verdes)
        colores = {
            "primary": "#0055AA",
            "primary_hover": "#003D7A",
            "secondary": "#FF6600",
            "header": "#003366",
            "subheader": "#0055AA",
            "link": "#0066CC",
            "link_hover": "#004080",
            "success": "#0077BB",  # Azul en vez de verde
            "success_bg": "#D6EAFF",  # Fondo azul claro más visible
            "warning": "#FF6600",  # Naranja brillante
            "warning_bg": "#FFE6CC",
            "danger": "#CC0066",  # Magenta en vez de rojo
            "danger_bg": "#FFE6F0",
            "info": "#0099CC",
            "info_bg": "#E6FAFF",
            "sidebar_bg": "#1a2a4a",
            "sidebar_text": "#FFFFFF",  # Blanco puro para máximo contraste
            "sidebar_collapse_bg": "#FF6600",  # Naranja brillante para visibilidad
            "sidebar_collapse_border": "#CC5500",
            "sidebar_collapse_icon": "#FFFFFF",  # Blanco para contraste
            "sidebar_collapse_hover": "#FF8800",
            "border": "#0055AA",
            "table_header": "#003355",
            "table_stripe": "#F0F8FF",
            "metric_value": "#003366",
            "metric_delta": "#0055AA",
            "chart_bar": "#FF6600",  # Naranja para barras (muy distinto al azul)
            "chart_scatter": "#0055AA",  # Azul para scatter
        }
    
    elif tipo == "tritanopia":
        # Tritanopia: NO ve azules - usar ROJOS y VERDES (sin azules)
        colores = {
            "primary": "#CC3300",
            "primary_hover": "#992200",
            "secondary": "#009933",
            "header": "#8B0000",
            "subheader": "#CC3300",
            "link": "#990000",
            "link_hover": "#660000",
            "success": "#006600",  # Verde oscuro
            "success_bg": "#D4EDDA",  # Verde claro más visible
            "warning": "#FF6600",  # Naranja
            "warning_bg": "#FFE6CC",
            "danger": "#990000",  # Rojo oscuro
            "danger_bg": "#F8D7DA",
            "info": "#996600",  # Marrón/ocre
            "info_bg": "#FFF8E6",
            "sidebar_bg": "#2d2d1e",
            "sidebar_text": "#FFFFFF",  # Blanco puro para máximo contraste
            "sidebar_collapse_bg": "#CC3300",  # Rojo para visibilidad
            "sidebar_collapse_border": "#990000",
            "sidebar_collapse_icon": "#FFFFFF",  # Blanco para contraste
            "sidebar_collapse_hover": "#FF4400",
            "border": "#CC3300",
            "table_header": "#663300",
            "table_stripe": "#FFF8F0",
            "metric_value": "#663300",
            "metric_delta": "#CC3300",
            "chart_bar": "#CC3300",  # Rojo para barras
            "chart_scatter": "#009933",  # Verde para scatter
        }
    else:
        return ""
    
    return f"<style>{css_base.format(**colores)}</style>"


# Paletas de colores para gráficas según tipo de daltonismo
# Colores MUY DISTINTOS al azul original de matplotlib
PALETAS_DALTONISMO = {
    "ninguno": None,  # Usar colores por defecto
    # Protanopia: Amarillos/Dorados para barras, Púrpura para líneas (sin rojos)
    "protanopia": ["#FFB800", "#7B2D8E", "#0066CC", "#00CCCC", "#CC9900", "#003366", "#9966CC", "#FFCC00"],
    # Deuteranopia: Naranjas para barras, Azul para líneas (sin verdes)
    "deuteranopia": ["#FF6600", "#0055AA", "#CC0066", "#00AACC", "#996600", "#003355", "#FF9933", "#6699CC"],
    # Tritanopia: Rojos para barras, Verde para líneas (sin azules)
    "tritanopia": ["#CC3300", "#009933", "#990000", "#996600", "#006600", "#663300", "#FF6633", "#339966"],
}

def obtener_paleta_daltonismo():
    """Devuelve la paleta de colores según el modo de daltonismo activo"""
    modo = st.session_state.get("a11y_modo_daltonismo", "ninguno")
    return PALETAS_DALTONISMO.get(modo, None)

def obtener_colores_grafica(n_colores=1):
    """
    Devuelve colores para gráficas según el modo de daltonismo activo.
    
    Args:
        n_colores: Número de colores necesarios
    
    Returns:
        Lista de colores hex o None si no hay modo de daltonismo activo
    """
    paleta = obtener_paleta_daltonismo()
    if paleta is None:
        return None
    
    # Repetir paleta si se necesitan más colores
    if n_colores <= len(paleta):
        return paleta[:n_colores]
    else:
        repeticiones = (n_colores // len(paleta)) + 1
        return (paleta * repeticiones)[:n_colores]

def configurar_matplotlib_daltonismo():
    """
    Configura matplotlib para usar colores accesibles según el modo de daltonismo.
    Llamar antes de crear gráficas.
    
    Returns:
        dict con configuración de colores o None si no hay modo activo
    """
    import matplotlib.pyplot as plt
    
    modo = st.session_state.get("a11y_modo_daltonismo", "ninguno")
    if modo == "ninguno":
        return None
    
    paleta = PALETAS_DALTONISMO.get(modo, None)
    if paleta is None:
        return None
    
    # Configurar ciclo de colores de matplotlib
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=paleta)
    
    # Colores específicos según modo - BARRAS MUY DISTINTAS al azul original
    if modo == "protanopia":
        config = {
            "bar_color": "#FFB800",  # Amarillo/dorado para barras
            "line_color": "#7B2D8E",  # Púrpura para líneas
            "scatter_color": "#0066CC",
            "bg_color": "#F5F8FF",
            "grid_color": "#CCDDFF",
            "text_color": "#003366",
            "edge_color": "#003366",
        }
    elif modo == "deuteranopia":
        config = {
            "bar_color": "#FF6600",  # Naranja para barras
            "line_color": "#0055AA",  # Azul para líneas
            "scatter_color": "#CC0066",
            "bg_color": "#F5F8FF",
            "grid_color": "#CCE0FF",
            "text_color": "#003355",
            "edge_color": "#003355",
        }
    elif modo == "tritanopia":
        config = {
            "bar_color": "#CC3300",  # Rojo para barras
            "line_color": "#009933",  # Verde para líneas
            "scatter_color": "#996600",
            "bg_color": "#FFFAF5",
            "grid_color": "#FFE0CC",
            "text_color": "#663300",
            "edge_color": "#663300",
        }
    else:
        return None
    
    return config

def aplicar_colores_figura(fig, ax):
    """
    Aplica colores de daltonismo a una figura de matplotlib existente.
    
    Args:
        fig: Figura de matplotlib
        ax: Axes de matplotlib
    """
    config = configurar_matplotlib_daltonismo()
    if config is None:
        return
    
    # Aplicar colores de fondo y texto
    fig.patch.set_facecolor(config["bg_color"])
    ax.set_facecolor(config["bg_color"])
    ax.tick_params(colors=config["text_color"])
    ax.xaxis.label.set_color(config["text_color"])
    ax.yaxis.label.set_color(config["text_color"])
    ax.title.set_color(config["text_color"])
    
    # Configurar grid
    ax.grid(True, color=config["grid_color"], linestyle='-', linewidth=0.5, alpha=0.7)
    
    # Configurar bordes
    for spine in ax.spines.values():
        spine.set_color(config["edge_color"])

def _css_modo_enfoque() -> str:
    """CSS para modo enfoque/concentración"""
    return """
    <style>
      [data-testid="stAppViewBlockContainer"] > div {
        max-width: 1100px;
        margin-left: auto;
        margin-right: auto;
      }
      [data-testid="stSidebar"] { 
        filter: grayscale(1) brightness(0.7) !important; 
        opacity: 0.6 !important;
      }
      [data-testid="stHeader"] {
        filter: grayscale(0.5) !important;
      }
    </style>
    """

def _css_resaltar_focus() -> str:
    """CSS para resaltar foco de teclado - MUY VISIBLE - Cubre TODOS los elementos"""
    return """
    <style>
      /* ===== RESALTADO DE FOCO MUY VISIBLE ===== */
      /* Variables para el anillo de foco */
      :root {
        --a11y-focus-ring: #FF6600;
        --a11y-focus-glow: rgba(255, 102, 0, 0.6);
        --a11y-focus-bg: rgba(255, 102, 0, 0.15);
      }
      
      /* ===== ELEMENTOS BÁSICOS ===== */
      *:focus,
      *:focus-visible,
      button:focus,
      button:focus-visible,
      input:focus,
      input:focus-visible,
      select:focus,
      select:focus-visible,
      textarea:focus,
      textarea:focus-visible,
      a:focus,
      a:focus-visible,
      [tabindex]:focus,
      [tabindex]:focus-visible {
        outline: 4px solid var(--a11y-focus-ring) !important;
        outline-offset: 3px !important;
        box-shadow: 
          0 0 0 6px var(--a11y-focus-glow),
          0 0 20px 4px var(--a11y-focus-glow),
          inset 0 0 0 2px var(--a11y-focus-bg) !important;
        border-radius: 6px !important;
        transition: all 0.15s ease-out !important;
        position: relative !important;
        z-index: 1000 !important;
      }
      
      /* ===== STREAMLIT CHECKBOXES - ESTRUCTURA ESPECÍFICA ===== */
      [data-testid="stCheckbox"]:focus,
      [data-testid="stCheckbox"]:focus-visible,
      [data-testid="stCheckbox"] label:focus,
      [data-testid="stCheckbox"] label:focus-visible,
      [data-testid="stCheckbox"] input:focus,
      [data-testid="stCheckbox"] input:focus-visible,
      [data-testid="stCheckbox"] *:focus,
      [data-testid="stCheckbox"] *:focus-visible {
        outline: 4px solid var(--a11y-focus-ring) !important;
        outline-offset: 3px !important;
        box-shadow: 
          0 0 0 6px var(--a11y-focus-glow),
          0 0 20px 4px var(--a11y-focus-glow),
          inset 0 0 0 2px var(--a11y-focus-bg) !important;
        border-radius: 6px !important;
        position: relative !important;
        z-index: 1000 !important;
      }
      
      /* Contenedor del checkbox cuando tiene foco */
      [data-testid="stCheckbox"]:has(input:focus),
      [data-testid="stCheckbox"]:has(input:focus-visible) {
        outline: 4px solid var(--a11y-focus-ring) !important;
        outline-offset: 3px !important;
        box-shadow: 
          0 0 0 6px var(--a11y-focus-glow),
          0 0 20px 4px var(--a11y-focus-glow) !important;
        border-radius: 6px !important;
        padding: 2px !important;
      }
      
      /* ===== STREAMLIT RADIO BUTTONS ===== */
      [data-testid="stRadio"]:focus,
      [data-testid="stRadio"]:focus-visible,
      [data-testid="stRadio"] label:focus,
      [data-testid="stRadio"] label:focus-visible,
      [data-testid="stRadio"] input:focus,
      [data-testid="stRadio"] input:focus-visible,
      [data-testid="stRadio"] *:focus,
      [data-testid="stRadio"] *:focus-visible {
        outline: 4px solid var(--a11y-focus-ring) !important;
        outline-offset: 3px !important;
        box-shadow: 
          0 0 0 6px var(--a11y-focus-glow),
          0 0 20px 4px var(--a11y-focus-glow),
          inset 0 0 0 2px var(--a11y-focus-bg) !important;
        border-radius: 6px !important;
        position: relative !important;
        z-index: 1000 !important;
      }
      
      [data-testid="stRadio"]:has(input:focus),
      [data-testid="stRadio"]:has(input:focus-visible) {
        outline: 4px solid var(--a11y-focus-ring) !important;
        outline-offset: 3px !important;
        box-shadow: 
          0 0 0 6px var(--a11y-focus-glow),
          0 0 20px 4px var(--a11y-focus-glow) !important;
        border-radius: 6px !important;
        padding: 2px !important;
      }
      
      /* ===== STREAMLIT BUTTONS ===== */
      .stButton button:focus,
      .stButton button:focus-visible,
      [data-testid="stButton"] button:focus,
      [data-testid="stButton"] button:focus-visible {
        outline: 4px solid var(--a11y-focus-ring) !important;
        outline-offset: 3px !important;
        box-shadow: 
          0 0 0 6px var(--a11y-focus-glow),
          0 0 20px 4px var(--a11y-focus-glow),
          inset 0 0 0 2px var(--a11y-focus-bg) !important;
        border-radius: 6px !important;
        position: relative !important;
        z-index: 1000 !important;
      }
      
      /* ===== STREAMLIT SELECTBOX ===== */
      [data-testid="stSelectbox"]:focus,
      [data-testid="stSelectbox"]:focus-visible,
      [data-testid="stSelectbox"] *:focus,
      [data-testid="stSelectbox"] *:focus-visible,
      [data-baseweb="select"]:focus,
      [data-baseweb="select"]:focus-visible,
      [data-baseweb="select"] > div:focus,
      [data-baseweb="select"] > div:focus-visible {
        outline: 4px solid var(--a11y-focus-ring) !important;
        outline-offset: 3px !important;
        box-shadow: 
          0 0 0 6px var(--a11y-focus-glow),
          0 0 20px 4px var(--a11y-focus-glow),
          inset 0 0 0 2px var(--a11y-focus-bg) !important;
        border-radius: 6px !important;
        position: relative !important;
        z-index: 1000 !important;
      }
      
      /* ===== STREAMLIT TEXT INPUT ===== */
      [data-testid="stTextInput"] input:focus,
      [data-testid="stTextInput"] input:focus-visible,
      [data-baseweb="input"] input:focus,
      [data-baseweb="input"] input:focus-visible {
        outline: 4px solid var(--a11y-focus-ring) !important;
        outline-offset: 3px !important;
        box-shadow: 
          0 0 0 6px var(--a11y-focus-glow),
          0 0 20px 4px var(--a11y-focus-glow),
          inset 0 0 0 2px var(--a11y-focus-bg) !important;
        border-radius: 6px !important;
        position: relative !important;
        z-index: 1000 !important;
      }
      
      /* ===== STREAMLIT SLIDER ===== */
      [data-testid="stSlider"]:focus,
      [data-testid="stSlider"]:focus-visible,
      [data-testid="stSlider"] *:focus,
      [data-testid="stSlider"] *:focus-visible {
        outline: 4px solid var(--a11y-focus-ring) !important;
        outline-offset: 3px !important;
        box-shadow: 
          0 0 0 6px var(--a11y-focus-glow),
          0 0 20px 4px var(--a11y-focus-glow) !important;
        border-radius: 6px !important;
        position: relative !important;
        z-index: 1000 !important;
      }
      
      /* ===== STREAMLIT EXPANDER ===== */
      [data-testid="stExpander"] summary:focus,
      [data-testid="stExpander"] summary:focus-visible {
        outline: 4px solid var(--a11y-focus-ring) !important;
        outline-offset: 3px !important;
        box-shadow: 
          0 0 0 6px var(--a11y-focus-glow),
          0 0 20px 4px var(--a11y-focus-glow) !important;
        border-radius: 6px !important;
        position: relative !important;
        z-index: 1000 !important;
      }
      
      /* ===== ELEMENTOS CON ROLES ===== */
      [role="button"]:focus,
      [role="button"]:focus-visible,
      [role="checkbox"]:focus,
      [role="checkbox"]:focus-visible,
      [role="radio"]:focus,
      [role="radio"]:focus-visible,
      [role="tab"]:focus,
      [role="tab"]:focus-visible {
        outline: 4px solid var(--a11y-focus-ring) !important;
        outline-offset: 3px !important;
        box-shadow: 
          0 0 0 6px var(--a11y-focus-glow),
          0 0 20px 4px var(--a11y-focus-glow),
          inset 0 0 0 2px var(--a11y-focus-bg) !important;
        border-radius: 6px !important;
        position: relative !important;
        z-index: 1000 !important;
      }
      
      /* ===== SIDEBAR ===== */
      [data-testid="stSidebar"] *:focus,
      [data-testid="stSidebar"] *:focus-visible {
        outline: 4px solid var(--a11y-focus-ring) !important;
        outline-offset: 3px !important;
        box-shadow: 
          0 0 0 6px var(--a11y-focus-glow),
          0 0 20px 4px var(--a11y-focus-glow) !important;
        border-radius: 6px !important;
        position: relative !important;
        z-index: 1000 !important;
      }
      
      /* ===== ANIMACIÓN DE PULSO ===== */
      @keyframes focusPulse {
        0%, 100% { 
          box-shadow: 
            0 0 0 6px var(--a11y-focus-glow),
            0 0 20px 4px var(--a11y-focus-glow),
            inset 0 0 0 2px var(--a11y-focus-bg) !important;
        }
        50% { 
          box-shadow: 
            0 0 0 8px var(--a11y-focus-glow),
            0 0 30px 8px var(--a11y-focus-glow),
            inset 0 0 0 2px var(--a11y-focus-bg) !important;
        }
      }
      
      *:focus,
      *:focus-visible {
        animation: focusPulse 1.5s ease-in-out infinite !important;
      }
      
      /* ===== INDICADOR VISUAL ADICIONAL - FLECHA ===== */
      *:focus::before,
      *:focus-visible::before {
        content: '►' !important;
        position: absolute !important;
        left: -25px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        color: var(--a11y-focus-ring) !important;
        font-size: 16px !important;
        font-weight: bold !important;
        text-shadow: 0 0 10px var(--a11y-focus-glow) !important;
        z-index: 1001 !important;
        pointer-events: none !important;
      }
      
      /* Para checkboxes, la flecha debe estar en el contenedor */
      [data-testid="stCheckbox"]:has(input:focus)::before,
      [data-testid="stCheckbox"]:has(input:focus-visible)::before {
        content: '►' !important;
        position: absolute !important;
        left: -25px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        color: var(--a11y-focus-ring) !important;
        font-size: 16px !important;
        font-weight: bold !important;
        text-shadow: 0 0 10px var(--a11y-focus-glow) !important;
        z-index: 1001 !important;
        pointer-events: none !important;
      }
      
      /* ===== SCROLL AL ELEMENTO ENFOCADO ===== */
      *:focus,
      *:focus-visible {
        scroll-margin: 50px !important;
      }
    </style>
    """

# ===== SISTEMA TTS MEJORADO =====

class TTSService:
    """Servicio mejorado de Text-to-Speech con descripciones de componentes"""
    
    def __init__(self):
        self.voces_disponibles = {
            "Español (España)": "es-ES",
            "Español (México)": "es-MX", 
            "Español (Colombia)": "es-CO",
            "Inglés (US)": "en-US",
            "Inglés (UK)": "en-GB"
        }
    
    def describir_grafico(self, tipo_grafico: str, titulo: str = "", datos: dict = None) -> str:
        """Genera descripción textual de un gráfico"""
        descripcion = f"Gráfico de tipo {tipo_grafico}. "
        if titulo:
            descripcion += f"Título: {titulo}. "
        if datos:
            if "valor_maximo" in datos:
                descripcion += f"Valor máximo: {datos['valor_maximo']}. "
            if "valor_minimo" in datos:
                descripcion += f"Valor mínimo: {datos['valor_minimo']}. "
            if "promedio" in datos:
                descripcion += f"Promedio: {datos['promedio']}. "
            if "total_elementos" in datos:
                descripcion += f"Total de elementos: {datos['total_elementos']}. "
        return descripcion
    
    def describir_boton(self, texto_boton: str, accion: str = "") -> str:
        """Genera descripción de un botón"""
        descripcion = f"Botón: {texto_boton}. "
        if accion:
            descripcion += f"Acción: {accion}. "
        return descripcion
    
    def describir_menu_desplegable(self, etiqueta: str, opciones: list, seleccionado: str = "") -> str:
        """Genera descripción de un menú desplegable"""
        descripcion = f"Menú desplegable: {etiqueta}. "
        descripcion += f"Opciones disponibles: {', '.join([str(o) for o in opciones[:5]])}. "
        if len(opciones) > 5:
            descripcion += f"Y {len(opciones) - 5} opciones más. "
        if seleccionado:
            descripcion += f"Opción seleccionada: {seleccionado}. "
        return descripcion
    
    def describir_tabla(self, num_filas: int, columnas: list, descripcion: str = "") -> str:
        """Genera descripción de una tabla"""
        texto = f"Tabla con {num_filas} filas y {len(columnas)} columnas. "
        if descripcion:
            texto += f"{descripcion}. "
        texto += f"Columnas: {', '.join([str(c) for c in columnas])}. "
        return texto
    
    def generar_audio(self, texto, velocidad=1.0, voz="es-ES"):
        """Genera audio usando Web Speech API (navegador) o fallback"""
        try:
            # Intentar usar Web Speech API del navegador (más eficiente)
            return self._tts_navegador(texto, velocidad, voz)
        except Exception as e:
            # Fallback a gTTS
            try:
                from gtts import gTTS
                import pygame
                
                texto_limpio = self._limpiar_texto_para_tts(texto)
                if not texto_limpio.strip():
                    return None
                    
                tts = gTTS(text=texto_limpio, lang=voz[:2], slow=False)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    tts.save(tmp_file.name)
                    temp_path = tmp_file.name
                
                pygame.mixer.init()
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                
                pygame.mixer.quit()
                os.unlink(temp_path)
                return True
            except Exception as e2:
                st.warning(f"Error en TTS: {e2}")
                return False
    
    def _tts_navegador(self, texto, velocidad, voz):
        """Usa Web Speech API del navegador - versión mejorada y más robusta"""
        texto_limpio = self._limpiar_texto_para_tts(texto)
        if not texto_limpio.strip():
            return False
        
        # Escapar texto de forma segura para JavaScript usando JSON
        import json
        texto_json = json.dumps(texto_limpio)
        
        # Crear un ID único para este TTS
        import time
        tts_id = f"tts_{int(time.time() * 1000)}"
        
        # JavaScript mejorado que maneja mejor los casos edge
        js_code = f"""
        <script>
        (function() {{
            const ttsId = '{tts_id}';
            
            // Verificar soporte de Web Speech API
            if (!('speechSynthesis' in window)) {{
                console.error('[TTS] Web Speech API no disponible');
                // Mostrar mensaje al usuario
                const msg = document.createElement('div');
                msg.style.cssText = 'position:fixed;top:20px;right:20px;background:#ff4444;color:white;padding:10px;border-radius:5px;z-index:99999;';
                msg.textContent = 'Tu navegador no soporta síntesis de voz. Prueba con Chrome, Edge o Safari.';
                document.body.appendChild(msg);
                setTimeout(() => msg.remove(), 5000);
                return false;
            }}
            
            const synth = window.speechSynthesis;
            
            // Función para hablar
            function ejecutarTTS() {{
                try {{
                    // Cancelar cualquier lectura anterior
                    synth.cancel();
                    
                    // Esperar un momento para asegurar que cancel() se procesó
                    setTimeout(function() {{
                        const texto = {texto_json};
                        const velocidad = {velocidad};
                        const vozLang = '{voz}';
                        
                        // Crear utterance
                        const utterance = new SpeechSynthesisUtterance(texto);
                        utterance.rate = Math.max(0.1, Math.min(10, velocidad));
                        utterance.lang = vozLang;
                        utterance.volume = 1.0;
                        utterance.pitch = 1.0;
                        
                        // Buscar voz apropiada
                        function seleccionarVoz() {{
                            const voices = synth.getVoices();
                            if (voices.length === 0) {{
                                console.warn('[TTS] No hay voces disponibles aún');
                                return;
                            }}
                            
                            // Buscar voz que coincida con el idioma
                            const langPrefix = vozLang.split('-')[0];
                            let voice = voices.find(v => v.lang === vozLang) ||
                                       voices.find(v => v.lang.startsWith(langPrefix + '-')) ||
                                       voices.find(v => v.lang.startsWith(langPrefix)) ||
                                       voices.find(v => v.default);
                            
                            if (voice) {{
                                utterance.voice = voice;
                                console.log('[TTS] Voz seleccionada:', voice.name, voice.lang);
                            }} else {{
                                console.warn('[TTS] No se encontró voz para', vozLang, ', usando default');
                            }}
                            
                            // Event listeners
                            utterance.onstart = function() {{
                                console.log('[TTS] Iniciado:', texto.substring(0, 50) + '...');
                            }};
                            
                            utterance.onend = function() {{
                                console.log('[TTS] Finalizado');
                            }};
                            
                            utterance.onerror = function(event) {{
                                console.error('[TTS] Error:', event.error, event);
                                if (event.error === 'not-allowed') {{
                                    alert('El navegador bloqueó la síntesis de voz. Por favor, permite el audio en la configuración del navegador.');
                                }}
                            }};
                            
                            // Hablar
                            try {{
                                synth.speak(utterance);
                                console.log('[TTS] Comando speak() ejecutado');
                            }} catch (err) {{
                                console.error('[TTS] Error al ejecutar speak():', err);
                            }}
                        }}
                        
                        // Si las voces ya están cargadas, usar directamente
                        if (synth.getVoices().length > 0) {{
                            seleccionarVoz();
                        }} else {{
                            // Esperar a que las voces se carguen
                            let voicesLoaded = false;
                            
                            function onVoicesChanged() {{
                                if (!voicesLoaded && synth.getVoices().length > 0) {{
                                    voicesLoaded = true;
                                    seleccionarVoz();
                                    synth.onvoiceschanged = null; // Limpiar listener
                                }}
                            }}
                            
                            synth.onvoiceschanged = onVoicesChanged;
                            
                            // Timeout de seguridad (algunos navegadores no disparan onvoiceschanged)
                            setTimeout(function() {{
                                if (!voicesLoaded) {{
                                    voicesLoaded = true;
                                    seleccionarVoz();
                                }}
                            }}, 1000);
                        }}
                    }}, 50); // Pequeño delay para asegurar que cancel() se procesó
                    
                    return true;
                }} catch (error) {{
                    console.error('[TTS] Error general:', error);
                    return false;
                }}
            }}
            
            // Ejecutar inmediatamente
            ejecutarTTS();
        }})();
        </script>
        """
        
        # Intentar usar st.components.v1.html primero (más confiable)
        try:
            from streamlit.components.v1 import html
            html(js_code, height=0, scrolling=False)
            return True
        except Exception:
            # Fallback a st.markdown
            try:
                st.markdown(js_code, unsafe_allow_html=True)
                return True
            except Exception as e:
                st.warning(f"Error al ejecutar TTS: {e}")
                return False
    
    def _limpiar_texto_para_tts(self, texto):
        """Limpia el texto para mejor síntesis de voz"""
        if texto is None:
            return ""
        texto = str(texto)
        import re
        texto = re.sub(r'[^\w\s\.\,\;\:\!\?\-]', '', texto)
        texto = re.sub(r'\s+', ' ', texto)
        return texto.strip()
    
    def leer_tabla(self, df, limite_filas=10):
        """Convierte una tabla DataFrame a texto legible"""
        if df is None or df.empty:
            return "Tabla vacía"
        
        texto = f"Tabla con {len(df)} filas y {len(df.columns)} columnas. "
        columnas = ", ".join([str(col) for col in df.columns])
        texto += f"Columnas: {columnas}. "
        
        filas_a_leer = min(limite_filas, len(df))
        texto += f"Mostrando primeras {filas_a_leer} filas: "
        
        for i in range(filas_a_leer):
            fila_texto = f"Fila {i+1}: "
            for col in df.columns:
                valor = df.iloc[i][col]
                fila_texto += f"{col}: {valor}, "
            texto += fila_texto + ". "
        
        return texto

# Instancia global del servicio TTS
_tts_service = TTSService()

def _inject_tts_hover():
    """Inyecta JavaScript para leer contenido cuando el cursor pasa por encima - para personas ciegas"""
    # Debug: Verificar que la función se está llamando
    import sys
    import time
    print(f"[DEBUG] _inject_tts_hover() llamada - TTS hover activo: {st.session_state.get('a11y_tts_hover', False)}", file=sys.stderr)
    
    velocidad = st.session_state.get("a11y_tts_velocidad", 1.0)
    voz = st.session_state.get("a11y_tts_voz", "es-ES")
    
    # Código JavaScript limpio y sin duplicación
    js_code = f"""
    <script>
    (function() {{
        'use strict';
        
        // TEST INMEDIATO: Verificar que el script se está ejecutando
        console.log('%c🧪 SCRIPT CARGADO - Esto debería aparecer SIEMPRE', 'color: orange; font-size: 18px; font-weight: bold; background: yellow; padding: 10px;');
        
        // Función para obtener el contexto correcto (documento principal o actual)
        function getMainContext() {{
            try {{
                if (window.parent && window.parent !== window && window.parent.document) {{
                    return {{
                        doc: window.parent.document,
                        win: window.parent,
                        isIframe: true
                    }};
                }}
            }} catch (e) {{
                console.warn('No se puede acceder a window.parent:', e);
            }}
            return {{
                doc: document,
                win: window,
                isIframe: false
            }};
        }}
        
        const ctx = getMainContext();
        const doc = ctx.doc;
        const win = ctx.win;
        
        console.log('%c🔊 TTS HOVER - INICIANDO', 'color: green; font-size: 16px; font-weight: bold;');
        console.log('Contexto:', ctx.isIframe ? 'iframe, usando window.parent' : 'documento principal');
        
        // Verificar soporte
        if (!win.speechSynthesis) {{
            console.error('❌ Speech Synthesis no disponible');
            return;
        }}
        
        // Usar variables globales en el contexto correcto
        if (!win.ttsHoverState) {{
            win.ttsHoverState = {{
                synth: win.speechSynthesis,
                lastElement: null,
                lastText: '',
                hoverTimeout: null,
                isSpeaking: false,
                eventCount: 0,
                rapidEventCount: 0,
                lastEventTime: 0,
                isPaused: false,
                pauseUntil: 0,
                sidebarIntroduced: false,
                sidebarLastVisible: false
            }};
        }}
        
        const state = win.ttsHoverState;
        const synth = state.synth;
        
        // Función para detectar si el elemento está en el sidebar
        function isInSidebar(element) {{
            const sidebar = element.closest('[data-testid="stSidebar"]');
            return sidebar !== null;
        }}
        
        // Función para detectar si se está desplegando un menú/expander
        function isMenuExpanding(element) {{
            // Detectar expanders de Streamlit
            const expander = element.closest('[data-testid="stExpander"]');
            if (expander) {{
                const summary = expander.querySelector('summary');
                if (summary && summary.getAttribute('aria-expanded') === 'true') {{
                    return true;
                }}
            }}
            return false;
        }}
        
        // Función SIMPLE para obtener texto
        function getText(element) {{
            if (!element) return null;
            
            const tag = element.tagName;
            
            // Detectar icono de desplegar/colapsar sidebar y leer descripción útil
            const ariaLabel = element.getAttribute('aria-label');
            const title = element.getAttribute('title');
            
            // Detectar botón del sidebar (Streamlit usa un botón específico)
            // Buscar en el elemento y sus padres
            let current = element;
            let foundSidebarButton = false;
            for (let i = 0; i < 5 && current; i++) {{
                // Verificar si es el botón del sidebar de Streamlit
                if (current.tagName === 'BUTTON') {{
                    const btnAriaLabel = current.getAttribute('aria-label');
                    const btnTitle = current.getAttribute('title');
                    const btnClass = current.className || '';
                    
                    // Detectar patrones comunes del botón del sidebar
                    if ((btnAriaLabel && (btnAriaLabel.includes('sidebar') || btnAriaLabel.includes('menu') || btnAriaLabel.includes('navegación'))) ||
                        (btnTitle && (btnTitle.includes('sidebar') || btnTitle.includes('menu') || btnTitle.includes('navegación'))) ||
                        (btnClass && (btnClass.includes('sidebar') || btnClass.includes('menu') || btnClass.includes('collapsible')))) {{
                        foundSidebarButton = true;
                        break;
                    }}
                }}
                current = current.parentElement;
            }}
            
            // Si es el botón del sidebar, leer descripción útil
            if (foundSidebarButton || (ariaLabel && (ariaLabel.includes('sidebar') || ariaLabel.includes('menu') || ariaLabel.includes('navegación'))) ||
                (title && (title.includes('sidebar') || title.includes('menu') || title.includes('navegación')))) {{
                return 'Icono para desplegar el menú lateral';
            }}
            
            // DETECTAR RADIO BUTTONS EN SIDEBAR - PRIORITARIO
            const isSidebarElement = isInSidebar(element);
            if (isSidebarElement) {{
                // Buscar radio buttons primero
                const radioContainer = element.closest('[data-testid="stRadio"]');
                if (radioContainer) {{
                    // Buscar el label más cercano o que contenga el elemento
                    let bestLabel = null;
                    
                    // Si el elemento es un label directamente
                    if (element.tagName === 'LABEL') {{
                        bestLabel = element;
                    }} else if (element.closest('label')) {{
                        bestLabel = element.closest('label');
                    }} else {{
                        // Buscar por posición: encontrar el label más cercano al cursor
                        const allLabels = radioContainer.querySelectorAll('label');
                        const elementRect = element.getBoundingClientRect();
                        const elementCenterX = elementRect.left + elementRect.width / 2;
                        const elementCenterY = elementRect.top + elementRect.height / 2;
                        
                        let minDistance = Infinity;
                        for (let label of allLabels) {{
                            const labelRect = label.getBoundingClientRect();
                            
                            // Verificar si el cursor está dentro del label (margen amplio)
                            if (elementCenterX >= labelRect.left - 100 && 
                                elementCenterX <= labelRect.right + 100 &&
                                elementCenterY >= labelRect.top - 100 && 
                                elementCenterY <= labelRect.bottom + 100) {{
                                bestLabel = label;
                                break;
                            }}
                            
                            // Calcular distancia al centro del label
                            const labelCenterX = labelRect.left + labelRect.width / 2;
                            const labelCenterY = labelRect.top + labelRect.height / 2;
                            const distance = Math.sqrt(
                                Math.pow(elementCenterX - labelCenterX, 2) + 
                                Math.pow(elementCenterY - labelCenterY, 2)
                            );
                            
                            if (distance < minDistance && distance < 300) {{
                                minDistance = distance;
                                bestLabel = label;
                            }}
                        }}
                    }}
                    
                    if (bestLabel) {{
                        // Obtener texto del label
                        let labelText = '';
                        
                        // Buscar en spans primero (más confiable)
                        const spans = bestLabel.querySelectorAll('span');
                        for (let span of spans) {{
                            const spanText = span.textContent ? span.textContent.trim() : '';
                            if (spanText && spanText.length > 2 && spanText.length < 200) {{
                                labelText = spanText;
                                break;
                            }}
                        }}
                        
                        // Si no hay en spans, usar textContent directo
                        if (!labelText || labelText.length === 0) {{
                            labelText = bestLabel.textContent ? bestLabel.textContent.trim() : '';
                            // Limpiar indicadores de radio button
                            labelText = labelText.replace(/^[•●○◯\s]+/g, '').trim();
                        }}
                        
                        if (labelText && labelText.length > 0 && labelText.length < 200) {{
                            const radioInput = bestLabel.querySelector('input[type="radio"]');
                            const isSelected = radioInput && radioInput.checked;
                            
                            // Limpiar emojis comunes pero mantener el texto
                            const cleanText = labelText.replace(/^[📊🎯📝📦🏠🔍]+/g, '').trim();
                            if (cleanText && cleanText.length > 0) {{
                                return cleanText + (isSelected ? ', seleccionada' : '');
                            }}
                        }}
                    }}
                }}
                
                // Si no es radio button, permitir que continúe el flujo normal
            }}
            
            // IGNORAR elementos SVG (iconos) que no sean botones
            if ((tag === 'SVG' || element.closest('svg')) && tag !== 'BUTTON') {{
                return null;
            }}
            
            // PERMITIR leer el panel de accesibilidad - el usuario quiere que se lea todo
            // Ya no ignoramos el panel de accesibilidad
            const text = element.textContent ? element.textContent.trim() : '';
            
            // Si el elemento tiene muchos hijos con texto, solo leer el texto directo del elemento
            // Esto evita leer contenedores grandes cuando el usuario pasa el cursor sobre texto específico
            const childElements = element.querySelectorAll('*');
            const hasManyTextChildren = Array.from(childElements).filter(function(child) {{
                const childText = child.textContent ? child.textContent.trim() : '';
                return childText && childText.length > 3;
            }}).length > 3;
            
            // Si tiene muchos hijos con texto, intentar obtener solo el texto directo
            if (hasManyTextChildren && text.length > 100) {{
                // Buscar el texto más cercano al elemento (no del contenedor completo)
                const directText = Array.from(element.childNodes).filter(function(node) {{
                    return node.nodeType === 3; // Text node
                }}).map(function(node) {{
                    return node.textContent ? node.textContent.trim() : '';
                }}).join(' ').trim();
                
                if (directText && directText.length >= 3 && directText.length <= 100) {{
                    return directText;
                }}
            }}
            
            // Títulos
            if (['H1','H2','H3','H4','H5','H6'].includes(tag)) {{
                return text ? 'Título: ' + text : null;
            }}
            
            // Botones - mejor detección
            if (tag === 'BUTTON' || element.getAttribute('role') === 'button') {{
                // Intentar obtener el texto del botón de forma más precisa
                const buttonText = text || element.getAttribute('aria-label') || element.getAttribute('title') || '';
                // Limpiar el texto (remover emojis y espacios extra)
                const cleanText = buttonText.replace(/[^\w\s]/g, ' ').replace(/\s+/g, ' ').trim();
                return cleanText || 'botón';
            }}
            
            // Enlaces
            if (tag === 'A') {{
                return text || 'enlace';
            }}
            
            // Inputs
            if (tag === 'INPUT') {{
                const closestDiv = element.closest('div');
                const labelEl = closestDiv ? closestDiv.querySelector('label') : null;
                const label = (labelEl && labelEl.textContent) ? labelEl.textContent.trim() : '';
                const value = element.value || '';
                return label + (value ? ': ' + value : '');
            }}
            
            // Checkboxes de Streamlit
            const checkbox = element.closest('[data-testid="stCheckbox"]');
            if (checkbox) {{
                const label = checkbox.textContent ? checkbox.textContent.trim() : '';
                const input = checkbox.querySelector('input');
                const checked = (input && input.checked) ? 'activada' : 'desactivada';
                return label ? 'Casilla ' + label + ', ' + checked : null;
            }}
            
            // Toggle/Switch de Streamlit
            const toggle = element.closest('[data-testid="stToggle"]');
            if (toggle) {{
                const label = toggle.textContent ? toggle.textContent.trim() : '';
                const input = toggle.querySelector('input[type="checkbox"]');
                const checked = (input && input.checked) ? 'activada' : 'desactivada';
                return label ? 'Interruptor ' + label + ', ' + checked : null;
            }}
            
            // Sliders de Streamlit
            const slider = element.closest('[data-testid="stSlider"]');
            if (slider) {{
                const label = slider.querySelector('label');
                const labelText = label ? label.textContent.trim() : '';
                const value = slider.querySelector('input[type="range"]');
                const valueText = value ? value.value : '';
                return labelText ? labelText + ', valor ' + valueText : null;
            }}
            
            // Botones de Streamlit (mejor detección)
            const stButton = element.closest('[data-testid="stButton"]');
            if (stButton) {{
                // Buscar el texto del botón de forma más precisa
                const button = stButton.querySelector('button');
                let buttonText = '';
                if (button) {{
                    buttonText = button.textContent ? button.textContent.trim() : '';
                    if (!buttonText) {{
                        buttonText = button.getAttribute('aria-label') || '';
                    }}
                }}
                if (!buttonText) {{
                    buttonText = stButton.textContent ? stButton.textContent.trim() : '';
                }}
                // Limpiar el texto
                buttonText = buttonText.replace(/[^\w\s]/g, ' ').replace(/\s+/g, ' ').trim();
                return buttonText ? 'Botón ' + buttonText : null;
            }}
            
            // Radio buttons de Streamlit - MEJORADO: detectar labels individuales
            const radio = element.closest('[data-testid="stRadio"]');
            if (radio) {{
                // Si el elemento es un label individual dentro del radio button, leer solo ese
                if (element.tagName === 'LABEL' || element.closest('label')) {{
                    const labelEl = element.tagName === 'LABEL' ? element : element.closest('label');
                    const labelText = labelEl ? (labelEl.textContent ? labelEl.textContent.trim() : '') : '';
                    if (labelText && labelText.length > 0 && labelText.length < 200) {{
                        const radioInput = labelEl ? labelEl.querySelector('input[type="radio"]') : null;
                        const isSelected = radioInput && radioInput.checked;
                        // Limpiar el texto para quitar emojis y espacios extra
                        const cleanText = labelText.replace(/^[📊🎯📝📦]+/g, '').trim();
                        return cleanText ? cleanText + (isSelected ? ', seleccionada' : '') : null;
                    }}
                }}
                
                // Si no es un label específico, buscar el label del radio button específico sobre el que está el cursor
                const radioLabel = element.closest('label[data-baseweb="radio"]');
                if (radioLabel) {{
                    const labelText = radioLabel.textContent ? radioLabel.textContent.trim() : '';
                    if (labelText && labelText.length > 0 && labelText.length < 200) {{
                        const radioInput = radioLabel.querySelector('input[type="radio"]');
                        const isSelected = radioInput && radioInput.checked;
                        const cleanText = labelText.replace(/^[📊🎯📝📦]+/g, '').trim();
                        return cleanText ? cleanText + (isSelected ? ', seleccionada' : '') : null;
                    }}
                }}
                
                // Fallback: leer todo el contenedor pero solo si no hay muchos labels
                const allLabels = radio.querySelectorAll('label');
                if (allLabels.length === 1) {{
                    const label = allLabels[0].textContent ? allLabels[0].textContent.trim() : '';
                const selected = radio.querySelector('input[type="radio"]:checked');
                    const cleanText = label.replace(/^[📊🎯📝📦]+/g, '').trim();
                    return cleanText ? cleanText + (selected ? ', seleccionada' : '') : null;
                }}
                return null; // No leer si hay múltiples opciones
            }}
            
            // Expander de Streamlit (como "Información de usuario")
            const expander = element.closest('[data-testid="stExpander"]');
            if (expander) {{
                const summary = expander.querySelector('summary');
                if (summary && (element === summary || element.closest('summary'))) {{
                    const summaryText = summary.textContent ? summary.textContent.trim() : '';
                    return summaryText ? 'Sección ' + summaryText + ', expandir o colapsar' : null;
                }}
            }}
            
            // Botones dentro de expanders (menú de usuario)
            if (expander) {{
                const button = element.closest('button');
                if (button && button.textContent) {{
                    const buttonText = button.textContent.trim();
                    // Detectar botones específicos del menú de usuario
                    if (buttonText.includes('Configuración de Accesibilidad') || buttonText.includes('Accesibilidad')) {{
                        return 'Botón Configuración de Accesibilidad';
                    }}
                    if (buttonText.includes('Cerrar sesión') || buttonText.includes('Cerrar')) {{
                        return 'Botón Cerrar sesión';
                    }}
                    if (buttonText && buttonText.length > 0) {{
                        return 'Botón ' + buttonText;
                    }}
                }}
            }}
            
            // GRÁFICAS E IMÁGENES - SOLUCIÓN ROBUSTA Y COMPLETA
            if (tag === 'IMG') {{
                // Verificar si es una imagen de gráfico
                const esGrafico = (element.width && element.width > 200 && element.height && element.height > 150);
                
                if (!esGrafico) {{
                    return null;
                }}
                
                // Función para construir descripción completa
                function construirDescripcionGrafico(titulo) {{
                    let descripcion = 'Gráfico: ' + titulo;
                    const tituloLower = titulo.toLowerCase();
                    
                    if (tituloLower.includes('distribución') && tituloLower.includes('calificaciones')) {{
                        descripcion += ' Este es un histograma que muestra la distribución de calificaciones finales de los estudiantes. Las barras verticales representan la frecuencia de estudiantes en cada rango de calificaciones de 0 a 100 puntos. El gráfico incluye tres líneas de referencia importantes: una línea roja punteada en 70 puntos que marca el límite de aprobación, una línea verde punteada que indica la media o promedio de todas las calificaciones, y una línea naranja que muestra la mediana. Este gráfico te permite identificar si la mayoría de estudiantes están aprobados o reprobados, y ver la concentración de calificaciones en diferentes rangos.';
                    }} else if (tituloLower.includes('análisis') && tituloLower.includes('asistencia')) {{
                        descripcion += ' Este gráfico muestra el análisis de asistencia de los estudiantes. Puede mostrar dos tipos de visualización: promedios por materia o asistencia individual por grupo. Si muestra promedios por materia, verás barras horizontales ordenadas de mayor a menor asistencia, lo que te permite identificar qué materias tienen mejor o peor asistencia. Si muestra asistencia por grupo, verás barras horizontales para cada estudiante del grupo seleccionado, con colores diferentes para estudiantes con asistencia menor al 80 por ciento, lo que indica quiénes requieren atención.';
                    }} else if (tituloLower.includes('tendencia') && tituloLower.includes('unidades')) {{
                        descripcion += ' Este gráfico de barras verticales muestra la tendencia de calificaciones promedio por unidad académica. Verás tres barras que representan las unidades U1, U2 y U3 respectivamente. La altura de cada barra indica el promedio de calificaciones de esa unidad. Este gráfico te permite visualizar si hay una mejora o declive en el rendimiento a lo largo del semestre. Si las barras aumentan de izquierda a derecha, significa que el rendimiento mejoró. Si disminuyen, significa que empeoró. Cada barra tiene un número encima que indica el valor exacto del promedio.';
                    }} else if (tituloLower.includes('pareto') || tituloLower.includes('factores de riesgo') || 
                               (tituloLower.includes('diagrama') && tituloLower.includes('pareto'))) {{
                        descripcion += ' Este diagrama de Pareto muestra los factores de riesgo ordenados por frecuencia de mayor a menor. Las barras representan la frecuencia de cada factor, y la línea muestra el porcentaje acumulado. El objetivo es identificar los factores más críticos que representan el 80 por ciento de los problemas. Los factores a la izquierda son los más importantes y requieren atención prioritaria.';
                    }} else if (tituloLower.includes('dispersión') || tituloLower.includes('scatter')) {{
                        descripcion += ' Este gráfico de dispersión muestra la relación entre dos variables numéricas. Cada punto representa una observación, permitiendo identificar correlaciones, tendencias o patrones entre las variables analizadas. Si los puntos forman una línea, hay una correlación fuerte. Si están dispersos, no hay relación clara.';
                    }} else if (tituloLower.includes('histograma') || (tituloLower.includes('distribución') && tituloLower.includes('calificación'))) {{
                        descripcion += ' Este histograma muestra la distribución de frecuencias de los datos. Las barras representan intervalos de valores y su altura indica cuántas observaciones caen en cada intervalo. Permite visualizar la forma de la distribución, identificar valores atípicos y entender la variabilidad de los datos.';
                    }} else if (tituloLower.includes('control')) {{
                        descripcion += ' Este gráfico de control muestra la estabilidad de un proceso a lo largo del tiempo. La línea central representa la media, y las líneas punteadas superior e inferior son los límites de control. Los puntos fuera de estos límites indican variaciones fuera de control que requieren atención.';
                    }}
                    return descripcion;
                }}
                
                // PRIMERO: Verificar si ya tiene un aria-label válido (prioridad máxima)
                const ariaLabel = element.getAttribute('aria-label');
                if (ariaLabel && ariaLabel.length > 15 && ariaLabel !== 'Gráfico o imagen') {{
                    return ariaLabel;
                }}
                
                const imgRect = element.getBoundingClientRect();
                const imgCenter = imgRect.left + imgRect.width / 2;
                const imgTop = imgRect.top;
                
                // DESHABILITAR Análisis de Asistencia - no leer nada
                // Verificar por posición (lado izquierdo del dashboard)
                const pageWidth = window.innerWidth;
                if (imgCenter < pageWidth * 0.5) {{
                    // Podría ser asistencia, verificar si hay h3 de asistencia cerca
                    const allH3 = document.querySelectorAll('h3');
                    for (let h3 of allH3) {{
                        if (isInSidebar(h3)) continue;
                        const h3Text = (h3.textContent || '').toLowerCase();
                        if (h3Text.includes('análisis') && h3Text.includes('asistencia')) {{
                            const h3Rect = h3.getBoundingClientRect();
                            const h3Center = h3Rect.left + h3Rect.width / 2;
                            if (h3Center < pageWidth * 0.5 && Math.abs(h3Center - imgCenter) < 300) {{
                                return 'Gráfico o imagen'; // NO LEER ASISTENCIA
                            }}
                        }}
                    }}
                }}
                
                // BUSCAR h3 solo para gráficos que queremos que funcionen
                const allH3 = document.querySelectorAll('h3');
                let mejorH3 = null;
                let menorDistancia = Infinity;
                
                for (let h3 of allH3) {{
                    if (isInSidebar(h3)) continue;
                    
                    const h3Rect = h3.getBoundingClientRect();
                    const estiloH3 = window.getComputedStyle(h3);
                    
                    // Verificar que el h3 esté visible
                    if (estiloH3.display === 'none' || estiloH3.visibility === 'hidden' || 
                        h3Rect.width === 0 || h3Rect.height === 0) {{
                        continue;
                    }}
                    
                    // Solo h3 que estén arriba de la imagen
                    if (h3Rect.bottom >= imgTop) continue;
                    
                    let h3Text = h3.textContent ? h3.textContent.trim() : '';
                    h3Text = h3Text.replace(/^[📊🎯📈📝📦🔍]+/g, '').trim();
                    const h3TextLower = h3Text.toLowerCase();
                    
                    // Ignorar genéricos
                    if (h3TextLower === 'selecciona una herramienta de calidad') continue;
                    
                    // IGNORAR Análisis de Asistencia
                    if (h3TextLower.includes('análisis') && h3TextLower.includes('asistencia')) continue;
                    
                    // Calcular distancia
                    const distanciaVertical = imgTop - h3Rect.bottom;
                    const distanciaHorizontal = Math.abs((h3Rect.left + h3Rect.width / 2) - imgCenter);
                    
                    // Solo considerar h3 cercanos y en la misma columna
                    if (distanciaVertical > 800) continue;
                    if (distanciaHorizontal > 400) continue;
                    
                    const distanciaTotal = distanciaVertical + (distanciaHorizontal * 2);
                    if (distanciaTotal < menorDistancia) {{
                        menorDistancia = distanciaTotal;
                        mejorH3 = h3;
                    }}
                }}
                
                if (mejorH3) {{
                    let headerText = mejorH3.textContent ? mejorH3.textContent.trim() : '';
                    headerText = headerText.replace(/^[📊🎯📈📝📦🔍]+/g, '').trim();
                    headerText = headerText.replace(/\s+/g, ' ').trim();
                    
                    if (headerText && headerText.length > 0) {{
                        const headerLower = headerText.toLowerCase();
                        
                        // Solo procesar gráficos permitidos
                        if (headerLower.includes('distribución') && headerLower.includes('calificaciones')) {{
                            return construirDescripcionGrafico('Distribución de Calificaciones');
                        }}
                        if (headerLower.includes('tendencia') && headerLower.includes('unidades')) {{
                            return construirDescripcionGrafico('Tendencia por Unidades');
                        }}
                        if (headerLower.includes('pareto') || (headerLower.includes('factores') && headerLower.includes('riesgo'))) {{
                            return construirDescripcionGrafico('Diagrama de Pareto');
                        }}
                        if (headerLower.includes('dispersión') || headerLower.includes('scatter')) {{
                            return construirDescripcionGrafico('Diagrama de Dispersión');
                        }}
                        if (headerLower.includes('histograma')) {{
                            return construirDescripcionGrafico('Histograma');
                        }}
                        if (headerLower.includes('control')) {{
                            return construirDescripcionGrafico('Gráfico de Control');
                        }}
                        
                        // Para cualquier otro caso
                        return construirDescripcionGrafico(headerText);
                    }}
                }}
                
                return 'Gráfico o imagen';
            }}
            
            // CANVAS (gráficos interactivos o generados dinámicamente)
            if (tag === 'CANVAS') {{
                // Buscar título cercano
                const container = element.closest('div');
                if (container) {{
                    const title = container.querySelector('h1, h2, h3, h4, h5, h6');
                    if (title) {{
                        const titleText = title.textContent ? title.textContent.trim() : '';
                        if (titleText) {{
                            return 'Gráfico interactivo: ' + titleText;
                        }}
                    }}
                }}
                return 'Gráfico interactivo';
            }}
            
            // SVG (gráficos vectoriales)
            if (tag === 'SVG' || element.closest('svg')) {{
                // Buscar título en el SVG
                const svgTitle = element.querySelector('title');
                if (svgTitle) {{
                    const titleText = svgTitle.textContent ? svgTitle.textContent.trim() : '';
                    if (titleText) {{
                        return 'Gráfico vectorial: ' + titleText;
                    }}
                }}
                // Buscar título cercano
                const container = element.closest('div');
                if (container) {{
                    const title = container.querySelector('h1, h2, h3, h4, h5, h6');
                    if (title) {{
                        const titleText = title.textContent ? title.textContent.trim() : '';
                        if (titleText) {{
                            return 'Gráfico vectorial: ' + titleText;
                        }}
                    }}
                }}
                return 'Gráfico vectorial';
            }}
            
            // TABLAS - Detección mejorada
            if (tag === 'TABLE') {{
                const rows = element.querySelectorAll('tr').length;
                const cols = element.querySelectorAll('tr:first-child th, tr:first-child td').length;
                
                // Buscar título o caption de la tabla
                let tablaTitulo = '';
                const caption = element.querySelector('caption');
                if (caption) {{
                    tablaTitulo = caption.textContent ? caption.textContent.trim() : '';
                }}
                
                // Buscar título en elementos anteriores
                let prevSibling = element.previousElementSibling;
                for (let i = 0; i < 5 && prevSibling && !tablaTitulo; i++) {{
                    if (prevSibling.tagName && ['H1','H2','H3','H4','H5','H6'].includes(prevSibling.tagName)) {{
                        tablaTitulo = prevSibling.textContent ? prevSibling.textContent.trim() : '';
                    }} else if (prevSibling.querySelector) {{
                        const titleEl = prevSibling.querySelector('h1, h2, h3, h4, h5, h6');
                        if (titleEl) {{
                            tablaTitulo = titleEl.textContent ? titleEl.textContent.trim() : '';
                        }}
                    }}
                    prevSibling = prevSibling.previousElementSibling;
                }}
                
                let descripcion = 'Tabla';
                if (tablaTitulo && tablaTitulo.length > 0) {{
                    descripcion += ': ' + tablaTitulo;
                }}
                descripcion += ' con ' + rows + ' filas';
                if (cols > 0) {{
                    descripcion += ' y ' + cols + ' columnas';
                }}
                descripcion += '. Pasa el cursor sobre cada celda para leer su contenido.';
                
                return descripcion;
            }}
            
            // Celdas de tabla - Mejora para leer contenido completo
            if (tag === 'TD' || tag === 'TH') {{
                // Obtener texto de la celda
                let cellText = text || '';
                
                // Si es un encabezado (TH), indicarlo
                if (tag === 'TH') {{
                    if (cellText && cellText.length > 0) {{
                        return 'Encabezado de columna: ' + cellText;
                    }}
                }}
                
                // Para celdas normales, obtener también el encabezado de columna si está disponible
                if (tag === 'TD' && cellText && cellText.length > 0) {{
                    const row = element.parentElement;
                    if (row) {{
                        const headerRow = row.parentElement ? row.parentElement.querySelector('tr:first-child') : null;
                        if (headerRow) {{
                            const cellIndex = Array.from(row.children).indexOf(element);
                            if (cellIndex >= 0 && headerRow.children[cellIndex]) {{
                                const headerText = headerRow.children[cellIndex].textContent ? headerRow.children[cellIndex].textContent.trim() : '';
                                if (headerText && headerText.length > 0) {{
                                    return headerText + ': ' + cellText;
                                }}
                            }}
                        }}
                    }}
                }}
                
                return cellText || null;
            }}
            
            // Streamlit DataFrames (tablas generadas por st.dataframe) - Mejora para detectar mejor
            if (element.closest && element.closest('[data-testid="stDataFrame"]')) {{
                const tableContainer = element.closest('[data-testid="stDataFrame"]');
                if (tableContainer && (tag === 'DIV' || tag === 'TABLE' || tag === 'TD' || tag === 'TH')) {{
                    const table = tableContainer.querySelector('table');
                    if (table) {{
                        const rows = table.querySelectorAll('tbody tr, tr').length;
                        const headerRow = table.querySelector('thead tr, tr:first-child');
                        const cols = headerRow ? headerRow.querySelectorAll('th, td').length : 0;
                        
                        // Buscar título en múltiples lugares
                        let tablaTitulo = '';
                        
                        // Buscar caption
                        const caption = tableContainer.querySelector('caption');
                        if (caption) {{
                            tablaTitulo = caption.textContent ? caption.textContent.trim() : '';
                        }}
                        
                        // Buscar en elementos anteriores
                        let prevSibling = tableContainer.previousElementSibling;
                        for (let i = 0; i < 8 && prevSibling && !tablaTitulo; i++) {{
                            if (prevSibling.tagName && ['H1','H2','H3','H4','H5','H6'].includes(prevSibling.tagName)) {{
                                tablaTitulo = prevSibling.textContent ? prevSibling.textContent.trim() : '';
                            }} else if (prevSibling.querySelector) {{
                                const titleEl = prevSibling.querySelector('h1, h2, h3, h4, h5, h6');
                                if (titleEl) {{
                                    tablaTitulo = titleEl.textContent ? titleEl.textContent.trim() : '';
                                }}
                                // Buscar también en captions
                                const prevCaption = prevSibling.querySelector('small, [class*="caption"]');
                                if (prevCaption && !tablaTitulo) {{
                                    tablaTitulo = prevCaption.textContent ? prevCaption.textContent.trim() : '';
                                }}
                            }}
                            prevSibling = prevSibling.previousElementSibling;
                        }}
                        
                        // Si no hay título, intentar identificar por contexto
                        if (!tablaTitulo) {{
                            const pageText = document.body.textContent || '';
                            if (pageText.includes('Alumnos y calificación final') || pageText.includes('Alumnos con calificación')) {{
                                tablaTitulo = 'Alumnos con calificación final';
                            }} else if (pageText.includes('Alumnos del grupo')) {{
                                tablaTitulo = 'Alumnos del grupo seleccionado';
                            }}
                        }}
                        
                        // Obtener nombres de columnas para descripción más detallada
                        let columnasNombres = [];
                        if (headerRow) {{
                            const headers = headerRow.querySelectorAll('th, td');
                            for (let h of headers) {{
                                const headerText = h.textContent ? h.textContent.trim() : '';
                                if (headerText && headerText.length > 0) {{
                                    columnasNombres.push(headerText);
                                }}
                            }}
                        }}
                        
                        let descripcion = 'Tabla de datos';
                        if (tablaTitulo && tablaTitulo.length > 0) {{
                            descripcion += ': ' + tablaTitulo;
                        }}
                        descripcion += '. Contiene ' + rows + ' filas';
                        if (cols > 0) {{
                            descripcion += ' y ' + cols + ' columnas';
                            if (columnasNombres.length > 0 && columnasNombres.length <= 6) {{
                                descripcion += ': ' + columnasNombres.join(', ');
                            }}
                        }}
                        descripcion += '. Pasa el cursor sobre cada celda para leer su contenido con el nombre de la columna.';
                        
                        return descripcion;
                    }}
                }}
            }}
            
            // Celdas dentro de Streamlit DataFrames
            if ((tag === 'TD' || tag === 'TH') && element.closest('[data-testid="stDataFrame"]')) {{
                const cellText = text || '';
                if (!cellText || cellText.length === 0) {{
                    return null;
                }}
                
                // Obtener el encabezado de columna
                const table = element.closest('table');
                if (table) {{
                    const row = element.parentElement;
                    if (row) {{
                        const headerRow = table.querySelector('thead tr, tr:first-child');
                        if (headerRow) {{
                            const cellIndex = Array.from(row.children).indexOf(element);
                            if (cellIndex >= 0 && headerRow.children[cellIndex]) {{
                                const headerText = headerRow.children[cellIndex].textContent ? headerRow.children[cellIndex].textContent.trim() : '';
                                if (headerText && headerText.length > 0) {{
                                    if (tag === 'TH') {{
                                        return 'Encabezado de columna: ' + headerText;
                                    }} else {{
                                        return headerText + ': ' + cellText;
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
                
                return cellText;
            }}
            
            // Cualquier texto (mínimo 3 caracteres, máximo 500)
            if (text && text.length >= 3 && text.length <= 500 && /[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ]/.test(text)) {{
                return text;
            }}
            
            return null;
        }}
        
        // Función SIMPLE para hablar
        function speak(text) {{
            if (!text || !text.trim()) {{
                console.log('⚠️ speak() llamado sin texto válido');
                return;
            }}
            
            const textToRead = text.trim();
            console.log('🔊 speak() llamado con texto:', textToRead.substring(0, 50));
            
            // Cancelar cualquier lectura anterior
            synth.cancel();
            state.isSpeaking = false;
            
            // Esperar un momento breve para que cancel() se procese
            setTimeout(function() {{
                if (!textToRead || textToRead.length === 0) {{
                    return;
                }}
                
                state.isSpeaking = true;
                
                const utterance = new SpeechSynthesisUtterance(textToRead);
                utterance.rate = {velocidad};
                utterance.lang = '{voz}';
                utterance.volume = 1.0;
                
                // Seleccionar voz
                const voices = synth.getVoices();
                if (voices.length > 0) {{
                    const langPrefix = '{voz}'.split('-')[0];
                    const voice = voices.find(function(v) {{ return v.lang === '{voz}'; }}) ||
                                 voices.find(function(v) {{ return v.lang.startsWith(langPrefix + '-'); }}) ||
                                 voices.find(function(v) {{ return v.lang.startsWith(langPrefix); }});
                    if (voice) utterance.voice = voice;
                }}
                
                utterance.onend = function() {{ 
                    state.isSpeaking = false; 
                    console.log('✅ Lectura completada');
                }};
                utterance.onerror = function(e) {{ 
                    state.isSpeaking = false; 
                    console.error('❌ Error en lectura:', e);
                }};
                
                synth.speak(utterance);
                console.log('🔊 Iniciando lectura de:', textToRead.substring(0, 50));
            }}, 100);
        }}
        
        // Handler SIMPLE de mouseover con LOGGING EXTENSIVO
        function onMouseOver(e) {{
            const now = Date.now();
            const element = e.target;
            
            // Detectar cuando el sidebar se despliega y leer introducción
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            const sidebarVisible = sidebar && sidebar.offsetWidth > 50; // Más de 50px de ancho = visible
            
            // Si el sidebar se acaba de hacer visible y no se ha leído la introducción
            if (sidebarVisible && !state.sidebarLastVisible && !state.sidebarIntroduced) {{
                // Cancelar cualquier lectura en curso para que no interfiera
                synth.cancel();
                state.isSpeaking = false;
                
                // Esperar un momento para que se estabilice y no haya interferencias
                setTimeout(function() {{
                    const introText = 'Has desplegado el menú de opciones. Aquí encontrarás las opciones de navegación, botones para actualizar datos y configuraciones de auto actualización. Pasa el cursor sobre cada elemento para escucharlo.';
                    console.log('%c📢 Introducción del sidebar:', 'color: purple; font-weight: bold;', introText);
                    speak(introText);
                    state.sidebarIntroduced = true;
                }}, 1000);
            }}
            
            // Si el sidebar se cierra, resetear el flag para que se lea la intro la próxima vez
            if (!sidebarVisible && state.sidebarLastVisible) {{
                state.sidebarIntroduced = false;
            }}
            
            state.sidebarLastVisible = sidebarVisible;
            
            // IGNORAR COMPLETAMENTE el sidebar cuando se está desplegando
            if (isInSidebar(element)) {{
                // Detectar eventos rápidos en el sidebar (indica despliegue)
                if (now - state.lastEventTime < 100) {{
                    state.rapidEventCount++;
                }} else {{
                    state.rapidEventCount = 0;
                }}
                state.lastEventTime = now;
                
                // Si hay eventos rápidos en el sidebar, ignorar completamente
                if (state.rapidEventCount > 3) {{
                    state.isPaused = true;
                    state.pauseUntil = now + 2000; // Pausar por 2 segundos (reducido para que se lea la intro)
                    if (state.hoverTimeout) clearTimeout(state.hoverTimeout);
                    console.log('⏸️ Ignorando sidebar: se está desplegando');
                    return;
                }}
                
                // Si estamos en pausa por el sidebar, ignorar todos los eventos del sidebar
                if (state.isPaused && now < state.pauseUntil) {{
                    return; // Ignorar completamente
                }}
                
                // Si la pausa terminó, reactivar pero con delay más largo para sidebar
                if (state.isPaused && now >= state.pauseUntil) {{
                    state.isPaused = false;
                    state.rapidEventCount = 0;
                    console.log('▶️ Reanudando lectura (sidebar estabilizado)');
                }}
            }} else {{
                // Si no es sidebar, resetear contador de eventos rápidos
                state.rapidEventCount = 0;
            }}
            
            // Detectar si el elemento es parte de un expander que se está desplegando
            if (isMenuExpanding(element)) {{
                state.isPaused = true;
                state.pauseUntil = now + 2000; // Pausar por 2 segundos
                if (state.hoverTimeout) clearTimeout(state.hoverTimeout);
                console.log('⏸️ Pausando lectura: expander detectado');
                return;
            }}
            
            // Si estamos en pausa general, ignorar
            if (state.isPaused && now < state.pauseUntil) {{
                return;
            }}
            
            state.eventCount++;
            // Log cada evento (solo los primeros 20 para no saturar)
            if (state.eventCount <= 20) {{
                console.log('%c🖱️ MOUSEOVER #' + state.eventCount, 'color: blue; font-weight: bold;', 
                           'Tag:', e.target.tagName, 
                           'Text:', (e.target.textContent || '').substring(0, 30));
            }}
            
            if (state.hoverTimeout) clearTimeout(state.hoverTimeout);
            
            const currentElement = e.target;
            const isSidebarElement = isInSidebar(currentElement);
            
            // Delay más largo para sidebar (800ms) para evitar leer cuando se despliega
            // Delay normal para otros elementos (300ms)
            const delay = isSidebarElement ? 800 : 300;
            
            state.hoverTimeout = setTimeout(function() {{
                const element = currentElement;
                
                // Doble verificación: si es sidebar y aún estamos en pausa, ignorar
                if (isInSidebar(element) && state.isPaused && Date.now() < state.pauseUntil) {{
                    return;
                }}
                
                // Si es el mismo elemento que el último procesado, no hacer nada
                if (element === state.lastElement) {{
                    if (state.eventCount <= 20) {{
                        console.log('⏭️ Elemento repetido, saltando');
                    }}
                    return;
                }}
                
                state.lastElement = element;
                
                // Intentar obtener texto del elemento
                let text = getText(element);
                
                if (state.eventCount <= 20) {{
                    console.log('🔍 Texto encontrado en elemento:', text ? text.substring(0, 50) : 'null');
                }}
                
                // Si no hay texto, intentar con el padre, pero con límite de longitud
                if (!text) {{
                    let parent = element.parentElement;
                    for (let i = 0; i < 3 && parent; i++) {{
                        const parentText = getText(parent);
                        // Solo usar texto del padre si es corto (menos de 100 caracteres)
                        // Esto evita leer contenedores grandes cuando el usuario pasa el cursor sobre texto específico
                        if (parentText && parentText.length < 100) {{
                            text = parentText;
                            if (state.eventCount <= 20) {{
                                console.log('🔍 Texto encontrado en padre:', text.substring(0, 50));
                            }}
                            break;
                        }}
                        parent = parent.parentElement;
                    }}
                }}
                
                // Si el texto es muy largo (más de 200 caracteres), probablemente es un contenedor
                // Intentar obtener solo el texto directo del elemento
                if (text && text.length > 200) {{
                    const directText = Array.from(element.childNodes).filter(function(node) {{
                        return node.nodeType === 3; // Text node
                    }}).map(function(node) {{
                        return node.textContent ? node.textContent.trim() : '';
                    }}).join(' ').trim();
                    
                    if (directText && directText.length >= 3 && directText.length <= 200) {{
                        text = directText;
                        if (state.eventCount <= 20) {{
                            console.log('🔍 Usando texto directo (evitando contenedor grande):', text.substring(0, 50));
                        }}
                    }}
                }}
                
                // Si encontramos texto y es diferente al anterior, leerlo
                if (text && text !== state.lastText) {{
                    // Cancelar lectura anterior antes de iniciar nueva
                    synth.cancel();
                    state.isSpeaking = false;
                    
                    state.lastText = text;
                    console.log('%c🔊 LEYENDO TEXTO:', 'color: green; font-size: 14px; font-weight: bold;', text.substring(0, 60));
                    speak(text);
                }} else if (!text && state.eventCount <= 20) {{
                    console.log('⚠️ No se encontró texto legible en este elemento');
                }}
            }}, delay);
        }}
        
        // TEST: Listener de prueba que SIEMPRE se ejecuta
        function testMouseOver(e) {{
            console.log('%c🧪 TEST EVENTO CAPTURADO', 'color: red; font-size: 12px;', 
                       'Tag:', e.target.tagName, 
                       'Class:', (e.target.className && typeof e.target.className === 'string') ? e.target.className.substring(0, 30) : (e.target.className ? String(e.target.className).substring(0, 30) : 'sin clase'));
        }}
        
        // Agregar listeners DIRECTAMENTE en el documento principal
        doc.addEventListener('mouseover', onMouseOver, true);
        doc.addEventListener('mouseover', testMouseOver, true);
        
        // También agregar en body cuando esté disponible
        if (doc.body) {{
            doc.body.addEventListener('mouseover', onMouseOver, true);
            doc.body.addEventListener('mouseover', testMouseOver, true);
            console.log('✅ Listeners agregados en doc.body');
        }} else {{
            // Esperar a que body esté disponible
            const bodyObserver = new MutationObserver(() => {{
                if (doc.body) {{
                    doc.body.addEventListener('mouseover', onMouseOver, true);
                    doc.body.addEventListener('mouseover', testMouseOver, true);
                    console.log('✅ Listeners agregados en doc.body (después de esperar)');
                    bodyObserver.disconnect();
                }}
            }});
            bodyObserver.observe(doc.documentElement, {{ childList: true, subtree: true }});
        }}
        
        // Re-agregar listeners después de que Streamlit actualice el DOM
        const streamlitObserver = new MutationObserver(() => {{
            // Re-agregar listeners periódicamente para asegurar que sigan activos
            setTimeout(() => {{
                doc.addEventListener('mouseover', onMouseOver, true);
                doc.addEventListener('mouseover', testMouseOver, true);
            }}, 100);
        }});
        streamlitObserver.observe(doc.body || doc.documentElement, {{ 
            childList: true, 
            subtree: true 
        }});
        
        console.log('%c✅ TTS HOVER ACTIVO - Pasa el cursor sobre elementos', 'color: green; font-size: 14px; font-weight: bold;');
        console.log('%c🧪 TEST: Deberías ver mensajes "TEST EVENTO CAPTURADO" en rojo cuando muevas el cursor', 'color: red; font-size: 12px; font-weight: bold;');
        
        // SCRIPT PARA ETIQUETAR GRÁFICAS AUTOMÁTICAMENTE
        function etiquetarGraficas() {{
            const allImages = doc.querySelectorAll('img');
            const allH3 = doc.querySelectorAll('h3');
            const pageText = doc.body.textContent || '';
            
            function construirDescripcion(titulo) {{
                let desc = 'Gráfico: ' + titulo;
                const tituloLower = titulo.toLowerCase();
                if (tituloLower.includes('distribución') && tituloLower.includes('calificaciones')) {{
                    desc += ' Este es un histograma que muestra la distribución de calificaciones finales de los estudiantes. Las barras verticales representan la frecuencia de estudiantes en cada rango de calificaciones de 0 a 100 puntos. El gráfico incluye tres líneas de referencia importantes: una línea roja punteada en 70 puntos que marca el límite de aprobación, una línea verde punteada que indica la media o promedio de todas las calificaciones, y una línea naranja que muestra la mediana. Este gráfico te permite identificar si la mayoría de estudiantes están aprobados o reprobados, y ver la concentración de calificaciones en diferentes rangos.';
                }} else if (tituloLower.includes('análisis') && tituloLower.includes('asistencia')) {{
                    desc += ' Este gráfico muestra el análisis de asistencia de los estudiantes. Puede mostrar dos tipos de visualización: promedios por materia o asistencia individual por grupo. Si muestra promedios por materia, verás barras horizontales ordenadas de mayor a menor asistencia, lo que te permite identificar qué materias tienen mejor o peor asistencia. Si muestra asistencia por grupo, verás barras horizontales para cada estudiante del grupo seleccionado, con colores diferentes para estudiantes con asistencia menor al 80 por ciento, lo que indica quiénes requieren atención.';
                }} else if (tituloLower.includes('tendencia') && tituloLower.includes('unidades')) {{
                    desc += ' Este gráfico de barras verticales muestra la tendencia de calificaciones promedio por unidad académica. Verás tres barras que representan las unidades U1, U2 y U3 respectivamente. La altura de cada barra indica el promedio de calificaciones de esa unidad. Este gráfico te permite visualizar si hay una mejora o declive en el rendimiento a lo largo del semestre. Si las barras aumentan de izquierda a derecha, significa que el rendimiento mejoró. Si disminuyen, significa que empeoró. Cada barra tiene un número encima que indica el valor exacto del promedio.';
                }} else if (tituloLower.includes('pareto') || tituloLower.includes('factores de riesgo') || 
                           (tituloLower.includes('diagrama') && tituloLower.includes('pareto'))) {{
                    desc += ' Este diagrama de Pareto muestra los factores de riesgo ordenados por frecuencia de mayor a menor. Las barras representan la frecuencia de cada factor, y la línea muestra el porcentaje acumulado. El objetivo es identificar los factores más críticos que representan el 80 por ciento de los problemas. Los factores a la izquierda son los más importantes y requieren atención prioritaria.';
                }} else if (tituloLower.includes('dispersión') || tituloLower.includes('scatter')) {{
                    desc += ' Este gráfico de dispersión muestra la relación entre dos variables numéricas. Cada punto representa una observación, permitiendo identificar correlaciones, tendencias o patrones entre las variables analizadas. Si los puntos forman una línea, hay una correlación fuerte. Si están dispersos, no hay relación clara.';
                }} else if (tituloLower.includes('histograma')) {{
                    desc += ' Este histograma muestra la distribución de frecuencias de los datos. Las barras representan intervalos de valores y su altura indica cuántas observaciones caen en cada intervalo. Permite visualizar la forma de la distribución, identificar valores atípicos y entender la variabilidad de los datos.';
                }} else if (tituloLower.includes('control')) {{
                    desc += ' Este gráfico de control muestra la estabilidad de un proceso a lo largo del tiempo. La línea central representa la media, y las líneas punteadas superior e inferior son los límites de control. Los puntos fuera de estos límites indican variaciones fuera de control que requieren atención.';
                }}
                return desc;
            }}
            
            // NUEVO MÉTODO: Identificar por elementos UI únicos (igual que en getText)
            for (let img of allImages) {{
                if (img.width > 200 && img.height > 150 && !img.closest('[data-testid="stSidebar"]')) {{
                    // Si ya tiene un aria-label válido, no sobrescribir
                    const existingLabel = img.getAttribute('aria-label');
                    if (existingLabel && existingLabel.length > 10 && existingLabel !== 'Gráfico o imagen') {{
                        continue;
                    }}
                    
                    // MISMA LÓGICA: Buscar h3 dentro del MISMO CONTENEDOR PADRE
                    const imgRect = img.getBoundingClientRect();
                    const imgTop = imgRect.top;
                    let mejorH3 = null;
                    
                    // Verificar que la imagen esté visible
                    const estiloImg = window.getComputedStyle(img);
                    if (estiloImg.display === 'none' || estiloImg.visibility === 'hidden' || 
                        imgRect.width === 0 || imgRect.height === 0) {{
                        continue; // Saltar imágenes ocultas
                    }}
                    
                    // Buscar en el contenedor padre y sus ancestros
                    let container = img.parentElement;
                    let nivel = 0;
                    const maxNiveles = 10;
                    
                    while (container && nivel < maxNiveles && container !== doc.body) {{
                        // Buscar h3 dentro de este contenedor
                        const h3sEnContenedor = container.querySelectorAll('h3');
                        
                        for (let h3 of h3sEnContenedor) {{
                            if (h3.closest('[data-testid="stSidebar"]')) continue;
                            
                            const h3Rect = h3.getBoundingClientRect();
                            const estiloH3 = window.getComputedStyle(h3);
                            
                            // Verificar que el h3 esté visible
                            if (estiloH3.display === 'none' || estiloH3.visibility === 'hidden' || 
                                h3Rect.width === 0 || h3Rect.height === 0) {{
                                continue;
                            }}
                            
                            // Verificar que esté arriba de la imagen
                            if (h3Rect.bottom >= imgTop) continue;
                            
                            let h3Text = h3.textContent ? h3.textContent.trim() : '';
                            h3Text = h3Text.replace(/^[📊🎯📈📝📦🔍]+/g, '').trim();
                            const h3TextLower = h3Text.toLowerCase();
                            
                            // Ignorar h3 genéricos
                            if (h3TextLower === 'selecciona una herramienta de calidad') continue;
                            
                            // IGNORAR Análisis de Asistencia
                            if (h3TextLower.includes('análisis') && h3TextLower.includes('asistencia')) continue;
                            
                            // Si encontramos un h3 válido en el contenedor, usarlo
                            if (h3Text && h3Text.length > 0) {{
                                mejorH3 = h3;
                                break;
                            }}
                        }}
                        
                        if (mejorH3) break;
                        
                        // También buscar en hermanos anteriores del contenedor
                        let sibling = container.previousElementSibling;
                        let hermanosRevisados = 0;
                        const maxHermanos = 3;
                        
                        while (sibling && hermanosRevisados < maxHermanos) {{
                            const h3sEnHermano = sibling.querySelectorAll('h3');
                            for (let h3 of h3sEnHermano) {{
                                if (h3.closest('[data-testid="stSidebar"]')) continue;
                                
                                const h3Rect = h3.getBoundingClientRect();
                                const estiloH3 = window.getComputedStyle(h3);
                                
                                if (estiloH3.display === 'none' || estiloH3.visibility === 'hidden' || 
                                    h3Rect.width === 0 || h3Rect.height === 0) {{
                                    continue;
                                }}
                                
                                let h3Text = h3.textContent ? h3.textContent.trim() : '';
                                h3Text = h3Text.replace(/^[📊🎯📈📝📦🔍]+/g, '').trim();
                                const h3TextLower = h3Text.toLowerCase();
                                
                                if (h3TextLower === 'selecciona una herramienta de calidad') continue;
                                
                                // IGNORAR Análisis de Asistencia
                                if (h3TextLower.includes('análisis') && h3TextLower.includes('asistencia')) continue;
                                
                                if (h3Text && h3Text.length > 0) {{
                                    mejorH3 = h3;
                                    break;
                                }}
                            }}
                            
                            if (mejorH3) break;
                            sibling = sibling.previousElementSibling;
                            hermanosRevisados++;
                        }}
                        
                        if (mejorH3) break;
                        
                        container = container.parentElement;
                        nivel++;
                    }}
                    
                    if (mejorH3) {{
                        let headerText = mejorH3.textContent ? mejorH3.textContent.trim() : '';
                        headerText = headerText.replace(/^[📊🎯📈📝📦🔍]+/g, '').trim();
                        headerText = headerText.replace(/\s+/g, ' ').trim();
                        
                        if (headerText && headerText.length > 0) {{
                            const headerLower = headerText.toLowerCase();
                            
                            // Identificar tipo de gráfico por el texto del h3
                            // IGNORAR Análisis de Asistencia - no etiquetar
                            if (headerLower.includes('distribución') && headerLower.includes('calificaciones')) {{
                                img.setAttribute('aria-label', construirDescripcion('Distribución de Calificaciones'));
                            }} else if (headerLower.includes('tendencia') && headerLower.includes('unidades')) {{
                                img.setAttribute('aria-label', construirDescripcion('Tendencia por Unidades'));
                            }} else if (headerLower.includes('pareto') || (headerLower.includes('factores') && headerLower.includes('riesgo'))) {{
                                img.setAttribute('aria-label', construirDescripcion('Diagrama de Pareto'));
                            }} else if (headerLower.includes('dispersión') || headerLower.includes('scatter')) {{
                                img.setAttribute('aria-label', construirDescripcion('Diagrama de Dispersión'));
                            }} else if (headerLower.includes('histograma')) {{
                                img.setAttribute('aria-label', construirDescripcion('Histograma'));
                            }} else if (headerLower.includes('control')) {{
                                img.setAttribute('aria-label', construirDescripcion('Gráfico de Control'));
                            }} else {{
                                // Para cualquier otro caso, usar el texto del h3 directamente
                                img.setAttribute('aria-label', construirDescripcion(headerText));
                            }}
                        }}
                    }}
                }}
            }}
        }}
        
        // Ejecutar inmediatamente y luego cada 2 segundos para capturar imágenes que se cargan después
        etiquetarGraficas();
        setInterval(etiquetarGraficas, 2000);
    }})();
    </script>
    """
    
    # Intentar múltiples métodos de inyección
    injected = False
    
    # Método 1: st.components.v1.html (puede crear iframe, pero el script accede al padre)
    try:
        from streamlit.components.v1 import html as st_html
        st_html(js_code, height=0, scrolling=False)
        print("[DEBUG] Script inyectado usando st.components.v1.html", file=sys.stderr)
        injected = True
    except Exception as e:
        print(f"[DEBUG] st.components.v1.html falló: {e}", file=sys.stderr)
    
    # Método 2: st.markdown (inyección directa, pero puede no ejecutar scripts)
    if not injected:
        try:
            _inject(js_code)
            print("[DEBUG] Script inyectado usando _inject (st.markdown)", file=sys.stderr)
            injected = True
        except Exception as e:
            print(f"[DEBUG] _inject falló: {e}", file=sys.stderr)
    
    if not injected:
        st.warning("⚠️ No se pudo inyectar el script de TTS hover. Por favor, recarga la página.")
        print("[DEBUG] ERROR: No se pudo inyectar el script usando ningún método", file=sys.stderr)

# ===== APLICAR ESTILOS =====

def aplicar_accesibilidad():
    """Aplica todos los estilos de accesibilidad según la configuración"""
    _init_state()
    
    # Cargar configuración del usuario si está logueado
    # Verificar si el usuario cambió para resetear la configuración
    user_id = usuario_id()
    if user_id:
        usuario_anterior = st.session_state.get("a11y_usuario_configurado")
        if usuario_anterior != user_id:
            # Usuario cambió, resetear configuración
            st.session_state["a11y_config_cargada"] = False
            st.session_state["a11y_ultimo_contenido"] = ""
        cargar_configuracion_usuario()
    # Si no hay usuario, igual aplicar los estilos que estén en session_state
    # Esto permite que la accesibilidad funcione en el login
    
    # Aplicar estilos base
    _inject(_css_base(st.session_state.get("a11y_texto", 100)))
    
    # Aplicar tamaño de texto en login si estamos en login
    if st.session_state.get("a11y_texto_login", 100) != 100:
        _inject(_css_login(st.session_state.get("a11y_texto_login", 100)))
    
    # Aplicar tipografía para dislexia con espaciado
    if st.session_state.get("a11y_dyslexia", False):
        esp_letras = st.session_state.get("a11y_espaciado_letras", 0.02)
        esp_palabras = st.session_state.get("a11y_espaciado_palabras", 0.0)
        esp_lineas = st.session_state.get("a11y_espaciado_lineas", 1.6)
        _inject(_css_dyslexia(esp_letras, esp_palabras, esp_lineas))
    
    # Aplicar modo oscuro
    modo_oscuro = st.session_state.get("a11y_modo_oscuro", False)
    if modo_oscuro:
        _inject(_css_modo_oscuro())
    
    # Aplicar alto contraste - ahora funciona en ambos modos (claro y oscuro)
    if st.session_state.get("a11y_contraste", False):
        if modo_oscuro:
            _inject(_css_contraste_alto_oscuro())  # Versión para modo oscuro
        else:
            _inject(_css_contraste_alto())  # Versión para modo claro
    
    # Aplicar modo daltonismo
    modo_daltonismo = st.session_state.get("a11y_modo_daltonismo", "ninguno")
    if modo_daltonismo != "ninguno":
        _inject(_css_daltonismo(modo_daltonismo))
    
    # Aplicar modo concentración
    if st.session_state.get("a11y_modo_concentracion", False):
        _inject(_css_modo_enfoque())
    
    # Aplicar resaltar foco
    if st.session_state.get("a11y_resaltar_focus", False):
        _inject(_css_resaltar_focus())
    
    # Aplicar TTS con hover si está activo - INDEPENDIENTE de "Habilitar Texto a Voz"
    tts_hover_activo = st.session_state.get("a11y_tts_hover", False)
    if tts_hover_activo:
        _inject_tts_hover()

def leer_contenido(texto, es_tabla=False, df=None):
    """Función principal para leer contenido"""
    if not st.session_state.get("a11y_tts_activo", False):
        return
    
    try:
        st.session_state["a11y_tts_leyendo"] = True
        
        if es_tabla and df is not None:
            texto_a_leer = _tts_service.leer_tabla(df)
        else:
            texto_a_leer = _tts_service._limpiar_texto_para_tts(texto)
        
        if not texto_a_leer or not texto_a_leer.strip():
            st.session_state["a11y_tts_leyendo"] = False
            return
        
        # Solo leer si es contenido nuevo
        if texto_a_leer != st.session_state.get("a11y_ultimo_contenido", ""):
            velocidad = st.session_state.get("a11y_tts_velocidad", 1.0)
            voz = st.session_state.get("a11y_tts_voz", "es-ES")
            
            success = _tts_service.generar_audio(texto_a_leer, velocidad, voz)
            
            if success:
                st.session_state["a11y_ultimo_contenido"] = texto_a_leer
        
        st.session_state["a11y_tts_leyendo"] = False
        
    except Exception as e:
        st.session_state["a11y_tts_leyendo"] = False
        # No mostrar error si es solo un problema de TTS
        import traceback
        st.warning(f"Error en TTS: {str(e)}")

def detener_lectura():
    """Detiene la lectura actual de forma más robusta"""
    try:
        # JavaScript mejorado para detener TTS
        js_code = """
        <script>
        (function() {
            if (window.speechSynthesis) {
                // Cancelar todas las lecturas pendientes
                window.speechSynthesis.cancel();
                
                // Asegurarse de que se detiene completamente
                const synth = window.speechSynthesis;
                if (synth.speaking || synth.pending) {
                    synth.cancel();
                }
                
                // Limpiar cola de síntesis
                try {
                    synth.cancel();
                } catch (e) {
                    console.warn('[TTS] Error al cancelar:', e);
                }
            }
        })();
        </script>
        """
        # Usar st.components.v1.html para mayor confiabilidad (igual que _tts_navegador)
        try:
            from streamlit.components.v1 import html
            html(js_code, height=0, scrolling=False)
        except Exception:
            # Fallback a st.markdown
            st.markdown(js_code, unsafe_allow_html=True)
    except Exception as e:
        # No mostrar error al usuario, solo log
        pass
    
    # Actualizar estado
    st.session_state["a11y_tts_leyendo"] = False
    st.session_state["a11y_ultimo_contenido"] = ""  # Limpiar último contenido para permitir re-lectura

# ===== FUNCIONES DE DESCRIPCIÓN PARA COMPONENTES =====

def describir_grafico_tts(tipo_grafico: str, titulo: str = "", datos: dict = None):
    """Describe un gráfico usando TTS"""
    if st.session_state.get("a11y_tts_activo", False):
        descripcion = _tts_service.describir_grafico(tipo_grafico, titulo, datos)
        leer_contenido(descripcion)

def describir_boton_tts(texto_boton: str, accion: str = ""):
    """Describe un botón usando TTS"""
    if st.session_state.get("a11y_tts_activo", False):
        descripcion = _tts_service.describir_boton(texto_boton, accion)
        leer_contenido(descripcion)

def describir_menu_tts(etiqueta: str, opciones: list, seleccionado: str = ""):
    """Describe un menú desplegable usando TTS"""
    if st.session_state.get("a11y_tts_activo", False):
        descripcion = _tts_service.describir_menu_desplegable(etiqueta, opciones, seleccionado)
        leer_contenido(descripcion)

# ===== APLICAR ESTILOS =====

def aplicar_accesibilidad():
    """Aplica todos los estilos de accesibilidad según la configuración"""
    _init_state()
    
    # Cargar configuración del usuario si está logueado
    # Verificar si el usuario cambió para resetear la configuración
    user_id = usuario_id()
    if user_id:
        usuario_anterior = st.session_state.get("a11y_usuario_configurado")
        if usuario_anterior != user_id:
            # Usuario cambió, resetear configuración
            st.session_state["a11y_config_cargada"] = False
            st.session_state["a11y_ultimo_contenido"] = ""
        cargar_configuracion_usuario()
    # Si no hay usuario, igual aplicar los estilos que estén en session_state
    # Esto permite que la accesibilidad funcione en el login
    
    # Aplicar estilos base
    _inject(_css_base(st.session_state.get("a11y_texto", 100)))
    
    # Aplicar tamaño de texto en login si estamos en login
    if st.session_state.get("a11y_texto_login", 100) != 100:
        _inject(_css_login(st.session_state.get("a11y_texto_login", 100)))
    
    # Aplicar tipografía para dislexia con espaciado
    if st.session_state.get("a11y_dyslexia", False):
        esp_letras = st.session_state.get("a11y_espaciado_letras", 0.02)
        esp_palabras = st.session_state.get("a11y_espaciado_palabras", 0.0)
        esp_lineas = st.session_state.get("a11y_espaciado_lineas", 1.6)
        _inject(_css_dyslexia(esp_letras, esp_palabras, esp_lineas))
    
    # Aplicar modo oscuro
    modo_oscuro = st.session_state.get("a11y_modo_oscuro", False)
    if modo_oscuro:
        _inject(_css_modo_oscuro())
    
    # Aplicar alto contraste - ahora funciona en ambos modos (claro y oscuro)
    if st.session_state.get("a11y_contraste", False):
        if modo_oscuro:
            _inject(_css_contraste_alto_oscuro())  # Versión para modo oscuro
        else:
            _inject(_css_contraste_alto())  # Versión para modo claro
    
    # Aplicar modo daltonismo
    modo_daltonismo = st.session_state.get("a11y_modo_daltonismo", "ninguno")
    if modo_daltonismo != "ninguno":
        _inject(_css_daltonismo(modo_daltonismo))
    
    # Aplicar modo concentración
    if st.session_state.get("a11y_modo_concentracion", False):
        _inject(_css_modo_enfoque())
    
    # Aplicar resaltar foco
    if st.session_state.get("a11y_resaltar_focus", False):
        _inject(_css_resaltar_focus())
    
    # Aplicar TTS con hover si está activo - INDEPENDIENTE de "Habilitar Texto a Voz"
    tts_hover_activo = st.session_state.get("a11y_tts_hover", False)
    if tts_hover_activo:
        _inject_tts_hover()
    else:
        # Limpiar listeners si se desactiva
        _inject("""
        <script>
        if (window.ttsHoverCleanup) {
            window.ttsHoverCleanup();
            console.log('%c🔊 [TTS Hover] 🔴 SISTEMA DESACTIVADO', 'color: red; font-size: 16px; font-weight: bold;');
        }
        </script>
        """)

def leer_contenido(texto, es_tabla=False, df=None):
    """Función principal para leer contenido"""
    if not st.session_state.get("a11y_tts_activo", False):
        return
    
    try:
        st.session_state["a11y_tts_leyendo"] = True
        
        if es_tabla and df is not None:
            texto_a_leer = _tts_service.leer_tabla(df)
        else:
            texto_a_leer = _tts_service._limpiar_texto_para_tts(texto)
        
        if not texto_a_leer or not texto_a_leer.strip():
            st.session_state["a11y_tts_leyendo"] = False
            return
        
        # Solo leer si es contenido nuevo
        if texto_a_leer != st.session_state.get("a11y_ultimo_contenido", ""):
            velocidad = st.session_state.get("a11y_tts_velocidad", 1.0)
            voz = st.session_state.get("a11y_tts_voz", "es-ES")
            
            success = _tts_service.generar_audio(texto_a_leer, velocidad, voz)
            
            if success:
                st.session_state["a11y_ultimo_contenido"] = texto_a_leer
        
        st.session_state["a11y_tts_leyendo"] = False
        
    except Exception as e:
        st.session_state["a11y_tts_leyendo"] = False
        # No mostrar error si es solo un problema de TTS
        import traceback
        st.warning(f"Error en TTS: {str(e)}")

def detener_lectura():
    """Detiene la lectura actual de forma más robusta"""
    try:
        # JavaScript mejorado para detener TTS
        js_code = """
        <script>
        (function() {
            if (window.speechSynthesis) {
                // Cancelar todas las lecturas pendientes
                window.speechSynthesis.cancel();
                
                // Asegurarse de que se detiene completamente
                const synth = window.speechSynthesis;
                if (synth.speaking || synth.pending) {
                    synth.cancel();
                }
                
                // Limpiar cola de síntesis
                try {
                    synth.cancel();
                } catch (e) {
                    console.warn('[TTS] Error al cancelar:', e);
                }
            }
        })();
        </script>
        """
        # Usar st.components.v1.html para mayor confiabilidad (igual que _tts_navegador)
        try:
            from streamlit.components.v1 import html
            html(js_code, height=0, scrolling=False)
        except Exception:
            # Fallback a st.markdown
            st.markdown(js_code, unsafe_allow_html=True)
    except Exception as e:
        # No mostrar error al usuario, solo log
        pass
    
    # Actualizar estado
    st.session_state["a11y_tts_leyendo"] = False
    st.session_state["a11y_ultimo_contenido"] = ""  # Limpiar último contenido para permitir re-lectura

# ===== FUNCIONES DE DESCRIPCIÓN PARA COMPONENTES =====

def describir_grafico_tts(tipo_grafico: str, titulo: str = "", datos: dict = None):
    """Describe un gráfico usando TTS"""
    if st.session_state.get("a11y_tts_activo", False):
        descripcion = _tts_service.describir_grafico(tipo_grafico, titulo, datos)
        leer_contenido(descripcion)

def describir_boton_tts(texto_boton: str, accion: str = ""):
    """Describe un botón usando TTS"""
    if st.session_state.get("a11y_tts_activo", False):
        descripcion = _tts_service.describir_boton(texto_boton, accion)
        leer_contenido(descripcion)

def describir_menu_tts(etiqueta: str, opciones: list, seleccionado: str = ""):
    """Describe un menú desplegable usando TTS"""
    if st.session_state.get("a11y_tts_activo", False):
        descripcion = _tts_service.describir_menu_desplegable(etiqueta, opciones, seleccionado)
        leer_contenido(descripcion)

# ===== APLICAR ESTILOS =====

def aplicar_accesibilidad():
    """Aplica todos los estilos de accesibilidad según la configuración"""
    _init_state()
    
    # Cargar configuración del usuario si está logueado
    # Verificar si el usuario cambió para resetear la configuración
    user_id = usuario_id()
    if user_id:
        usuario_anterior = st.session_state.get("a11y_usuario_configurado")
        if usuario_anterior != user_id:
            # Usuario cambió, resetear configuración
            st.session_state["a11y_config_cargada"] = False
            st.session_state["a11y_ultimo_contenido"] = ""
        cargar_configuracion_usuario()
    # Si no hay usuario, igual aplicar los estilos que estén en session_state
    # Esto permite que la accesibilidad funcione en el login
    
    # Aplicar estilos base
    _inject(_css_base(st.session_state.get("a11y_texto", 100)))
    
    # Aplicar tamaño de texto en login si estamos en login
    if st.session_state.get("a11y_texto_login", 100) != 100:
        _inject(_css_login(st.session_state.get("a11y_texto_login", 100)))
    
    # Aplicar tipografía para dislexia con espaciado
    if st.session_state.get("a11y_dyslexia", False):
        esp_letras = st.session_state.get("a11y_espaciado_letras", 0.02)
        esp_palabras = st.session_state.get("a11y_espaciado_palabras", 0.0)
        esp_lineas = st.session_state.get("a11y_espaciado_lineas", 1.6)
        _inject(_css_dyslexia(esp_letras, esp_palabras, esp_lineas))
    
    # Aplicar modo oscuro
    modo_oscuro = st.session_state.get("a11y_modo_oscuro", False)
    if modo_oscuro:
        _inject(_css_modo_oscuro())
    
    # Aplicar alto contraste - ahora funciona en ambos modos (claro y oscuro)
    if st.session_state.get("a11y_contraste", False):
        if modo_oscuro:
            _inject(_css_contraste_alto_oscuro())  # Versión para modo oscuro
        else:
            _inject(_css_contraste_alto())  # Versión para modo claro
    
    # Aplicar modo daltonismo
    modo_daltonismo = st.session_state.get("a11y_modo_daltonismo", "ninguno")
    if modo_daltonismo != "ninguno":
        _inject(_css_daltonismo(modo_daltonismo))
    
    # Aplicar modo concentración
    if st.session_state.get("a11y_modo_concentracion", False):
        _inject(_css_modo_enfoque())
    
    # Aplicar resaltar foco
    if st.session_state.get("a11y_resaltar_focus", False):
        _inject(_css_resaltar_focus())
    
    # Aplicar TTS con hover si está activo
    tts_hover_activo = st.session_state.get("a11y_tts_hover", False)
    if tts_hover_activo:
        # Debug: Verificar que se está ejecutando
        import sys
        print(f"[DEBUG] aplicar_accesibilidad() - TTS hover está activo, inyectando script...", file=sys.stderr)
        _inject_tts_hover()
    else:
        import sys
        print(f"[DEBUG] aplicar_accesibilidad() - TTS hover NO está activo (valor: {tts_hover_activo})", file=sys.stderr)

# ===== PANEL DE ACCESIBILIDAD =====

def _on_checkbox_change(key):
    """Callback para aplicar cambios instantáneamente cuando un checkbox cambia"""
    # Mapeo de keys especiales que no siguen el patrón estándar
    special_keys = {
        "a11y_resaltar_focus": "a11y_resaltar_cb"
    }
    # Obtener el valor del widget
    widget_key = special_keys.get(key, f"{key}_cb")
    if widget_key in st.session_state:
        st.session_state[key] = st.session_state[widget_key]
        # Guardar cambio
        _guardar_si_cambio(key, st.session_state[key], f"{key}_previo")

def _mostrar_contenido_panel_accesibilidad():
    """Muestra el contenido del panel de accesibilidad (sin expander)"""
    # Sección TTS
    st.markdown("**🔊 Texto a Voz (TTS)**")
    st.caption("💡 Nota: Algunos navegadores requieren interacción del usuario antes de permitir síntesis de voz. Si no escuchas nada, intenta hacer clic en cualquier parte de la página primero.")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        tts_activo = st.checkbox(
            "Habilitar Texto a Voz",
            value=st.session_state.get("a11y_tts_activo", False),
            key="a11y_tts_activo_cb",
            help="Activa las funciones de texto a voz. Podrás leer contenido haciendo clic en botones específicos, gráficos y tablas.",
            on_change=_on_checkbox_change,
            args=("a11y_tts_activo",)
        )
    
    with col2:
        if st.button("🔊 Probar", key="probar_tts_btn"):
            # Activar TTS temporalmente si no está activo para probar
            tts_activo_temp = st.session_state.get("a11y_tts_activo", False)
            st.session_state["a11y_tts_activo"] = True
            texto_prueba = "Síntesis de voz activada correctamente. Esta es una prueba del sistema de texto a voz."
            leer_contenido(texto_prueba)
            st.session_state["a11y_tts_activo"] = tts_activo_temp
            st.rerun()
    
    with col3:
        if st.button("📖 Leer todo", key="leer_todo_btn"):
            # Activar TTS temporalmente si no está activo
            tts_activo_temp = st.session_state.get("a11y_tts_activo", False)
            st.session_state["a11y_tts_activo"] = True
            st.session_state["a11y_ultimo_contenido"] = ""
            # Leer todo el contenido de la página actual
            leer_todo_contenido_pagina()
            st.session_state["a11y_tts_activo"] = tts_activo_temp
            st.rerun()
    
    with col4:
        # Botón Detener siempre visible cuando TTS está activo
        if st.session_state.get("a11y_tts_activo", False):
            if st.button("⏹️ Detener", key="detener_tts_btn", help="Detiene la lectura actual de texto a voz"):
                detener_lectura()
                st.rerun()
    
    st.session_state["a11y_tts_activo"] = tts_activo
    # Guardar automáticamente si hay cambio
    _guardar_si_cambio("a11y_tts_activo", tts_activo, "a11y_tts_activo_previo")
    
    # Opción de TTS hover (leer al pasar el cursor) - INDEPENDIENTE de "Habilitar Texto a Voz"
    tts_hover_previo = st.session_state.get("a11y_tts_hover", False)
    tts_hover = st.checkbox(
        "🖱️ Leer al pasar el cursor",
        value=tts_hover_previo,
        key="a11y_tts_hover_cb",
        help="Lee automáticamente el contenido cuando pasas el cursor por encima. Ideal para personas con discapacidad visual. Funciona independientemente de otras opciones de TTS.",
        on_change=_on_checkbox_change,
        args=("a11y_tts_hover",)
    )
    st.session_state["a11y_tts_hover"] = tts_hover
    
    # Si se acaba de activar, leer mensaje informativo usando TTS del navegador directamente
    if tts_hover and not tts_hover_previo:
        mensaje_info = "Modo cursor activo. Pasa el cursor sobre cualquier elemento para escucharlo. En la esquina superior izquierda encontrarás un icono para desplegar el menú lateral con opciones de navegación y configuración."
        # Leer usando TTS del navegador directamente (no requiere TTS activo)
        velocidad_tts = st.session_state.get("a11y_tts_velocidad", 1.0)
        voz_tts = st.session_state.get("a11y_tts_voz", "es-ES")
        _tts_service._tts_navegador(mensaje_info, velocidad_tts, voz_tts)
    
    if tts_hover:
        st.info("🎯 **Modo cursor activo**: Pasa el cursor sobre cualquier elemento (textos, botones, gráficos, tablas) para escuchar su contenido. 💡 **Tip**: En la esquina superior izquierda hay un icono para desplegar el menú lateral.")
    
    if tts_activo:
        col3, col4 = st.columns(2)
        with col3:
            velocidad_actual = st.slider(
                "Velocidad",
                min_value=0.5,
                max_value=2.0,
                value=float(st.session_state.get("a11y_tts_velocidad", 1.0)),
                step=0.1,
                key="a11y_tts_velocidad_slider"
            )
            st.session_state["a11y_tts_velocidad"] = velocidad_actual
            _guardar_si_cambio("a11y_tts_velocidad", velocidad_actual, "a11y_tts_velocidad_previo")
        
        with col4:
            voz_seleccionada = st.selectbox(
                "Voz/Idioma",
                options=list(_tts_service.voces_disponibles.keys()),
                index=list(_tts_service.voces_disponibles.values()).index(
                    st.session_state.get("a11y_tts_voz", "es-ES")
                ) if st.session_state.get("a11y_tts_voz", "es-ES") in _tts_service.voces_disponibles.values() else 0,
                key="a11y_tts_voz_select",
                help="Selecciona el idioma y variante de la voz. La disponibilidad depende de tu navegador."
            )
            voz_actual = _tts_service.voces_disponibles[voz_seleccionada]
            st.session_state["a11y_tts_voz"] = voz_actual
            _guardar_si_cambio("a11y_tts_voz", voz_actual, "a11y_tts_voz_previo")
            
            # Mostrar nota sobre idiomas
            if voz_actual != "es-ES":
                st.caption(f"📌 Idioma seleccionado: {voz_seleccionada}. Si no funciona, verifica que tu navegador tenga voces instaladas para este idioma.")
    
    st.divider()
    st.markdown("**🎨 Ajustes Visuales**")
    
    # Modo oscuro/claro - con callback para aplicación instantánea
    modo_oscuro = st.checkbox(
        "🌙 Modo oscuro",
        value=st.session_state.get("a11y_modo_oscuro", False),
        key="a11y_modo_oscuro_cb",
        help="Cambia el color de textos y fondos a modo oscuro",
        on_change=_on_checkbox_change,
        args=("a11y_modo_oscuro",)
    )
    st.session_state["a11y_modo_oscuro"] = modo_oscuro
    _guardar_si_cambio("a11y_modo_oscuro", modo_oscuro, "a11y_modo_oscuro_previo")
    
    # Alto contraste - ahora disponible en ambos modos (claro y oscuro)
    contraste_label = "⚡ Alto contraste (modo oscuro)" if modo_oscuro else "⚡ Alto contraste (modo claro)"
    contraste_help = "Aumenta el contraste con colores brillantes sobre fondo negro" if modo_oscuro else "Aumenta el contraste con bordes más marcados"
    alto_contraste = st.checkbox(
        contraste_label,
        value=st.session_state.get("a11y_contraste", False),
        key="a11y_contraste_cb",
        help=contraste_help,
        on_change=_on_checkbox_change,
        args=("a11y_contraste",)
    )
    st.session_state["a11y_contraste"] = alto_contraste
    _guardar_si_cambio("a11y_contraste", alto_contraste, "a11y_contraste_previo")
    
    # Modo daltonismo - con nombres descriptivos
    opciones_daltonismo = {
        "ninguno": "Sin ajuste",
        "protanopia": "Protanopia (dificultad con rojos)",
        "deuteranopia": "Deuteranopia (dificultad con verdes)",
        "tritanopia": "Tritanopia (dificultad con azules)"
    }
    opciones_keys = list(opciones_daltonismo.keys())
    opciones_labels = list(opciones_daltonismo.values())
    
    modo_daltonismo_label = st.selectbox(
        "🎨 Modo para daltonismo",
        options=opciones_labels,
        index=opciones_keys.index(st.session_state.get("a11y_modo_daltonismo", "ninguno")),
        key="a11y_modo_daltonismo_select",
        help="Ajusta los colores de la interfaz para mejorar la visibilidad según el tipo de daltonismo"
    )
    # Convertir label a key
    modo_daltonismo = opciones_keys[opciones_labels.index(modo_daltonismo_label)]
    st.session_state["a11y_modo_daltonismo"] = modo_daltonismo
    _guardar_si_cambio("a11y_modo_daltonismo", modo_daltonismo, "a11y_modo_daltonismo_previo")
    
    st.divider()
    st.markdown("**📝 Tipografía y Espaciado**")
    
    # Tipografía para dislexia - con callback
    fuente_dislexia = st.checkbox(
        "📖 Tipografía para dislexia",
        value=st.session_state.get("a11y_dyslexia", False),
        key="a11y_dyslexia_cb",
        on_change=_on_checkbox_change,
        args=("a11y_dyslexia",)
    )
    st.session_state["a11y_dyslexia"] = fuente_dislexia
    _guardar_si_cambio("a11y_dyslexia", fuente_dislexia, "a11y_dyslexia_previo")
    
    if fuente_dislexia:
        st.markdown("**Ajustes de espaciado:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            esp_letras = st.slider(
                "Espaciado entre letras",
                min_value=0.0,
                max_value=0.1,
                value=float(st.session_state.get("a11y_espaciado_letras", 0.02)),
                step=0.01,
                key="a11y_esp_letras_slider"
            )
            st.session_state["a11y_espaciado_letras"] = esp_letras
            _guardar_si_cambio("a11y_espaciado_letras", esp_letras, "a11y_espaciado_letras_previo")
        with col2:
            esp_palabras = st.slider(
                "Espaciado entre palabras",
                min_value=0.0,
                max_value=0.2,
                value=float(st.session_state.get("a11y_espaciado_palabras", 0.0)),
                step=0.01,
                key="a11y_esp_palabras_slider"
            )
            st.session_state["a11y_espaciado_palabras"] = esp_palabras
            _guardar_si_cambio("a11y_espaciado_palabras", esp_palabras, "a11y_espaciado_palabras_previo")
        with col3:
            esp_lineas = st.slider(
                "Espaciado entre líneas",
                min_value=1.0,
                max_value=2.5,
                value=float(st.session_state.get("a11y_espaciado_lineas", 1.6)),
                step=0.1,
                key="a11y_esp_lineas_slider"
            )
            st.session_state["a11y_espaciado_lineas"] = esp_lineas
            _guardar_si_cambio("a11y_espaciado_lineas", esp_lineas, "a11y_espaciado_lineas_previo")
    
    # Tamaño de texto general
    texto_actual = st.slider(
        "Tamaño de texto %",
        min_value=90,
        max_value=150,
        step=2,
        value=int(st.session_state.get("a11y_texto", 100)),
        key="a11y_texto_slider",
    )
    st.session_state["a11y_texto"] = texto_actual
    _guardar_si_cambio("a11y_texto", texto_actual, "a11y_texto_previo")
    
    # Tamaño de texto en login
    texto_login_actual = st.slider(
        "Tamaño de texto en inicio de sesión %",
        min_value=100,
        max_value=150,
        step=5,
        value=int(st.session_state.get("a11y_texto_login", 100)),
        key="a11y_texto_login_slider",
    )
    st.session_state["a11y_texto_login"] = texto_login_actual
    _guardar_si_cambio("a11y_texto_login", texto_login_actual, "a11y_texto_login_previo")
    
    st.divider()
    st.markdown("**🎯 Modo Concentración**")
    
    # Modo concentración con icono - con callback
    modo_concentracion = st.checkbox(
        "🎯 Modo concentración",
        value=st.session_state.get("a11y_modo_concentracion", False),
        key="a11y_modo_concentracion_cb",
        help="Reduce distracciones enfocando el contenido principal",
        on_change=_on_checkbox_change,
        args=("a11y_modo_concentracion",)
    )
    st.session_state["a11y_modo_concentracion"] = modo_concentracion
    _guardar_si_cambio("a11y_modo_concentracion", modo_concentracion, "a11y_modo_concentracion_previo")
    
    # Opción de resaltar foco de teclado
    resaltar_focus = st.checkbox(
        "🔦 Resaltar foco de teclado",
        value=st.session_state.get("a11y_resaltar_focus", False),
        key="a11y_resaltar_cb",
        on_change=_on_checkbox_change,
        args=("a11y_resaltar_focus",),
        help="Resalta de forma muy visible el elemento que tiene el foco al navegar con Tab. Útil para navegación por teclado."
    )
    st.session_state["a11y_resaltar_focus"] = resaltar_focus
    _guardar_si_cambio("a11y_resaltar_focus", resaltar_focus, "a11y_resaltar_focus_previo")
    
    if resaltar_focus:
        st.info("🔦 **Foco visible activado**: Usa Tab para navegar y verás un resaltado naranja brillante en cada elemento.")
    
    # Botón para guardar configuración
    if usuario_id():
        if st.button("💾 Guardar configuración", key="guardar_config_btn", use_container_width=True):
            if guardar_configuracion_usuario():
                st.success("✅ Configuración guardada")
            else:
                st.error("❌ Error al guardar configuración")
    else:
        st.info("Inicia sesión para guardar tu configuración")

def panel_accesibilidad(en_sidebar: bool = True):
    """Panel completo de configuración de accesibilidad"""
    _init_state()
    
    # Cargar configuración del usuario al abrir el panel
    user_id = usuario_id()
    if user_id:
        usuario_anterior = st.session_state.get("a11y_usuario_configurado")
        if usuario_anterior != user_id:
            # Usuario cambió, resetear configuración
            st.session_state["a11y_config_cargada"] = False
            st.session_state["a11y_ultimo_contenido"] = ""
        cargar_configuracion_usuario()
    
    container = st.sidebar if en_sidebar else st
    
    with container.expander("🎧 Accesibilidad", expanded=False):
        _mostrar_contenido_panel_accesibilidad()
    
    aplicar_accesibilidad()

# ===== FUNCIONES HELPER =====

def leer_tabla_si_activo(df, descripcion=""):
    """Función conveniente para leer tablas si TTS está activo"""
    if st.session_state.get("a11y_tts_activo", False) and df is not None:
        texto_descripcion = f"{descripcion}. " if descripcion else ""
        leer_contenido(texto_descripcion, es_tabla=True, df=df)

def leer_texto_si_activo(texto):
    """Función conveniente para leer texto si TTS está activo"""
    if st.session_state.get("a11y_tts_activo", False) and texto:
        leer_contenido(texto, es_tabla=False)

def crear_boton_lectura(texto_a_leer, etiqueta_boton="🔊 Leer", key_suffix=""):
    """Crea un botón para leer texto específico bajo demanda"""
    if st.session_state.get("a11y_tts_activo", False):
        if st.button(etiqueta_boton, key=f"leer_btn_{key_suffix}"):
            leer_contenido(texto_a_leer)
            return True
    return False

def leer_dashboard_automatico():
    """Lee automáticamente el contenido principal del dashboard si TTS está activo"""
    if not st.session_state.get("a11y_tts_activo", False):
        return
    
    if (st.session_state.get("a11y_leyendo_dashboard", False) or 
        st.session_state.get("a11y_ultimo_contenido", "") == "dashboard_principal"):
        return
        
    try:
        st.session_state["a11y_leyendo_dashboard"] = True
        st.session_state["a11y_ultimo_contenido"] = "dashboard_principal"
        texto_dashboard = "Dashboard de Análisis Académico. Vista principal del sistema con métricas educativas."
        leer_contenido(texto_dashboard)
    except Exception as e:
        st.error(f"Error en lectura automática: {e}")
    finally:
        st.session_state["a11y_leyendo_dashboard"] = False

def leer_seccion_automatico(titulo, contenido=""):
    """Lee automáticamente una sección específica"""
    if not st.session_state.get("a11y_tts_activo", False):
        return
        
    contenido_id = f"seccion_{titulo}_{contenido}"
    if st.session_state.get("a11y_ultimo_contenido") == contenido_id:
        return
        
    texto_seccion = f"Sección: {titulo}. "
    if contenido:
        texto_seccion += f"{contenido}. "
        
    st.session_state["a11y_ultimo_contenido"] = contenido_id
    leer_contenido(texto_seccion)

def leer_metricas_automatico(metricas_dict):
    """Lee las métricas principales del dashboard"""
    if not st.session_state.get("a11y_tts_activo", False):
        return
        
    metricas_id = "metricas_" + "_".join([str(v) for v in metricas_dict.values()])
    if st.session_state.get("a11y_ultimo_contenido") == metricas_id:
        return
        
    texto_metricas = "Métricas del dashboard: "
    for clave, valor in metricas_dict.items():
        texto_metricas += f"{clave}: {valor}. "
        
    st.session_state["a11y_ultimo_contenido"] = metricas_id
    leer_contenido(texto_metricas)

def leer_elemento_seleccionado(elemento, contexto=""):
    """Lee un elemento específico que el usuario selecciona"""
    if not st.session_state.get("a11y_tts_activo", False):
        return
        
    texto = f"{contexto} {elemento}" if contexto else str(elemento)
    leer_contenido(texto)

def leer_todo_contenido_pagina():
    """Lee todo el contenido de la página actual incluyendo métricas, gráficas y sidebar"""
    if not st.session_state.get("a11y_tts_activo", False):
        return
    
    try:
        # Obtener la opción del menú actual - usar múltiples formas de detectar
        opcion_actual = st.session_state.get("opcion_actual_menu", "")
        if not opcion_actual:
            opcion_actual = st.session_state.get("nav_main", "")
        if not opcion_actual:
            opcion_actual = st.session_state.get("opcion_seleccionada", "")
        
        texto_completo = "Sistema de Análisis Educativo del Instituto Tecnológico de Tijuana. "
        
        # Información del sidebar
        user = st.session_state.get("user", {})
        if user:
            texto_completo += f"Usuario actual: {user.get('usuario', 'Desconocido')}. "
        
        # Información de navegación del sidebar
        texto_completo += "Panel de navegación lateral. Opciones disponibles: Dashboard Principal, Análisis de Calidad, Registro de Datos, Exportar Reportes. "
        texto_completo += "Botones disponibles: Actualizar Datos, Recargar servicios. "
        auto_on = st.session_state.get("auto_actualizar", True)
        auto_secs = st.session_state.get("auto_secs", 30)
        if auto_on:
            texto_completo += f"Auto actualización activada cada {auto_secs} segundos. "
        else:
            texto_completo += "Auto actualización desactivada. "
        texto_completo += f"Página actual: {opcion_actual}. "
        
        # Leer contenido específico según la opción
        contenido_especifico = ""
        if "Dashboard" in opcion_actual or "🏠" in opcion_actual or "Principal" in opcion_actual:
            contenido_especifico = leer_contenido_dashboard()
        elif "Análisis" in opcion_actual or "Calidad" in opcion_actual or "📈" in opcion_actual:
            contenido_especifico = leer_contenido_analisis_calidad()
        elif "Registro" in opcion_actual or "📝" in opcion_actual or "Datos" in opcion_actual:
            contenido_especifico = leer_contenido_registro_datos()
        elif "Exportar" in opcion_actual or "📦" in opcion_actual or "Reportes" in opcion_actual:
            contenido_especifico = leer_contenido_exportar_reportes()
        else:
            # Si no se detecta, intentar leer contenido genérico
            contenido_especifico = "Contenido de la página actual. "
        
        texto_completo += contenido_especifico
        
        # Leer el texto completo (resetear último contenido para forzar lectura)
        st.session_state["a11y_ultimo_contenido"] = ""
        leer_contenido(texto_completo)
        
    except Exception as e:
        # No mostrar error visible, solo log
        import traceback
        print(f"Error al leer contenido completo: {e}")
        print(traceback.format_exc())

def leer_contenido_dashboard():
    """Genera texto completo del dashboard para TTS"""
    try:
        from services.analytics import AnalyticsService
        from services.database import DatabaseService
        import numpy as np
        
        db = DatabaseService()
        analytics = AnalyticsService(db)
        metricas = analytics.calcular_metricas_principales()
        
        texto = "Dashboard de Análisis Académico. "
        texto += "Métricas principales del sistema. "
        texto += f"Total de estudiantes: {metricas.get('total_estudiantes', 0)}. "
        texto += f"Total de calificaciones registradas: {metricas.get('total_calificaciones', 0)}. "
        texto += f"Tasa de aprobación: {metricas.get('tasa_aprobacion', 0)} por ciento. "
        texto += f"Tasa de reprobación: {metricas.get('tasa_reprobacion', 0)} por ciento. "
        texto += f"Tasa de deserción: {metricas.get('tasa_desercion', 0)} por ciento. "
        
        # Información de gráficas de distribución
        texto += "Distribución de Calificaciones. Gráfico histograma mostrando la distribución de calificaciones finales de los estudiantes. "
        if not analytics.df_calificaciones.empty:
            dfc = analytics.df_calificaciones.copy()
            if "calificacion_final" in dfc.columns:
                vals = pd.to_numeric(dfc["calificacion_final"], errors="coerce").dropna()
                if len(vals) > 0:
                    media = float(vals.mean())
                    mediana = float(np.median(vals))
                    minimo = float(vals.min())
                    maximo = float(vals.max())
                    texto += f"Promedio de calificaciones: {media:.1f}. Mediana: {mediana:.1f}. "
                    texto += f"Rango de calificaciones: mínimo {minimo:.1f}, máximo {maximo:.1f}. "
                    texto += f"Límite de aprobación: 70 puntos. "
        
        # Información de gráficas de asistencia
        texto += "Análisis de Asistencia. Gráficos de barras horizontales mostrando asistencia promedio por materia o por grupo. "
        if not analytics.df_calificaciones.empty and "asistencia" in analytics.df_calificaciones.columns:
            asist_prom = analytics.df_calificaciones["asistencia"].mean()
            texto += f"Asistencia promedio general: {asist_prom:.1f} por ciento. "
        
        # Información de gráficas de tendencia
        texto += "Tendencia por Unidades. Gráfico de barras mostrando promedios de calificaciones por unidad académica: Unidad 1, Unidad 2, Unidad 3. "
        if not analytics.df_calificaciones.empty:
            unidades = ['u1', 'u2', 'u3']
            for u in unidades:
                if u in analytics.df_calificaciones.columns:
                    prom_u = analytics.df_calificaciones[u].mean()
                    texto += f"Promedio {u}: {prom_u:.1f}. "
        
        return texto
    except Exception as e:
        return f"Error al generar contenido del dashboard: {str(e)}. "

def leer_contenido_analisis_calidad():
    """Genera texto completo del análisis de calidad para TTS"""
    try:
        from services.analytics import AnalyticsService
        from services.database import DatabaseService
        
        db = DatabaseService()
        analytics = AnalyticsService(db)
        
        texto = "Análisis de Calidad. "
        texto += "Herramientas de análisis estadístico para evaluar el rendimiento académico. "
        
        # Información sobre datos disponibles
        if not analytics.df_calificaciones.empty:
            texto += f"Total de registros de calificaciones: {len(analytics.df_calificaciones)}. "
        
        if not analytics.df_materias.empty:
            texto += f"Total de materias disponibles: {len(analytics.df_materias)}. "
        
        if not analytics.df_estudiantes.empty:
            texto += f"Total de estudiantes: {len(analytics.df_estudiantes)}. "
        
        texto += "Gráficos disponibles: Histograma de distribución de calificaciones, Gráfico de control de calidad estadístico. "
        texto += "Filtros disponibles por materia, periodo y grupo. "
        
        return texto
    except Exception as e:
        return f"Error al generar contenido de análisis de calidad: {str(e)}. "

def leer_todo_contenido_analisis_calidad_completo(analytics):
    """Lee todo el contenido completo de Análisis de Calidad incluyendo herramienta seleccionada y gráficas"""
    if not st.session_state.get("a11y_tts_activo", False):
        return
    
    try:
        texto = "Análisis de Calidad. Herramientas de análisis estadístico. "
        
        # Obtener herramienta seleccionada
        herramienta = st.session_state.get("admin_tool_radio", "")
        if herramienta:
            texto += f"Herramienta seleccionada: {herramienta}. "
        
        # Leer contenido según herramienta
        if herramienta == "Diagrama de Pareto":
            try:
                pareto_data = analytics.generar_grafico_pareto()
                if pareto_data is not None and not pareto_data.empty:
                    texto += f"Diagrama de Pareto. Total de categorías: {len(pareto_data)}. "
                    texto += f"Total de factores: {pareto_data['frecuencia'].sum()}. "
                    factores_80 = pareto_data[pareto_data['porcentaje_acumulado'] <= 80]
                    texto += f"Categorías críticas: {len(factores_80)}. "
                    for idx, row in pareto_data.head(5).iterrows():
                        texto += f"{row['categoria']}: {row['frecuencia']} ocurrencias, {row['porcentaje_acumulado']:.1f} por ciento acumulado. "
            except:
                pass
        elif herramienta == "Gráfico de Control":
            try:
                datos_visual = analytics.obtener_datos_para_analisis_visual()
                if not datos_visual.empty:
                    variable = st.session_state.get("ctrl_var", "")
                    if variable:
                        datos_validos = datos_visual[variable].dropna()
                        if len(datos_validos) > 0:
                            media = datos_validos.mean()
                            desviacion = datos_validos.std()
                            lcs = media + 3 * desviacion
                            lci = media - 3 * desviacion
                            puntos_fuera = datos_validos[np.logical_or(datos_validos > lcs, datos_validos < lci)]
                            texto += f"Gráfico de Control para {variable}. Media: {media:.2f}. "
                            texto += f"Límite superior: {lcs:.2f}. Límite inferior: {lci:.2f}. "
                            texto += f"Observaciones: {len(datos_validos)}. Puntos fuera de control: {len(puntos_fuera)}. "
            except:
                pass
        
        # Leer contenido general
        texto += leer_contenido_analisis_calidad()
        
        st.session_state["a11y_ultimo_contenido"] = ""
        leer_contenido(texto)
    except Exception as e:
        import traceback
        print(f"Error al leer contenido completo de análisis de calidad: {e}")
        print(traceback.format_exc())

def leer_contenido_registro_datos():
    """Genera texto completo del registro de datos para TTS con todas las opciones de tabs"""
    try:
        from services.analytics import AnalyticsService
        from services.database import DatabaseService
        from services.rbac import es_docente
        
        db = DatabaseService()
        analytics = AnalyticsService(db)
        
        texto = "Registro de Datos. "
        texto += "Módulo para registrar y gestionar información académica. "
        
        # Información sobre datos disponibles
        if not analytics.df_estudiantes.empty:
            texto += f"Total de estudiantes registrados: {len(analytics.df_estudiantes)}. "
        
        if not analytics.df_materias.empty:
            texto += f"Total de materias registradas: {len(analytics.df_materias)}. "
        
        if not analytics.df_calificaciones.empty:
            texto += f"Total de calificaciones registradas: {len(analytics.df_calificaciones)}. "
        
        texto += "Opciones disponibles en pestañas: "
        
        num_pestaña = 1
        
        # Describir cada pestaña con detalle
        texto += f"Pestaña {num_pestaña}: Importar desde Excel. Permite importar datos masivos de estudiantes, calificaciones y factores desde un archivo Excel. "
        texto += "Puedes seleccionar el archivo y el sistema validará los datos antes de importarlos. "
        num_pestaña += 1
        
        texto += f"Pestaña {num_pestaña}: Registrar Estudiante. Formulario para ingresar nuevos estudiantes. "
        texto += "Campos disponibles: Matrícula (obligatorio), Nombres (obligatorio), Apellido paterno (obligatorio), "
        texto += "Apellido materno (opcional), Semestre de ingreso (obligatorio), Carrera (obligatorio), "
        texto += "Horas de estudio semanales (obligatorio), y opción para marcar si el estudiante está en riesgo de deserción. "
        num_pestaña += 1
        
        texto += f"Pestaña {num_pestaña}: Registrar Materias. Formulario para crear nuevas materias. "
        texto += "Campos: Nombre de la materia (obligatorio), Carrera (obligatorio), Semestre (obligatorio), "
        texto += "Docente asignado (opcional), y grupo inicial con período y grupo. "
        num_pestaña += 1
        
        # Si es docente, incluir la pestaña de calificaciones
        if es_docente():
            texto += f"Pestaña {num_pestaña}: Registrar Calificaciones. Permite a los docentes registrar calificaciones por materia y grupo. "
            texto += "Primero seleccionas la carrera, luego la materia, después el grupo, y finalmente puedes ingresar las calificaciones de los alumnos inscritos. "
            num_pestaña += 1
        
        texto += f"Pestaña {num_pestaña}: Registrar Factores. Permite registrar factores de riesgo o características adicionales de los estudiantes. "
        texto += "Puedes seleccionar el estudiante y agregar factores como problemas familiares, económicos, académicos, etc. "
        num_pestaña += 1
        
        texto += f"Pestaña {num_pestaña}: Inscribir Alumnos. Permite inscribir estudiantes a materias y grupos específicos. "
        texto += "Selecciona la carrera, luego la materia, el grupo, y finalmente los alumnos que deseas inscribir. "
        num_pestaña += 1
        
        texto += f"Pestaña {num_pestaña}: Asignar Docentes. Permite asignar docentes a las materias. "
        texto += "Selecciona la materia y el docente que deseas asignar. "
        
        return texto
    except Exception as e:
        return f"Error al generar contenido de registro de datos: {str(e)}. "

def leer_contenido_exportar_reportes():
    """Genera texto completo de exportar reportes para TTS"""
    try:
        from services.analytics import AnalyticsService
        from services.database import DatabaseService
        
        db = DatabaseService()
        analytics = AnalyticsService(db)
        
        texto = "Exportar Reportes. "
        texto += "Módulo para generar y descargar reportes en diferentes formatos. "
        texto += "Formatos disponibles: Excel, CSV y PDF. "
        texto += "Tipos de reporte: Reporte General, Reporte de Estudiantes, Reporte de Calificaciones, "
        texto += "Reporte de Factores de Riesgo, Reporte Personalizado. "
        
        # Información sobre datos disponibles para exportar
        if not analytics.df_estudiantes.empty:
            texto += f"Puedes exportar datos de {len(analytics.df_estudiantes)} estudiantes. "
        
        if not analytics.df_calificaciones.empty:
            texto += f"Puedes exportar {len(analytics.df_calificaciones)} registros de calificaciones. "
        
        if not analytics.df_factores.empty:
            texto += f"Puedes exportar {len(analytics.df_factores)} factores de riesgo. "
        
        texto += "Puedes filtrar por rango de calificaciones, estado de deserción y categorías de factores. "
        texto += "Selecciona el tipo de reporte y formato deseado para descargar. "
        
        return texto
    except Exception as e:
        return f"Error al generar contenido de exportar reportes: {str(e)}. "

def leer_todo_contenido_analisis_calidad_docente(analytics):
    """Lee todo el contenido de Análisis de Calidad para docente"""
    if not st.session_state.get("a11y_tts_activo", False):
        return
    
    try:
        texto = "Análisis de Calidad. Análisis por materia y grupo. "
        
        # Obtener selecciones actuales
        materia_sel = st.session_state.get("ac_materia_sel", "")
        grupo_sel = st.session_state.get("ac_grupo_sel", "")
        
        if materia_sel:
            texto += f"Materia seleccionada: {materia_sel}. "
        if grupo_sel:
            texto += f"Grupo seleccionado: {grupo_sel}. "
        
        # Obtener datos del grupo si están disponibles
        try:
            mats = analytics.db.obtener_materias() or []
            if mats and materia_sel:
                opciones_mats = {m["nombre"]: m["id"] for m in mats}
                materia_id = opciones_mats.get(materia_sel)
                if materia_id:
                    grupos = analytics.db.obtener_grupos(materia_id=materia_id) or []
                    if grupos and grupo_sel:
                        g = next((g for g in grupos if f"{g['periodo']} - {g['grupo']}" == grupo_sel), None)
                        if g:
                            datos = analytics.db.obtener_calificaciones_por(materia_id, g['periodo'], g['grupo'])
                            if datos:
                                df = pd.DataFrame(datos)
                                if "reprobado" in df.columns:
                                    reprob = int(df["reprobado"].sum())
                                    total = len(df)
                                    pct = round(100 * reprob / max(total, 1), 1)
                                    texto += f"Reprobados: {reprob} de {total}, {pct} por ciento. "
                                
                                if "calificacion_final" in df.columns:
                                    vals = pd.to_numeric(df["calificacion_final"], errors="coerce").dropna()
                                    if not vals.empty:
                                        media = float(vals.mean())
                                        mediana = float(vals.median())
                                        texto += f"Histograma de calificación final. Promedio: {media:.1f}. Mediana: {mediana:.1f}. "
                                
                                cols_ctrl = [c for c in ["u1", "u2", "u3"] if c in df.columns]
                                if cols_ctrl:
                                    texto += f"Gráfico de control por unidades: {', '.join([c.upper() for c in cols_ctrl])}. "
        except:
            pass
        
        texto += "Tabla de alumnos y calificaciones del grupo disponible. "
        
        st.session_state["a11y_ultimo_contenido"] = ""
        leer_contenido(texto)
    except Exception as e:
        import traceback
        print(f"Error al leer contenido de análisis de calidad docente: {e}")
        print(traceback.format_exc())


