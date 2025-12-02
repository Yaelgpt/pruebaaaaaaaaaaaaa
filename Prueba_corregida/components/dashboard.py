import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from components.accesibilidad import obtener_colores_grafica, aplicar_colores_figura, configurar_matplotlib_daltonismo


# AGREGAR ESTAS FUNCIONES AL INICIO DEL ARCHIVO dashboard.py
def tabla_accesible(dataframe, table_id="default_table", caption=""):
    """Muestra tabla con capacidad de lectura por celda mediante TTS"""
    
    # Mostrar la tabla normal
    st.dataframe(dataframe, use_container_width=True, height=520, hide_index=True)
    
    # Solo si TTS está activo, mostrar controles de lectura
    if st.session_state.get("a11y_tts_activo", False):
        st.markdown("---")
        st.caption("🔊 **Lectura accesible** - Selecciona contenido para leer")
        
        # Crear columnas para los controles
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Selector de filas y columnas para lectura específica
            fila_seleccionada = st.selectbox(
                "Fila a leer",
                options=list(range(len(dataframe))),
                format_func=lambda x: f"Fila {x+1}",
                key=f"fila_{table_id}"
            )
        
        with col2:
            if st.button("📖 Leer fila", key=f"leer_fila_{table_id}"):
                leer_fila_tabla(dataframe, fila_seleccionada, table_id)
        
        with col3:
            if st.button("⏹️ Detener", key=f"detener_{table_id}"):
                from components.accesibilidad import detener_lectura
                detener_lectura()

def leer_fila_tabla(dataframe, fila_index, table_id):
    """Lee una fila específica de la tabla usando TTS"""
    try:
        if fila_index < len(dataframe):
            fila = dataframe.iloc[fila_index]
            texto_fila = f"Fila {fila_index + 1}: "
            
            for columna, valor in fila.items():
                texto_fila += f"{columna}: {valor}. "
            
            from components.accesibilidad import leer_contenido
            leer_contenido(texto_fila)
            
    except Exception as e:
        st.error(f"Error al leer fila: {e}")

