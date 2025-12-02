import streamlit as st  
from services.database import DatabaseService
from services.analytics import AnalyticsService
from components.accesibilidad import panel_accesibilidad, _resetear_configuracion_a_defaults, _mostrar_contenido_panel_accesibilidad
from components.accesibilidad import leer_tabla_si_activo, leer_texto_si_activo, leer_contenido
from components.dashboard import mostrar_dashboard_principal
from components.registro_datos import (
    mostrar_registro_datos,
    mostrar_registro_calificaciones,  
)
from components.exportacion import mostrar_exportar_reportes
from components.login import mostrar_login
from services.rbac import es_docente, es_admin 
from components.analisis_calidad import (
    mostrar_analisis_calidad,
    analitica_histograma_y_control,
)


# intento de import compatible con versiones
try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    try:
        from streamlit import st_autorefresh  # algunas builds lo exponen aquí
    except Exception:
        st_autorefresh = None  # si no existe, desactivamos la función
# ===== etiquetas de menú para evitar descalces por emojis =====
MENU_DASH = "🏠 Dashboard Principal"
MENU_QUAL = "📈 Análisis de Calidad"
MENU_REG  = "📝 Registro de Datos"
MENU_EXP  = "📦 Exportar Reportes"



# Estilos
st.markdown("""
<style>
    .main-header { font-size: 3rem !important; color: #1f3a60 !important; text-align: center !important; margin-bottom: 2rem !important; font-weight: bold !important; }
    .main-header-left { font-size: 2.5rem !important; color: #2c3e50 !important; text-align: left !important; margin-bottom: 2rem !important; font-weight: bold !important; }
    .sub-header { font-size: 1.8rem; color: #2c3e50; margin-bottom: 1rem; font-weight: bold; }
    .metric-card { background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #3498db; margin-bottom: 1rem; }
    .success-text { color: #27ae60; }
    .warning-text { color: #f39c12; }
    .danger-text { color: #e74c3c; }
    
    /* Botón de accesibilidad en el header junto a Deploy */
    .stHeader {
        position: relative;
    }
    #accesibilidad-header-btn-container {
        position: fixed !important;
        top: 0 !important;
        right: 5.5rem !important;
        z-index: 1000000 !important;
        height: 3rem !important;
        display: flex !important;
        align-items: center !important;
        padding: 0 0.5rem !important;
        pointer-events: auto !important;
    }
    #accesibilidad-header-btn-container button {
        background: transparent !important;
        border: none !important;
        padding: 0.5rem !important;
        font-size: 1.2rem !important;
        color: rgba(49, 51, 63, 0.6) !important;
        box-shadow: none !important;
        cursor: pointer !important;
        height: auto !important;
        pointer-events: auto !important;
    }
    #accesibilidad-header-btn-container button:hover {
        background: rgba(0, 0, 0, 0.05) !important;
        border-radius: 4px !important;
    }
    
    /* Panel de accesibilidad colapsable - estilos compactos */
    div[data-testid="stExpander"]:has(> div > div:has-text("Configuración de Accesibilidad")) {
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def inicializar_servicios(_version: int = 2):
    db = DatabaseService()
    analytics = AnalyticsService(db)
    return db, analytics

def _mostrar_boton_accesibilidad_header():
    """Muestra el botón de accesibilidad en el header junto a Deploy"""
    mostrar_accesibilidad = st.session_state.get("mostrar_panel_accesibilidad", False)
    btn_text = "♿" if not mostrar_accesibilidad else "✓"
    
    # Usar solo CSS para posicionar el botón de Streamlit en el header
    st.markdown(f"""
    <style>
    button[key="btn_accesibilidad_header"] {{
        position: fixed !important;
        top: 0.25rem !important;
        right: 5.5rem !important;
        z-index: 1000000 !important;
        background: transparent !important;
        border: none !important;
        padding: 0.5rem !important;
        font-size: 1.2rem !important;
        color: rgba(49, 51, 63, 0.6) !important;
        box-shadow: none !important;
        cursor: pointer !important;
    }}
    button[key="btn_accesibilidad_header"]:hover {{
        background: rgba(0, 0, 0, 0.05) !important;
        border-radius: 4px !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Botón de Streamlit posicionado con CSS
    if st.button(btn_text, key="btn_accesibilidad_header", help="Configuración de accesibilidad", use_container_width=False):
        st.session_state["mostrar_panel_accesibilidad"] = not mostrar_accesibilidad
        if st.session_state.get("mostrar_menu_perfil", False):
            st.session_state["mostrar_menu_perfil"] = False
        st.rerun()

def _mostrar_panel_accesibilidad_colapsable():
    """Muestra el panel de accesibilidad como un contenedor colapsable compacto"""
    # Inicializar estado y cargar configuración
    from components.accesibilidad import _init_state, cargar_configuracion_usuario
    from services.rbac import usuario_id
    _init_state()
    user_id = usuario_id()
    if user_id:
        usuario_anterior = st.session_state.get("a11y_usuario_configurado")
        if usuario_anterior != user_id:
            st.session_state["a11y_config_cargada"] = False
            st.session_state["a11y_ultimo_contenido"] = ""
        cargar_configuracion_usuario()
    
    # Usar un expander de Streamlit nativo - más simple, funcional y compacto
    with st.expander("🎧 Configuración de Accesibilidad", expanded=True):
        # Botón para cerrar el panel
        col_close1, col_close2 = st.columns([10, 1])
        with col_close1:
            st.markdown("")
        with col_close2:
            if st.button("Cerrar", key="cerrar_panel_accesibilidad", use_container_width=True):
                st.session_state["mostrar_panel_accesibilidad"] = False
                st.rerun()
        
        # Contenido del panel
        _mostrar_contenido_panel_accesibilidad()




def main():
    db, analytics = inicializar_servicios()
    
    # Aplicar accesibilidad en todas las pantallas
    from components.accesibilidad import aplicar_accesibilidad
    aplicar_accesibilidad()

    # CORREGIR: Evitar bucle en el título
    titulo_container = st.container()
    with titulo_container:
        st.markdown("""
        <style>
            .main-header {
                font-size: 3rem !important;
                color: #1f3a60 !important;
                text-align: center !important;
                margin-bottom: 2rem !important;
                font-weight: bold !important;
            }
        </style>
        """, unsafe_allow_html=True)
        st.markdown('<div class="main-header">🎓 SISTEMA DE ANÁLISIS EDUCATIVO - ITT</div>', unsafe_allow_html=True)
        
        # AGREGAR botón de lectura para el título
        if st.session_state.get("a11y_tts_activo", False):
            from components.accesibilidad import crear_boton_lectura
            col1, col2 = st.columns([4, 1])
            with col2:
                try:
                    crear_boton_lectura(
                        "Sistema de Análisis Educativo del Instituto Tecnológico de Tijuana", 
                        "🔊 Leer título", 
                        "titulo_principal"
                    )
                except Exception:
                    pass
    
    # Panel de accesibilidad colapsable (justo después del título, compacto y no estorboso)
    if st.session_state.get("mostrar_panel_accesibilidad", False):
        _mostrar_panel_accesibilidad_colapsable()

    # Sesión
    if "user" not in st.session_state:
        st.session_state["user"] = None

    if st.session_state["user"] is None:
        # NO resetear accesibilidad aquí para permitir que funcione en login
        # Solo limpiar estados de usuario específicos
        if not st.session_state.get("a11y_login_iniciado", False):
            st.session_state["a11y_config_cargada"] = False
            st.session_state["a11y_usuario_configurado"] = None
            st.session_state["a11y_usuario_leido"] = False
            st.session_state["a11y_dashboard_leido"] = False
            st.session_state["a11y_login_iniciado"] = True
        
        # Usar clase con tamaño menor que el título principal pero alineado a la izquierda
        st.markdown("""
        <style>
            .main-header-left {
                font-size: 2.5rem !important;
                color: #2c3e50 !important;
                text-align: left !important;
                margin-bottom: 2rem !important;
                font-weight: bold !important;
            }
        </style>
        """, unsafe_allow_html=True)
        st.markdown('<div class="main-header-left">Acceso</div>', unsafe_allow_html=True)
        mostrar_login()
        st.stop()

    # Botón de accesibilidad en el header
    _mostrar_boton_accesibilidad_header()
    
    # Sidebar - CORREGIR para evitar bucles
    with st.sidebar:
        st.image("https://www.tijuana.tecnm.mx/wp-content/themes/tecnm/images/logo_TECT.png", width=150)
        
        # Botón de usuario en el sidebar (discreto)
        st.divider()
        usuario_nombre = st.session_state["user"]["usuario"]
        mostrar_perfil = st.session_state.get("mostrar_menu_perfil", False)
        
        if st.button(f"👤 {usuario_nombre}", key="btn_usuario_sidebar", use_container_width=True, help="Menú de usuario"):
            st.session_state["mostrar_menu_perfil"] = not mostrar_perfil
            if st.session_state.get("mostrar_panel_accesibilidad", False):
                st.session_state["mostrar_panel_accesibilidad"] = False
            st.rerun()
        
        # Menú de perfil expandible en sidebar
        if st.session_state.get("mostrar_menu_perfil", False):
            with st.expander("Información de usuario", expanded=True):
                st.caption(f"Rol: **{st.session_state['user'].get('rol', 'docente')}**")
                
                # SOLO leer una vez al cargar
                if (st.session_state.get("a11y_tts_activo", False) and 
                    not st.session_state.get("a11y_usuario_leido", False)):
                    try:
                        leer_contenido(f"Sesión activa para el usuario: {st.session_state['user']['usuario']}")
                        st.session_state["a11y_usuario_leido"] = True
                    except Exception:
                        pass
                
                # Opción para abrir accesibilidad desde el menú de perfil
                if st.button("♿ Configuración de Accesibilidad", key="accesibilidad_desde_perfil", use_container_width=True):
                    st.session_state["mostrar_panel_accesibilidad"] = True
                    st.session_state["mostrar_menu_perfil"] = False
                    st.rerun()
                
                st.divider()
                
                if st.button("🚪 Cerrar sesión", key="cerrar_sesion_menu", use_container_width=True, type="primary"):
                    # Resetear TODOS los estados de accesibilidad ANTES de cerrar sesión
                    _resetear_configuracion_a_defaults()
                    st.session_state["a11y_usuario_leido"] = False
                    st.session_state["a11y_dashboard_leido"] = False
                    st.session_state["a11y_ultimo_contenido"] = ""
                    st.session_state["a11y_config_cargada"] = False
                    st.session_state["a11y_usuario_configurado"] = None
                    st.session_state["mostrar_panel_accesibilidad"] = False
                    st.session_state["mostrar_menu_perfil"] = False
                    # Limpiar valores previos también
                    for key in list(st.session_state.keys()):
                        if key.startswith("a11y_") and key.endswith("_previo"):
                            del st.session_state[key]
                    # Cerrar sesión al final
                    st.session_state["user"] = None
                    st.rerun()
        
        st.divider()
        
        # NAVEGACIÓN con botones de lectura
        nav_container = st.container()
        with nav_container:
            st.sidebar.markdown("### Navegación")
            
            if st.session_state.get("a11y_tts_activo", False):
                from components.accesibilidad import crear_boton_lectura
                try:
                    crear_boton_lectura(
                        "Panel de navegación con opciones: Dashboard Principal, Análisis de Calidad, Registro de Datos, Exportar Reportes",
                        "🔊 Leer opciones",
                        "navegacion_opciones"
                    )
                except Exception:
                    pass

            menu_items = [MENU_DASH, MENU_QUAL]
            if es_docente() or es_admin():
                menu_items.append(MENU_REG)
            menu_items.append(MENU_EXP)

            # Obtener índice de la opción guardada previamente (para preservar selección al cerrar accesibilidad)
            opcion_previa = st.session_state.get("opcion_actual_menu", MENU_DASH)
            indice_previo = 0
            if opcion_previa in menu_items:
                indice_previo = menu_items.index(opcion_previa)
            
            opcion = st.sidebar.radio("Selecciona una opción:", menu_items, index=indice_previo, key="nav_main")
            
            # Guardar opción actual para que leer_todo_contenido_pagina pueda accederla
            st.session_state["opcion_actual_menu"] = opcion
            
            # Leer opción seleccionada solo cuando cambia
            if st.session_state.get("a11y_tts_activo", False):
                opcion_anterior = st.session_state.get("a11y_opcion_anterior", "")
                if opcion != opcion_anterior:
                    try:
                        leer_contenido(f"Opción seleccionada: {opcion}")
                        st.session_state["a11y_opcion_anterior"] = opcion
                    except Exception:
                        pass

        st.divider()
        if st.button("🔄 Actualizar Datos", use_container_width=True):
            analytics.actualizar_datos()
            st.rerun()

        if st.button("Recargar servicios"):
            st.cache_resource.clear()
            st.rerun()

        st.divider()
        # controles de auto refresh
        auto_on = st.toggle("Auto actualizar", value=True, help="Refresca la vista de forma periódica")
        auto_secs = st.select_slider(
            "Intervalo",
            options=[10, 15, 30, 60, 120, 300],
            value=30,
            help="Frecuencia de actualización automática"
        )
        
        # Guardar en session_state para que leer_todo_contenido_pagina pueda acceder
        st.session_state["auto_actualizar"] = auto_on
        st.session_state["auto_secs"] = auto_secs
        
        # REMOVIDO: No leer automáticamente la configuración de auto actualizar
        # Esto causaba que se leyera cada vez que se hacía clic en otros botones
        
        # texto informativo
        if auto_on:
            st.caption(f"Auto actualización cada {auto_secs} s")
        else:
            st.caption("Auto actualización desactivada")
        st.caption("Usa el botón 'Actualizar Datos' para forzar una actualización")

    # Auto refresh solo en vistas de lectura
    if auto_on and st_autorefresh is not None and opcion in (MENU_DASH, MENU_QUAL):
        # disparamos el refresh y actualizamos datos en cada ciclo
        st_autorefresh(interval=auto_secs * 1000, key="auto_refresh_main")
        try:
            analytics.actualizar_datos()
        except Exception:
            pass

    # Contenido
    try:
        if opcion == MENU_DASH:
            mostrar_dashboard_principal(analytics)

        elif opcion == MENU_QUAL:
            # Admin ve las herramientas completas
            if es_admin():
                mostrar_analisis_calidad(analytics)
            else:
                # Docente: oculta herramientas y muestra solo su análisis por materia y grupo
                from components.accesibilidad import crear_boton_lectura, leer_todo_contenido_analisis_calidad_docente
                
                if st.session_state.get("a11y_tts_activo", False):
                    col_titulo, col_boton, col_leer_todo = st.columns([3, 1, 1])
                    with col_titulo:
                        st.markdown('<div class="sub-header">Análisis de Calidad</div>', unsafe_allow_html=True)
                    with col_boton:
                        crear_boton_lectura(
                            "Análisis de Calidad - Análisis por materia y grupo",
                            "🔊",
                            "analisis_calidad_docente_titulo"
                        )
                    with col_leer_todo:
                        if st.button("📖 Leer todo", key="leer_todo_analisis_calidad_docente"):
                            leer_todo_contenido_analisis_calidad_docente(analytics)
                            st.rerun()
                else:
                    st.markdown('<div class="sub-header">Análisis de Calidad</div>', unsafe_allow_html=True)
                analitica_histograma_y_control(analytics)

        elif opcion == MENU_REG:
            # Docente: solo la vista de registrar calificaciones
            if es_docente() and not es_admin():
                st.subheader("Registrar Calificaciones")
                mostrar_registro_calificaciones(analytics)
            else:
                # Admin: todo el módulo de registro
                mostrar_registro_datos(db)

        elif opcion == MENU_EXP:
            mostrar_exportar_reportes(db)

    except Exception as e:
        st.error(f"Error cargando la sección: {e}")

if __name__ == "__main__":
    main()