# 📋 Guía de Instalación - Sistema de Análisis Educativo

## ⚠️ IMPORTANTE: Versión de Python

**NO uses Python 3.14** - Esta versión es muy reciente y tiene incompatibilidades con Streamlit y protobuf.

### ✅ Versiones Recomendadas:
- **Python 3.11** (recomendado)
- **Python 3.12** (también funciona bien)

### ❌ Versiones NO Compatibles:
- Python 3.14 (causa error: `TypeError: Metaclasses with custom tp_new are not supported`)

---

## 🚀 Instalación Paso a Paso

### 1. Verificar Versión de Python

Abre una terminal y ejecuta:

```bash
python --version
```

**Debe mostrar:** `Python 3.11.x` o `Python 3.12.x`

Si tienes Python 3.14, necesitas instalar una versión compatible:

#### Windows:
1. Descarga Python 3.11 desde: https://www.python.org/downloads/
2. Durante la instalación, marca la opción "Add Python to PATH"
3. Verifica con `python --version`

#### Mac/Linux:
```bash
# Usando pyenv (recomendado)
pyenv install 3.11.9
pyenv local 3.11.9
```

---

### 2. Crear Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

---

### 3. Instalar Dependencias

```bash
# Instalar todas las dependencias
pip install -r requirements.txt
```

Si no tienes el archivo `requirements.txt`, instala manualmente:

```bash
pip install streamlit>=1.28.0
pip install pandas>=2.0.0
pip install numpy>=1.24.0
pip install matplotlib>=3.7.0
pip install supabase>=2.0.0
pip install reportlab>=4.0.0
pip install streamlit-autorefresh>=0.0.6
pip install gtts>=2.4.0
pip install pygame>=2.5.0
pip install python-dotenv>=1.0.0
```

---

### 4. Configurar Variables de Entorno

Crea un archivo `.streamlit/secrets.toml` con tus credenciales de Supabase:

```toml
SUPABASE_URL = "tu_url_de_supabase"
SUPABASE_KEY = "tu_key_de_supabase"
```

**O** configura variables de entorno:

```bash
# Windows (PowerShell)
$env:SUPABASE_URL="tu_url"
$env:SUPABASE_KEY="tu_key"

# Mac/Linux
export SUPABASE_URL="tu_url"
export SUPABASE_KEY="tu_key"
```

---

### 5. Ejecutar la Aplicación

```bash
streamlit run app.py
```

---

## 🔧 Solución de Problemas

### Error: `TypeError: Metaclasses with custom tp_new are not supported`

**Causa:** Estás usando Python 3.14

**Solución:**
1. Instala Python 3.11 o 3.12
2. Crea un nuevo entorno virtual con esa versión
3. Reinstala las dependencias

### Error: `ModuleNotFoundError: No module named 'streamlit'`

**Solución:**
```bash
pip install -r requirements.txt
```

### Error: `No module named 'supabase'`

**Solución:**
```bash
pip install supabase
```

### Error: `SUPABASE_URL y SUPABASE_KEY no encontrados`

**Solución:**
1. Crea el archivo `.streamlit/secrets.toml`
2. O configura las variables de entorno (ver paso 4)

---

## 📦 Dependencias Principales

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| streamlit | >=1.28.0 | Framework web |
| pandas | >=2.0.0 | Análisis de datos |
| numpy | >=1.24.0 | Cálculos numéricos |
| matplotlib | >=3.7.0 | Gráficos |
| supabase | >=2.0.0 | Base de datos |
| reportlab | >=4.0.0 | Generación de PDFs |
| gtts | >=2.4.0 | Text-to-Speech |
| pygame | >=2.5.0 | Audio para TTS |

---

## 💡 Consejos

1. **Siempre usa un entorno virtual** para evitar conflictos entre proyectos
2. **Verifica la versión de Python** antes de instalar dependencias
3. **Mantén las dependencias actualizadas** pero evita versiones muy nuevas que puedan romper compatibilidad
4. **Lee los mensajes de error** - suelen indicar qué falta o qué está mal configurado

---

## 🆘 ¿Necesitas Ayuda?

Si después de seguir estos pasos aún tienes problemas:

1. Verifica que estás usando Python 3.11 o 3.12
2. Asegúrate de tener todas las dependencias instaladas
3. Revisa que las credenciales de Supabase estén correctas
4. Comparte el mensaje de error completo para diagnóstico