def mostrar_dashboard_principal(analytics):
    """Dashboard principal con Distribucion arriba y Asistencia + Tendencia abajo."""
    
    from components.accesibilidad import leer_dashboard_automatico, leer_metricas_automatico, crear_boton_lectura, leer_elemento_seleccionado
    


    # AGREGAR: Botón para leer título
    if st.session_state.get("a11y_tts_activo", False):
        col_titulo, col_boton = st.columns([3, 1])
        with col_titulo:
            st.markdown('<div class="sub-header">📊 Dashboard de Análisis Académico</div>', unsafe_allow_html=True)
        with col_boton:
            crear_boton_lectura("Dashboard de Análisis Académico - Vista principal del sistema", "🔊 Leer título", "dashboard_titulo")
    else:
        st.markdown('<div class="sub-header">📊 Dashboard de Análisis Académico</div>', unsafe_allow_html=True)

    # métricas
    metricas = analytics.calcular_metricas_principales()
    
    # MODIFICAR: Lectura de métricas con botones individuales
    if metricas['total_estudiantes'] > 0:
        c1, c2, c3, c4, c5 = st.columns(5)
        
        with c1: 
            st.metric("Estudiantes", metricas['total_estudiantes'])
            if st.session_state.get("a11y_tts_activo", False):
                crear_boton_lectura(f"Total estudiantes: {metricas['total_estudiantes']}", "🔊", "metric_estudiantes")
        
        with c2: 
            st.metric("Calificaciones", metricas['total_calificaciones'])
            if st.session_state.get("a11y_tts_activo", False):
                crear_boton_lectura(f"Total calificaciones: {metricas['total_calificaciones']}", "🔊", "metric_calificaciones")
        
        with c3: 
            st.metric("Aprobación", f"{metricas['tasa_aprobacion']}%")
            if st.session_state.get("a11y_tts_activo", False):
                crear_boton_lectura(f"Tasa de aprobación: {metricas['tasa_aprobacion']}%", "🔊", "metric_aprobacion")
        
        with c4: 
            st.metric("Reprobación", f"{metricas['tasa_reprobacion']}%")
            if st.session_state.get("a11y_tts_activo", False):
                crear_boton_lectura(f"Tasa de reprobación: {metricas['tasa_reprobacion']}%", "🔊", "metric_reprobacion")
        
        with c5: 
            st.metric("Deserción", f"{metricas['tasa_desercion']}%")
            if st.session_state.get("a11y_tts_activo", False):
                crear_boton_lectura(f"Tasa de deserción: {metricas['tasa_desercion']}%", "🔊", "metric_desercion")

    # AGREGAR: Botón para leer sección completa
    if st.session_state.get("a11y_tts_activo", False):
        col_sec, col_btn = st.columns([4, 1])
        with col_sec:
            st.subheader("📊 Distribución de Calificaciones")

        with col_btn:
            crear_boton_lectura(
                "Distribución de Calificaciones - Gráfico histograma mostrando la distribución de calificaciones finales de los estudiantes", 
                "🔊 Leer sección", 
                "distribucion_seccion"
            )
    else:
        st.subheader("📊 Distribución de Calificaciones")

    mostrar_distribucion_calificaciones(analytics)

    st.divider()

    # Sección inferior con botones de lectura
    if st.session_state.get("a11y_tts_activo", False):
        col_left_head, col_right_head = st.columns(2)
        
        with col_left_head:
            col_sec, col_btn = st.columns([3, 1])
            with col_sec:
                st.subheader("📊 Análisis de Asistencia")
            with col_btn:
                crear_boton_lectura("Análisis de Asistencia - Gráficos de asistencia por materia y grupos", "🔊", "asistencia_seccion")
        
        with col_right_head:
            col_sec, col_btn = st.columns([3, 1])
            with col_sec:
                st.subheader("📈 Tendencia por Unidades")
            with col_btn:
                crear_boton_lectura("Tendencia por Unidades - Promedios de calificaciones por unidad académica", "🔊", "tendencia_seccion")
    else:
        col_left_head, col_right_head = st.columns(2)
        with col_left_head:
            st.subheader("📊 Análisis de Asistencia")
        with col_right_head:
            st.subheader("📈 Tendencia por Unidades")

    # fila 2: asistencia y tendencia en paralelo
    col_left, col_right = st.columns([1, 1], gap="large")
    with col_left:
        grafica_asistencia_dashboard(analytics)
    with col_right:
        mostrar_tendencia_unidades(analytics)
    
    # SOLO leer automáticamente si es la primera vez
    if st.session_state.get("a11y_tts_activo", False) and not st.session_state.get("a11y_dashboard_leido", False):
        leer_dashboard_automatico()
        st.session_state["a11y_dashboard_leido"] = True

def _nombre_completo_row(row: dict) -> str:
    partes = []
    if row.get("nombres"):
        partes.append(str(row["nombres"]).strip())
    if row.get("apellido_paterno"):
        partes.append(str(row["apellido_paterno"]).strip())
    if row.get("apellido_materno") and str(row["apellido_materno"]).strip().lower() != "nan":
        partes.append(str(row["apellido_materno"]).strip())
    return " ".join(partes) if partes else f"ID {row.get('id','')}"


