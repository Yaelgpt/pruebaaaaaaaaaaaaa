# Documentación de Accesibilidad
## Sistema de Análisis Educativo - ITT

**Fecha:** Noviembre 2024  
**Versión:** 1.0

---

## 1. Funciones de Accesibilidad Implementadas

### 1.1 Texto a Voz (TTS - Text-to-Speech)

| Función | Descripción |
|---------|-------------|
| `leer_contenido()` | Lee texto en voz alta usando Web Speech API del navegador |
| `crear_boton_lectura()` | Crea botones "🔊 Leer" para elementos específicos |
| `leer_tabla_si_activo()` | Lee contenido de tablas de datos |
| `leer_todo_contenido_pagina()` | Lee todo el contenido de la página actual |
| `leer_dashboard_automatico()` | Lee métricas y gráficas del dashboard |
| `leer_contenido_analisis_calidad()` | Lee análisis estadísticos |
| `detener_lectura()` | Detiene la síntesis de voz |

**Características:**
- Velocidad ajustable (0.5x - 2.0x)
- Selección de voz/idioma (Español España, Español Latinoamérica, Inglés)
- Botón de prueba de voz
- Botón "Leer todo" para contenido completo
- Lectura automática de cambios de navegación

---

### 1.2 Modos Visuales

#### 1.2.1 Modo Oscuro
**Función:** `_css_modo_oscuro()`

