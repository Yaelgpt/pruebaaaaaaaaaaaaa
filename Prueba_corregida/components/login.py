import os
import streamlit as st
from services.auth_service import AuthService
from components.accesibilidad import aplicar_accesibilidad, _init_state


def _mostrar_contenido_accesibilidad_login():
    """Panel de accesibilidad simplificado para login (sin guardar en BD)"""
    
    # Guardar valores anteriores para detectar cambios
    prev_oscuro = st.session_state.get("a11y_modo_oscuro", False)
    prev_contraste = st.session_state.get("a11y_contraste", False)
    prev_daltonismo = st.session_state.get("a11y_modo_daltonismo", "ninguno")
    prev_dislexia = st.session_state.get("a11y_dyslexia", False)
    prev_tamanio = st.session_state.get("a11y_texto_login", 100)
    
    st.markdown("**🎨 Ajustes Visuales**")
    
    # Modo oscuro
    modo_oscuro = st.checkbox(
        "🌙 Modo oscuro",
        value=prev_oscuro,
        key="a11y_modo_oscuro_login_cb",
        help="Activa el modo oscuro para reducir fatiga visual"
    )
    st.session_state["a11y_modo_oscuro"] = modo_oscuro
    
    # Alto contraste
    alto_contraste = st.checkbox(
        "⚡ Alto contraste",
        value=prev_contraste,
        key="a11y_contraste_login_cb",
    )
    st.session_state["a11y_contraste"] = alto_contraste
    
    # Modo daltonismo
    opciones_daltonismo = {
        "ninguno": "Sin ajuste",
        "protanopia": "Protanopia (dificultad con rojos)",
        "deuteranopia": "Deuteranopia (dificultad con verdes)",
        "tritanopia": "Tritanopia (dificultad con azules)"
    }
    opciones_keys = list(opciones_daltonismo.keys())
    opciones_labels = list(opciones_daltonismo.values())
    
    indice_actual = opciones_keys.index(prev_daltonismo) if prev_daltonismo in opciones_keys else 0
    
    modo_daltonismo_label = st.selectbox(
        "🎨 Modo para daltonismo",
        options=opciones_labels,
        index=indice_actual,
        key="a11y_modo_daltonismo_login_select",
        help="Ajusta los colores para mejorar visibilidad"
    )
    modo_daltonismo = opciones_keys[opciones_labels.index(modo_daltonismo_label)]
    st.session_state["a11y_modo_daltonismo"] = modo_daltonismo
    
    st.divider()
    st.markdown("**📝 Tipografía**")
    
    # Tipografía para dislexia
    fuente_dislexia = st.checkbox(
        "📖 Tipografía para dislexia",
        value=prev_dislexia,
        key="a11y_dyslexia_login_cb",
    )
    st.session_state["a11y_dyslexia"] = fuente_dislexia
    
    # Tamaño de texto
    tamanio = st.slider(
        "Tamaño de texto %",
        min_value=80,
        max_value=150,
        value=prev_tamanio,
        step=5,
        key="a11y_texto_login_slider"
    )
    st.session_state["a11y_texto_login"] = tamanio
    st.session_state["a11y_texto"] = tamanio
    
    # Detectar si hubo algún cambio y hacer rerun para aplicar
    cambio = (
        modo_oscuro != prev_oscuro or
        alto_contraste != prev_contraste or
        modo_daltonismo != prev_daltonismo or
        fuente_dislexia != prev_dislexia or
        tamanio != prev_tamanio
    )
    
    if cambio:
        st.rerun()