def mostrar_distribucion_calificaciones(analytics):
    import unicodedata, re

    def _norm(s):
        if s is None: 
            return ""
        s = unicodedata.normalize("NFKD", str(s))
        s = "".join(c for c in s if not unicodedata.combining(c))
        return re.sub(r"\s+", " ", s).strip().lower()

    

    dfc = analytics.df_calificaciones.copy()
    if dfc.empty or "calificacion_final" not in dfc.columns:
        st.info("No hay datos de calificaciones para mostrar")
        return

    # Catálogos para nombres legibles
    dm = analytics.df_materias[["id", "nombre"]].copy() if not analytics.df_materias.empty else pd.DataFrame(columns=["id","nombre"])
    de = analytics.df_estudiantes[["id","nombres","apellido_paterno","apellido_materno","nombre"]].copy() if not analytics.df_estudiantes.empty else pd.DataFrame(columns=["id","nombres","apellido_paterno","apellido_materno","nombre"])
    de = de.fillna("")
    de["alumno"] = (
        de["nombres"].astype(str).str.strip() + " " +
        de["apellido_paterno"].astype(str).str.strip() + " " +
        de["apellido_materno"].astype(str).str.strip()
    ).str.replace(r"\s+", " ", regex=True).str.strip()

    dfc["materia_nombre"] = dfc["materia_id"].map(dict(zip(dm["id"], dm["nombre"]))).fillna(dfc["materia_id"].astype(str))
    dfc = dfc.merge(de[["id","alumno"]], left_on="estudiante_id", right_on="id", how="left")

    cplot, cside = st.columns([9, 3], gap="large")

    with cside:
        st.markdown("**Alumnos y calificación final**")
        q = st.text_input("Buscar alumno o materia", key="dist_q").strip()

    # Filtrado por el buscador que alimenta tabla y gráfica
    if q:
        qn = _norm(q)
        dfc = dfc[dfc.apply(
            lambda r: qn in _norm(r.get("alumno","")) or
                      qn in _norm(r.get("materia_nombre","")) or
                      str(r.get("estudiante_id","")) == q or
                      str(r.get("materia_id","")) == q,
            axis=1
        )]

    # Datos para histograma
    vals = pd.to_numeric(dfc["calificacion_final"], errors="coerce").dropna().clip(0, 100)
    bins = max(6, min(20, int(np.sqrt(vals.size)))) if vals.size else 6

    with cplot:
        fig, ax = plt.subplots(figsize=(9.6, 5.2), dpi=110, constrained_layout=True)
        
        # Obtener colores de daltonismo si está activo
        colores = obtener_colores_grafica(4)
        if colores:
            color_hist = colores[0]
            color_limite = colores[1]
            color_media = colores[2]
            color_mediana = colores[3]
        else:
            color_hist = "#4c78a8"
            color_limite = "#d62728"
            color_media = "#2ca02c"
            color_mediana = "#ff7f0e"
        
        if vals.size:
            ax.hist(
                vals, bins=bins, range=(0,100),
                histtype="bar", rwidth=1.0,
                color=color_hist, edgecolor="white", linewidth=0.6, alpha=0.95
            )
            ax.axvline(70, color=color_limite, linestyle="--", linewidth=1.6, label="Límite 70")
            media = float(vals.mean()); mediana = float(np.median(vals))
            ax.axvline(media,  color=color_media, linestyle=":",   linewidth=1.6, label=f"Media {media:.1f}")
            ax.axvline(mediana,color=color_mediana, linestyle="-.", linewidth=1.6, label=f"Mediana {mediana:.1f}")
            ax.set_xlim(0, 100)
            ax.set_xlabel("Calificación final")
            ax.set_ylabel("Frecuencia")
            ax.grid(axis="y", alpha=0.2)
            ax.legend(loc="upper left")
            
            # Aplicar colores de daltonismo a la figura
            aplicar_colores_figura(fig, ax)
        else:
            ax.text(0.5, 0.5, "Sin datos para el filtro", ha="center", va="center", transform=ax.transAxes)
        st.pyplot(fig, use_container_width=True)