- Fondo oscuro (#1a1a2e) para reducir fatiga visual
- Texto claro (#e0e0e0) con alto contraste
- Sidebar con fondo más oscuro (#16213e)
- Ideal para uso nocturno o sensibilidad a la luz

#### 1.2.2 Alto Contraste
**Función:** `_css_contraste_alto()`

- Fondo blanco puro (#FFFFFF)
- Texto negro puro (#000000)
- Bordes definidos y visibles
- Para usuarios con baja visión

#### 1.2.3 Modos para Daltonismo
**Función:** `_css_daltonismo(tipo)`

| Tipo | Descripción | Colores Usados |
|------|-------------|----------------|
| **Protanopia** | Dificultad con rojos | Azules (#0066CC) y Amarillos (#FFD700) |
| **Deuteranopia** | Dificultad con verdes | Azules (#0055AA) y Naranjas (#FF6600) |
| **Tritanopia** | Dificultad con azules | Rojos (#CC3300) y Verdes (#009933) |

**Elementos afectados:**
- Sidebar completo (fondo y texto)
- Botones y controles
- Alertas (success, warning, error, info)
- Tablas (encabezados y filas alternadas)
- Gráficas de matplotlib (barras, líneas, scatter)
- Botón de colapsar sidebar
- Checkboxes, radio buttons, sliders
- Métricas y cards

---

### 1.3 Tipografía para Dislexia
**Función:** `_css_dyslexia()`

**Características:**
- Fuente OpenDyslexic (específica para dislexia)
- Fallback a Arial, sans-serif
- Espaciado entre letras ajustable (0 - 0.1em)
- Espaciado entre palabras ajustable (0 - 0.5em)
- Altura de línea ajustable (1.0 - 2.5)

---

### 1.4 Escalado de Texto
**Función:** `_css_base(text_scale)`

- Rango: 80% - 150%
- Aplica a todo el contenido
- Configuración separada para pantalla de login
- Preserva proporciones de la interfaz

---

### 1.5 Modo Concentración/Enfoque
**Función:** `_css_modo_enfoque()`

- Reduce distracciones visuales
- Atenúa sidebar (grayscale + opacity)
- Centra el contenido principal
- Ideal para usuarios con TDAH

---

### 1.6 Resaltado de Foco
**Función:** `_css_resaltar_focus()`

- Anillo visible (#ffbf47) al navegar con teclado
- Sombra de enfoque para mayor visibilidad
- Facilita navegación sin ratón

---

### 1.7 Persistencia de Configuración

**Funciones:**
- `cargar_configuracion_usuario()` - Carga desde base de datos
- `guardar_configuracion_usuario()` - Guarda en base de datos

**Tabla en Supabase:** `configuracion_accesibilidad`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| usuario_id | int | ID del usuario |
| tts_activo | boolean | TTS habilitado |
| tts_velocidad | float | Velocidad de voz |
| tts_voz | string | Idioma de voz |
| modo_oscuro | boolean | Modo oscuro activo |
| alto_contraste | boolean | Alto contraste activo |
| modo_daltonismo | string | Tipo de daltonismo |
| tamanio_texto | int | Escala de texto % |
| fuente_dislexia | boolean | Fuente OpenDyslexic |
| espaciado_letras | float | Espaciado letras |
| espaciado_palabras | float | Espaciado palabras |
| espaciado_lineas | float | Altura de línea |
| modo_concentracion | boolean | Modo enfoque |
| resaltar_focus | boolean | Resaltar foco teclado |

---

## 2. Por Qué Se Eligieron Estas Funciones

### 2.1 TTS (Texto a Voz)
**Justificación:**
- Usuarios con discapacidad visual necesitan acceso auditivo
- Usuarios con dislexia se benefician de escuchar mientras leen
- Cumple con WCAG 2.1 - Principio 1 (Perceptible)

### 2.2 Modos de Daltonismo
**Justificación:**
- 8% de hombres y 0.5% de mujeres tienen algún tipo de daltonismo
- Las gráficas educativas dependen fuertemente del color
- Sin adaptación, información crítica se pierde

### 2.3 Tipografía para Dislexia
**Justificación:**
- 10-15% de la población tiene dislexia
- OpenDyslexic reduce errores de lectura en estudios
- El espaciado adicional facilita seguimiento de líneas

### 2.4 Modo Oscuro
**Justificación:**
- Reduce fatiga visual en uso prolongado
- Beneficia usuarios con fotofobia
- Ahorra batería en pantallas OLED

### 2.5 Escalado de Texto
**Justificación:**
- Usuarios con baja visión requieren texto más grande
- WCAG 2.1 requiere zoom hasta 200% sin pérdida de funcionalidad

### 2.6 Persistencia por Usuario
**Justificación:**
- Cada usuario tiene necesidades diferentes
- Evita reconfigurar en cada sesión
- Mejora experiencia de usuario

---

## 3. Cómo Se Probaron

### 3.1 Pruebas de TTS
| Prueba | Método | Resultado |
|--------|--------|-----------|
| Síntesis de voz | Botón "Probar" en panel | ✅ Funciona en Chrome, Edge, Firefox |
| Lectura de tablas | Activar TTS y navegar tablas | ✅ Lee filas y columnas |
| Detener lectura | Botón "Detener" | ✅ Cancela síntesis inmediatamente |
| Cambio de velocidad | Slider de velocidad | ✅ Ajusta correctamente |

### 3.2 Pruebas de Modos Visuales
| Prueba | Método | Resultado |
|--------|--------|-----------|
| Modo oscuro | Toggle en panel | ✅ Aplica a toda la interfaz |
| Alto contraste | Toggle en panel | ✅ Máximo contraste |
| Daltonismo | Selector de tipo | ✅ Colores cambian globalmente |
| Gráficas daltonismo | Generar gráficas con modo activo | ✅ Barras y líneas usan paleta accesible |

### 3.3 Pruebas de Tipografía
| Prueba | Método | Resultado |
|--------|--------|-----------|
| Fuente dislexia | Activar checkbox | ✅ OpenDyslexic se aplica |
| Espaciado | Ajustar sliders | ✅ Espaciado se modifica en tiempo real |
| Escalado texto | Slider de tamaño | ✅ Texto escala correctamente |

### 3.4 Pruebas de Persistencia
| Prueba | Método | Resultado |
|--------|--------|-----------|
| Guardar config | Cambiar opciones, cerrar sesión, volver a entrar | ✅ Configuración preservada |
| Multi-usuario | Probar con diferentes usuarios | ✅ Cada usuario tiene su config |

### 3.5 Pruebas en Login
| Prueba | Método | Resultado |
|--------|--------|-----------|
| Accesibilidad sin sesión | Activar opciones en login | ✅ Funciona antes de autenticarse |
| Daltonismo en login | Cambiar modo | ✅ Colores cambian |
| Tamaño texto login | Ajustar slider | ✅ Texto escala |

---

## 4. Resultados

### 4.1 Métricas de Implementación
- **Total de funciones de accesibilidad:** 26+
- **Líneas de código CSS:** ~1500
- **Modos de daltonismo:** 3 (Protanopia, Deuteranopia, Tritanopia)
- **Opciones configurables:** 14

### 4.2 Cobertura
| Área | Cobertura |
|------|-----------|
| Dashboard | ✅ Completa |
| Análisis de Calidad | ✅ Completa |
| Registro de Datos | ✅ Completa |
| Exportar Reportes | ✅ Completa |
| Login | ✅ Completa |
| Sidebar | ✅ Completa |
| Gráficas matplotlib | ✅ Completa |
| Tablas | ✅ Completa |
| Alertas/Notificaciones | ✅ Completa |

### 4.3 Compatibilidad de Navegadores
| Navegador | TTS | Modos Visuales |
|-----------|-----|----------------|
| Chrome | ✅ | ✅ |
| Edge | ✅ | ✅ |
| Firefox | ✅ | ✅ |
| Safari | ⚠️ Parcial | ✅ |

---

## 5. Mejoras Pendientes

### 5.1 Alta Prioridad
| Mejora | Descripción | Complejidad |
|--------|-------------|-------------|
| Navegación por teclado | Atajos de teclado para acciones comunes | Media |
| ARIA labels | Etiquetas descriptivas para lectores de pantalla | Media |
| Skip links | Enlaces para saltar navegación | Baja |

### 5.2 Media Prioridad
| Mejora | Descripción | Complejidad |
|--------|-------------|-------------|
| Subtítulos automáticos | Para contenido multimedia futuro | Alta |
| Modo alto contraste inverso | Fondo negro, texto blanco | Baja |
| Animaciones reducidas | Para usuarios con sensibilidad al movimiento | Media |

### 5.3 Baja Prioridad
| Mejora | Descripción | Complejidad |
|--------|-------------|-------------|
| Temas personalizados | Permitir colores personalizados | Alta |
| Exportar configuración | Backup de preferencias | Baja |
| Perfiles de accesibilidad | Configuraciones predefinidas | Media |

---

## 6. Cumplimiento de Estándares

### WCAG 2.1 - Nivel AA
| Criterio | Estado | Notas |
|----------|--------|-------|
| 1.1.1 Contenido no textual | ⚠️ Parcial | Falta alt en algunas imágenes |
| 1.3.1 Info y relaciones | ✅ | Estructura semántica correcta |
| 1.4.1 Uso del color | ✅ | Daltonismo implementado |
| 1.4.3 Contraste mínimo | ✅ | Alto contraste disponible |
| 1.4.4 Redimensionar texto | ✅ | Escalado hasta 150% |
| 2.1.1 Teclado | ⚠️ Parcial | Navegación básica funciona |
| 2.4.1 Evitar bloques | ⚠️ Pendiente | Skip links pendientes |
| 3.1.1 Idioma de la página | ✅ | Español configurado |

---

## 7. Tecnologías Utilizadas

- **Framework:** Streamlit 1.28+
- **TTS:** Web Speech API (navegador)
- **Fuentes:** OpenDyslexic, Google Fonts
- **Gráficas:** Matplotlib con paletas accesibles
- **Persistencia:** Supabase (PostgreSQL)
- **Estilos:** CSS inyectado dinámicamente

---

## 8. Archivos Relevantes

```
components/
├── accesibilidad.py      # Módulo principal de accesibilidad (~2100 líneas)
├── login.py              # Accesibilidad en pantalla de login
├── dashboard.py          # Integración con dashboard
└── analisis_calidad.py   # Gráficas con colores accesibles

app.py                    # Aplicación principal con panel de accesibilidad
```

---

## 9. Contacto y Soporte

Para reportar problemas de accesibilidad o sugerir mejoras:
- Abrir issue en el repositorio
- Contactar al equipo de desarrollo

---

*Documento generado automáticamente - Sistema de Análisis Educativo ITT*