def mostrar_login():
    # Inicializar estado de accesibilidad
    _init_state()
    
    # Mostrar botón de accesibilidad en el login
    mostrar_accesibilidad = st.session_state.get("mostrar_panel_accesibilidad_login", False)
    
    # Botón de accesibilidad en la esquina superior derecha
    col_acc1, col_acc2 = st.columns([10, 1])
    with col_acc1:
        st.markdown("")
    with col_acc2:
        btn_text = "♿" if not mostrar_accesibilidad else "✓"
        if st.button(btn_text, key="btn_accesibilidad_login", help="Configuración de accesibilidad"):
            st.session_state["mostrar_panel_accesibilidad_login"] = not mostrar_accesibilidad
            st.rerun()
    
    # Mostrar panel de accesibilidad si está activo (usando expander nativo de Streamlit)
    if st.session_state.get("mostrar_panel_accesibilidad_login", False):
        with st.expander("🎧 Configuración de Accesibilidad", expanded=True):
            # Botón para cerrar y aplicar cambios
            col_close1, col_close2 = st.columns([10, 1])
            with col_close1:
                st.caption("💡 Los cambios se aplican automáticamente")
            with col_close2:
                if st.button("Cerrar", key="cerrar_panel_accesibilidad_login", use_container_width=True):
                    st.session_state["mostrar_panel_accesibilidad_login"] = False
                    st.rerun()
            
            # Contenido del panel simplificado para login (sin guardar en BD)
            _mostrar_contenido_accesibilidad_login()
    
    # Aplicar accesibilidad DESPUÉS de procesar cambios
    aplicar_accesibilidad()
    
    # Aplicar tamaño de texto para el login (usar valor de session_state directamente)
    tamanio_login = st.session_state.get("a11y_texto_login", 100)
    
    st.markdown(f"""
    <style>
      .login-card {{max-width:420px;margin:6rem auto;padding:2rem;border:1px solid #ddd;border-radius:12px;background:#fff;box-shadow:0 8px 24px rgba(0,0,0,.06)}}
      [data-testid="stForm"] *,
      [data-testid="stForm"] input,
      [data-testid="stForm"] button,
      [data-testid="stForm"] label,
      [data-testid="stForm"] .stTextInput label,
      [data-testid="stForm"] .stButton button {{
        font-size: {tamanio_login}% !important;
      }}
      .login-card * {{
        font-size: {tamanio_login}% !important;
      }}
      /* Aplicar tamaño a todo el contenido del login */
      [data-testid="stAppViewContainer"] * {{
        font-size: {tamanio_login}% !important;
      }}
    </style>
    """, unsafe_allow_html=True)

    if "user" not in st.session_state:
        st.session_state["user"] = None

    # Sesión activa
    if st.session_state["user"] is not None:
        u = st.session_state["user"]
        st.success(f"Sesión: {u['usuario']}  Rol: {u.get('rol','docente')}")
        if st.button("Cerrar sesión"):
            st.session_state["user"] = None
            st.rerun()
        return

    tab_login, tab_signup = st.tabs(["🔐 Iniciar sesión", "🆕 Crear usuario"])

    # Iniciar sesión
    with tab_login:
        with st.form("frm_login"):
            login_usuario = st.text_input("Usuario")
            login_password = st.text_input("Contraseña", type="password")
            login_ok = st.form_submit_button("Entrar")
        if login_ok:
            try:
                auth = AuthService()
                u = auth.verificar_login(login_usuario, login_password)
                if u:
                    st.session_state["user"] = u
                    st.success("Acceso concedido")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
            except Exception as e:
                st.error(f"Error al iniciar sesión. Detalle: {e}")

    # Crear usuario con rol seleccionado
    with tab_signup:
        st.info("Crea un usuario en la tabla usuarios. Elige el rol al crearlo.")
        with st.form("frm_signup"):
            signup_usuario = st.text_input("Nuevo usuario")
            signup_pwd1 = st.text_input("Contraseña", type="password")
            signup_pwd2 = st.text_input("Repite la contraseña", type="password")
            signup_rol = st.radio("Rol", ["docente", "admin"], index=0, horizontal=True)
            signup_ok = st.form_submit_button("Crear")
        if signup_ok:
            if not signup_usuario or not signup_pwd1:
                st.error("Completa usuario y contraseña")
            elif signup_pwd1 != signup_pwd2:
                st.error("Las contraseñas no coinciden")
            else:
                try:
                    auth = AuthService()
                    creado = auth.crear_usuario(signup_usuario, signup_pwd1, rol=signup_rol)
                    if creado:
                        st.success(f"Usuario {signup_usuario} creado con rol {signup_rol}. Ahora inicia sesión.")
                    else:
                        st.warning("Ese usuario ya existe")
                except Exception as e:
                    st.error(f"Error al crear usuario. Detalle: {e}")