# BUSCA ESTAS LÍNEAS en mostrar_distribucion_calificaciones:
    with cside:
        tabla = dfc[["estudiante_id","alumno","materia_nombre","calificacion_final"]].copy()
        if not tabla.empty:
            tabla = tabla.rename(columns={
                "estudiante_id": "ID",
                "alumno": "Alumno",
                "materia_nombre": "Materia",
                "calificacion_final": "Final"
            }).sort_values("Final", ascending=False, na_position="last")

            # << NUEVO: toggle para activar tabla accesible >>
            usar_accesible = st.toggle(
                "Tabla accesible para lectura",
                value=False,
                help="Activa lectura por celda y click-to-read",
                key="toggle_tabla_tts"
            )

            if usar_accesible:
                # TTS por celda (click-to-read)
                tabla_accesible(
                    tabla.reset_index(drop=True),
                    table_id="alumnos_tts",
                    caption="Alumnos con calificación final"
                )
            else:
                # Tabla normal
                st.dataframe(tabla, use_container_width=True, height=520, hide_index=True)

        else:
            st.info("Sin filas para mostrar.")


def grafica_asistencia_dashboard(analytics):
    """
    Promedio de asistencia por materia o por grupo.
    """
    

    df = analytics.df_calificaciones.copy()
    if df.empty or "asistencia" not in df.columns:
        st.info("No hay datos de asistencia")
        return

    try:
        dm = analytics.df_materias[["id", "nombre"]].copy()
    except Exception:
        dm = pd.DataFrame(columns=["id", "nombre"])
    map_mat = dict(zip(dm["id"], dm["nombre"]))

    try:
        de = analytics.df_estudiantes[["id", "nombres", "apellido_paterno", "apellido_materno"]].copy()
        de = de.fillna("")
        de["alumno"] = (de["nombres"].astype(str).str.strip() + " " +
                        de["apellido_paterno"].astype(str).str.strip() + " " +
                        de["apellido_materno"].astype(str).str.strip())
        # limpieza anti “nan”
        de["alumno"] = de["alumno"].str.replace("nan", "", case=False)
        de["alumno"] = de["alumno"].str.replace(r"\s+", " ", regex=True).str.strip()

    except Exception:
        de = pd.DataFrame(columns=["id", "alumno"])
        de["id"] = []
        de["alumno"] = []
    map_est = dict(zip(de["id"], de.get("alumno", de.get("nombre", de.get("nombres", "")))))

    modo = st.radio("Vista", ["Promedio por materia", "Alumnos de un grupo"],
                    horizontal=True, key="asis_modo")

    if modo == "Promedio por materia":
        g = df.groupby("materia_id", as_index=False)["asistencia"].mean()
        if g.empty:
            st.info("No hay datos para calcular promedios")
            return
        g["materia"] = g["materia_id"].map(map_mat).fillna(g["materia_id"].astype(str))
        g = g.sort_values("asistencia", ascending=False)

        fig, ax = plt.subplots(figsize=(9, 4), dpi=110, constrained_layout=True)
        
        # Obtener color de daltonismo si está activo
        colores = obtener_colores_grafica(1)
        color_bar = colores[0] if colores else "#1f77b4"
        
        ax.barh(g["materia"], g["asistencia"], color=color_bar)
        ax.invert_yaxis()
        ax.set_xlabel("Asistencia promedio")
        ax.set_xlim(0, 100)
        ax.grid(axis="x", alpha=0.2)
        for i, v in enumerate(g["asistencia"]):
            ax.text(min(v + 1, 100), i, f"{v:.0f}%", va="center")
        
        # Aplicar colores de daltonismo a la figura
        aplicar_colores_figura(fig, ax)
        st.pyplot(fig, use_container_width=True)

    else:
        mats_disp = sorted(df["materia_id"].dropna().unique().tolist())
        if not mats_disp:
            st.info("No hay materias con datos de asistencia")
            return

        opciones = [f"ID {int(m)}: {map_mat.get(int(m), 'Materia')}" for m in mats_disp]
        etiqueta = st.selectbox("Materia", opciones, key="asis_mat_sel")
        try:
            materia_id = int(etiqueta.split()[1].strip(":"))
        except Exception:
            materia_id = mats_disp[0]

        grupos = df[df["materia_id"] == materia_id][["periodo", "grupo"]].drop_duplicates()
        grp_labels = [f"{r.periodo}  {r.grupo}" for r in grupos.itertuples(index=False)]
        if not grp_labels:
            st.info("La materia no tiene grupos con datos")
            return
        grp_sel = st.selectbox("Grupo", grp_labels, key="asis_grp_sel")
        periodo = grp_sel.split()[0]
        grupo = grp_sel.split()[-1]

        dfg = df[(df["materia_id"] == materia_id) &
                 (df["periodo"] == periodo) &
                 (df["grupo"] == grupo)].copy()
        if dfg.empty:
            st.info("No hay alumnos con asistencia en ese grupo")
            return

        dfg["alumno"] = dfg["estudiante_id"].map(map_est).fillna(dfg["estudiante_id"].astype(str))
        dfg = dfg.sort_values("asistencia", ascending=True)

        fig, ax = plt.subplots(figsize=(9, 4.5), dpi=110, constrained_layout=True)
        
        # Obtener colores de daltonismo si está activo
        colores = obtener_colores_grafica(2)
        color_bar = colores[0] if colores else "#1f77b4"
        color_bajo = colores[1] if colores else "#e74c3c"
        
        bars = ax.barh(dfg["alumno"], dfg["asistencia"], color=color_bar)
        ax.set_xlabel(f"Asistencia del grupo  {periodo}  {grupo}")
        ax.set_xlim(0, 100)
        ax.grid(axis="x", alpha=0.2)
        for bar, v in zip(bars, dfg["asistencia"]):
            if v < 80:
                bar.set_color(color_bajo)
        
        # Aplicar colores de daltonismo a la figura
        aplicar_colores_figura(fig, ax)
        st.pyplot(fig, use_container_width=True)

        tabla = dfg[["estudiante_id", "alumno", "asistencia"]].rename(columns={"estudiante_id": "ID"})
        st.caption("Alumnos del grupo seleccionado")
        st.dataframe(tabla, use_container_width=True, height=280, hide_index=True)


