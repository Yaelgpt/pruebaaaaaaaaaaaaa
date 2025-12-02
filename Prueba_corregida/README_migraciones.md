
# Correcciones incluidas

Estas son las mejoras aplicadas al proyecto

1. Niveles de acceso admin y docente con campo `usuarios.rol`. Docente ve solo sus grupos y datos asociados cuando se configure RLS en Supabase.  
2. Columna de asistencia mediante tabla `asistencias` y vista `asistencia_resumen`  
3. Etiquetas de materia en gráficas de barras y filtros de materia para histograma y gráfico de control  
4. Edición de datos en página de registro con `st.data_editor` y métodos `actualizar_*`  
5. Filtros por materia en el análisis y control de reprobados con métricas visibles  
6. Validación de datos al registrar e importar. Nombres sin números y limpieza de texto  
7. Separación de nombres, apellido paterno y materno con nuevo índice único para evitar duplicados  
8. Evitar duplicidad al importar gracias a índice único y lógica de `importar_estudiantes_validando`  
9. Filtro para factores vía SQL y front. Índice único razonable  
10. Auto actualizaciones posibles con `st.rerun` o `st_autorefresh` a añadir donde se requiera
11. **Sistema completo de accesibilidad** con TTS mejorado, modo oscuro/claro, daltonismo, tipografías para dislexia, modo concentración y configuración por usuario

## Cómo aplicar

### Migración Base (2025-11-09)
1. En Supabase ejecuta el archivo `.streamlit/migrations_20251109.sql`  
2. Reinicia tu app de Streamlit  
3. Verifica creación de al menos una materia, un profesor y asignar profesor a usuario  
4. Crea grupos con materia y periodo. Inscribe estudiantes y registra calificaciones

### Migración de Accesibilidad (2025-01-XX)
1. En Supabase ejecuta el archivo `.streamlit/migration_accesibilidad.sql`
2. Reinicia tu app de Streamlit
3. Las configuraciones de accesibilidad se guardarán automáticamente por usuario
4. Accede al panel de accesibilidad desde el sidebar para configurar tus preferencias

## Notas

- Si ya tienes tablas con datos activa RLS con cuidado. Las políticas están comentadas
- El módulo `services/validators.py` centraliza validaciones
- Para asistencia usa `DatabaseService.registrar_asistencia` y muestra `asistencia_resumen` en tus tablas
- El módulo `components/accesibilidad.py` contiene todas las funcionalidades de accesibilidad
- Las configuraciones de accesibilidad se guardan en la tabla `configuracion_accesibilidad` por usuario
