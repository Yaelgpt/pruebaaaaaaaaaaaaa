import os
import streamlit as st
from services.auth_service import AuthService
from components.accesibilidad import aplicar_accesibilidad, _init_state


def _mostrar_contenido_accesibilidad_login():
    """Panel de accesibilidad COMPLETO para login (igual que el panel principal, sin guardar en BD)"""
    from components.accesibilidad import (
        _mostrar_contenido_panel_accesibilidad,
        _on_checkbox_change,
        _guardar_si_cambio,
        _tts_service,
        leer_contenido,
        detener_lectura,
        leer_todo_contenido_pagina
    )
    
    # Usar la misma función que el panel principal, pero sin el botón de guardar
    st.markdown("**🔊 Texto a Voz (TTS)**")
    st.caption("💡 Nota: Algunos navegadores requieren interacción del usuario antes de permitir síntesis de voz. Si no escuchas nada, intenta hacer clic en cualquier parte de la página primero.")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        tts_activo = st.checkbox(
            "Habilitar Texto a Voz",
            value=st.session_state.get("a11y_tts_activo", False),
            key="a11y_tts_activo_login_cb",
            help="Activa las funciones de texto a voz. Podrás leer contenido haciendo clic en botones específicos, gráficos y tablas.",
            on_change=_on_checkbox_change,
            args=("a11y_tts_activo",)
        )
    
    with col2:
        if st.button("🔊 Probar", key="probar_tts_login_btn"):
            tts_activo_temp = st.session_state.get("a11y_tts_activo", False)
            st.session_state["a11y_tts_activo"] = True
            texto_prueba = "Síntesis de voz activada correctamente. Esta es una prueba del sistema de texto a voz."
            leer_contenido(texto_prueba)
            st.session_state["a11y_tts_activo"] = tts_activo_temp
            st.rerun()
    
    with col3:
        if st.button("📖 Leer todo", key="leer_todo_login_btn"):
            tts_activo_temp = st.session_state.get("a11y_tts_activo", False)
            st.session_state["a11y_tts_activo"] = True
            st.session_state["a11y_ultimo_contenido"] = ""
            leer_todo_contenido_pagina()
            st.session_state["a11y_tts_activo"] = tts_activo_temp
            st.rerun()
    
    with col4:
        if st.session_state.get("a11y_tts_activo", False):
            if st.button("⏹️ Detener", key="detener_tts_login_btn", help="Detiene la lectura actual de texto a voz"):
                detener_lectura()
                st.rerun()
    
    st.session_state["a11y_tts_activo"] = tts_activo
    
    # Opción de TTS hover (leer al pasar el cursor) - INDEPENDIENTE de "Habilitar Texto a Voz"
    tts_hover = st.checkbox(
        "🖱️ Leer al pasar el cursor",
        value=st.session_state.get("a11y_tts_hover", False),
        key="a11y_tts_hover_login_cb",
        help="Lee automáticamente el contenido cuando pasas el cursor por encima. Ideal para personas con discapacidad visual. Funciona independientemente de otras opciones de TTS.",
        on_change=_on_checkbox_change,
        args=("a11y_tts_hover",)
    )
    st.session_state["a11y_tts_hover"] = tts_hover
    
    if tts_hover:
        st.info("🎯 **Modo cursor activo**: Pasa el cursor sobre cualquier elemento (textos, botones, gráficos, tablas) para escuchar su contenido.")
    
    if tts_activo:
        col3, col4 = st.columns(2)
        with col3:
            velocidad_actual = st.slider(
                "Velocidad",
                min_value=0.5,
                max_value=2.0,
                value=float(st.session_state.get("a11y_tts_velocidad", 1.0)),
                step=0.1,
                key="a11y_tts_velocidad_login_slider"
            )
            st.session_state["a11y_tts_velocidad"] = velocidad_actual
        
        with col4:
            voz_seleccionada = st.selectbox(
                "Voz/Idioma",
                options=list(_tts_service.voces_disponibles.keys()),
                index=list(_tts_service.voces_disponibles.values()).index(
                    st.session_state.get("a11y_tts_voz", "es-ES")
                ) if st.session_state.get("a11y_tts_voz", "es-ES") in _tts_service.voces_disponibles.values() else 0,
                key="a11y_tts_voz_login_select",
                help="Selecciona el idioma y variante de la voz. La disponibilidad depende de tu navegador."
            )
            voz_actual = _tts_service.voces_disponibles[voz_seleccionada]
            st.session_state["a11y_tts_voz"] = voz_actual
            
            if voz_actual != "es-ES":
                st.caption(f"📌 Idioma seleccionado: {voz_seleccionada}. Si no funciona, verifica que tu navegador tenga voces instaladas para este idioma.")
    
    st.divider()
    st.markdown("**🎨 Ajustes Visuales**")
    
    # Modo oscuro/claro - con callback para aplicación instantánea
    modo_oscuro = st.checkbox(
        "🌙 Modo oscuro",
        value=st.session_state.get("a11y_modo_oscuro", False),
        key="a11y_modo_oscuro_login_cb",
        help="Cambia el color de textos y fondos a modo oscuro",
        on_change=_on_checkbox_change,
        args=("a11y_modo_oscuro",)
    )
    st.session_state["a11y_modo_oscuro"] = modo_oscuro
    
    # Alto contraste - ahora disponible en ambos modos (claro y oscuro)
    contraste_label = "⚡ Alto contraste (modo oscuro)" if modo_oscuro else "⚡ Alto contraste (modo claro)"
    contraste_help = "Aumenta el contraste con colores brillantes sobre fondo negro" if modo_oscuro else "Aumenta el contraste con bordes más marcados"
    alto_contraste = st.checkbox(
        contraste_label,
        value=st.session_state.get("a11y_contraste", False),
        key="a11y_contraste_login_cb",
        help=contraste_help,
        on_change=_on_checkbox_change,
        args=("a11y_contraste",)
    )
    st.session_state["a11y_contraste"] = alto_contraste
    
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
        key="a11y_modo_daltonismo_login_select",
        help="Ajusta los colores de la interfaz para mejorar la visibilidad según el tipo de daltonismo"
    )
    modo_daltonismo = opciones_keys[opciones_labels.index(modo_daltonismo_label)]
    st.session_state["a11y_modo_daltonismo"] = modo_daltonismo
    
    st.divider()
    st.markdown("**📝 Tipografía y Espaciado**")
    
    # Tipografía para dislexia - con callback
    fuente_dislexia = st.checkbox(
        "📖 Tipografía para dislexia",
        value=st.session_state.get("a11y_dyslexia", False),
        key="a11y_dyslexia_login_cb",
        on_change=_on_checkbox_change,
        args=("a11y_dyslexia",)
    )
    st.session_state["a11y_dyslexia"] = fuente_dislexia
    
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
                key="a11y_esp_letras_login_slider"
            )
            st.session_state["a11y_espaciado_letras"] = esp_letras
        with col2:
            esp_palabras = st.slider(
                "Espaciado entre palabras",
                min_value=0.0,
                max_value=0.2,
                value=float(st.session_state.get("a11y_espaciado_palabras", 0.0)),
                step=0.01,
                key="a11y_esp_palabras_login_slider"
            )
            st.session_state["a11y_espaciado_palabras"] = esp_palabras
        with col3:
            esp_lineas = st.slider(
                "Espaciado entre líneas",
                min_value=1.0,
                max_value=2.5,
                value=float(st.session_state.get("a11y_espaciado_lineas", 1.6)),
                step=0.1,
                key="a11y_esp_lineas_login_slider"
            )
            st.session_state["a11y_espaciado_lineas"] = esp_lineas
    
    # Tamaño de texto general
    texto_actual = st.slider(
        "Tamaño de texto %",
        min_value=90,
        max_value=150,
        step=2,
        value=int(st.session_state.get("a11y_texto", 100)),
        key="a11y_texto_login_slider",
    )
    st.session_state["a11y_texto"] = texto_actual
    
    # Tamaño de texto en login
    texto_login_actual = st.slider(
        "Tamaño de texto en inicio de sesión %",
        min_value=100,
        max_value=150,
        step=5,
        value=int(st.session_state.get("a11y_texto_login", 100)),
        key="a11y_texto_login_login_slider",
    )
    st.session_state["a11y_texto_login"] = texto_login_actual
    
    st.divider()
    st.markdown("**🎯 Modo Concentración**")
    
    # Modo concentración con icono - con callback
    modo_concentracion = st.checkbox(
        "🎯 Modo concentración",
        value=st.session_state.get("a11y_modo_concentracion", False),
        key="a11y_modo_concentracion_login_cb",
        help="Reduce distracciones enfocando el contenido principal",
        on_change=_on_checkbox_change,
        args=("a11y_modo_concentracion",)
    )
    st.session_state["a11y_modo_concentracion"] = modo_concentracion
    
    # Opción de resaltar foco de teclado
    resaltar_focus = st.checkbox(
        "🔦 Resaltar foco de teclado",
        value=st.session_state.get("a11y_resaltar_focus", False),
        key="a11y_resaltar_login_cb",
        on_change=_on_checkbox_change,
        args=("a11y_resaltar_focus",),
        help="Resalta de forma muy visible el elemento que tiene el foco al navegar con Tab. Útil para navegación por teclado."
    )
    st.session_state["a11y_resaltar_focus"] = resaltar_focus
    
    if resaltar_focus:
        st.info("🔦 **Foco visible activado**: Usa Tab para navegar y verás un resaltado naranja brillante en cada elemento.")
    
    # Nota: No hay botón de guardar porque no hay usuario logueado en el login
    st.caption("💡 Los cambios se aplican automáticamente. Inicia sesión para guardar tu configuración permanentemente.")

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
      /* Aplicar tamaño a todo el contenido del login, EXCEPTO los títulos principales */
      [data-testid="stAppViewContainer"] *:not(.main-header):not(.main-header-left):not(.sub-header) {{
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