def mostrar_tendencia_unidades(analytics):
    """Promedios por unidad con filtro de materia."""
    

    dfc = analytics.df_calificaciones
    if dfc.empty:
        st.info("No hay datos de unidades para mostrar")
        return

    dfm = analytics.df_materias.copy()
    opciones = {"Todas": None}
    for _, r in dfm.iterrows():
        opciones[f"ID {r['id']}: {r['nombre']}"] = int(r['id'])
    sel = st.selectbox("Materia", list(opciones.keys()), key="tend_materia_sel")
    materia_id = opciones[sel]

    data = dfc.copy()
    titulo = "Todas las materias"
    if materia_id is not None:
        data = data[data['materia_id'] == materia_id].copy()
        if not dfm.empty:
            nom = dfm[dfm['id'] == materia_id]
            if not nom.empty:
                titulo = nom.iloc[0]['nombre']

    unidades = ['u1', 'u2', 'u3']
    existentes = [u for u in unidades if u in data.columns]
    if len(existentes) == 0:
        st.info("No hay columnas de unidades")
        return

    proms = [data[u].mean() for u in existentes]
    fig, ax = plt.subplots(figsize=(7.5, 4), dpi=110, constrained_layout=True)
    
    # Obtener color de daltonismo si está activo
    colores = obtener_colores_grafica(1)
    color_bar = colores[0] if colores else "#1f77b4"
    
    ax.bar(existentes, proms, color=color_bar)
    ax.set_xlabel('Unidad')
    ax.set_ylabel('Calificación promedio')
    ax.set_title(f'Tendencia de Calificaciones por Unidad - {titulo}')
    ax.grid(True, alpha=0.1)
    for i, v in enumerate(proms):
        ax.text(i, v + 0.4, f'{v:.1f}', ha='center', va='bottom')
    
    # Aplicar colores de daltonismo a la figura
    aplicar_colores_figura(fig, ax)
    st.pyplot(fig, use_container_width=True)
