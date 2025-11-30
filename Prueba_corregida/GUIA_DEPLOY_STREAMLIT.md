# Guía de Deploy en Streamlit Community Cloud

## Requisitos Previos

### 1. Cuenta en GitHub
- Necesitas una cuenta en [GitHub](https://github.com)
- Tu código debe estar en un repositorio (público o privado)

### 2. Cuenta en Streamlit Cloud
- Regístrate en [share.streamlit.io](https://share.streamlit.io)
- Puedes usar tu cuenta de GitHub para registrarte

---

## Archivos Necesarios para el Deploy

Tu proyecto ya tiene los archivos necesarios:

### ✅ `requirements.txt` (YA EXISTE)
```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
supabase>=2.0.0
reportlab>=4.0.0
streamlit-autorefresh>=0.0.6
gtts>=2.4.0
pygame>=2.5.0
python-dotenv>=1.0.0
```

### ✅ `app.py` (YA EXISTE)
- Archivo principal de la aplicación

### ✅ `.streamlit/secrets.toml` (YA EXISTE - NO SUBIR A GITHUB)
- Contiene las credenciales de Supabase

---

## Pasos para el Deploy

### Paso 1: Preparar el Repositorio en GitHub

1. **Crear repositorio en GitHub:**
   ```bash
   # En tu terminal, dentro de la carpeta del proyecto
   git init
   git add .
   git commit -m "Initial commit - Sistema de Análisis Educativo"
   ```

2. **Crear archivo `.gitignore`** (IMPORTANTE - para no subir secretos):
   ```
   # .gitignore
   .streamlit/secrets.toml
   __pycache__/
   *.pyc
   .env
   .venv/
   venv/
   *.log
   ```

3. **Subir a GitHub:**
   ```bash
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   git branch -M main
   git push -u origin main
   ```

### Paso 2: Configurar Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)

2. Haz clic en **"New app"**

3. Completa los campos:
   - **Repository:** `TU_USUARIO/TU_REPOSITORIO`
   - **Branch:** `main`
   - **Main file path:** `app.py`

4. Haz clic en **"Advanced settings"**

### Paso 3: Configurar Secrets (MUY IMPORTANTE)

En **"Advanced settings"** → **"Secrets"**, pega:

```toml
ADMIN_SEED = "TuClaveSuperSegura123"
SUPABASE_URL = "https://sfnsazqplqdbxauivxce.supabase.co"
SUPABASE_KEY = "tu_supabase_key_aqui"
```

⚠️ **NUNCA subas secrets.toml a GitHub** - Usa los secrets de Streamlit Cloud

### Paso 4: Deploy

1. Haz clic en **"Deploy!"**
2. Espera 2-5 minutos mientras se construye la app
3. Tu app estará disponible en: `https://tu-app.streamlit.app`

---

## Estructura del Proyecto para Deploy

```
tu-repositorio/
├── app.py                    # Archivo principal ✅
├── requirements.txt          # Dependencias ✅
├── .gitignore               # Excluir secretos ⚠️ CREAR
├── components/
│   ├── __init__.py
│   ├── accesibilidad.py
│   ├── analisis_calidad.py
│   ├── dashboard.py
│   ├── exportacion.py
│   ├── login.py
│   └── registro_datos.py
├── services/
│   ├── __init__.py
│   ├── analytics.py
│   ├── auth_service.py
│   ├── database.py
│   └── rbac.py
├── config/
│   ├── __init__.py
│   └── constants.py
└── .streamlit/
    └── config.toml          # Opcional - configuración de tema
```

---

## Crear archivo .gitignore

Crea este archivo en la raíz del proyecto:

```gitignore
# Secrets - NUNCA subir
.streamlit/secrets.toml
.env
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Logs
*.log

# OS
.DS_Store
Thumbs.db
```

---

## Configuración Opcional: Tema de Streamlit

Crea `.streamlit/config.toml` (este SÍ se puede subir):

```toml
[theme]
primaryColor = "#1f3a60"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

---

## Comandos Rápidos

```bash
# 1. Crear .gitignore
echo ".streamlit/secrets.toml" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore

# 2. Inicializar git
git init

# 3. Agregar archivos
git add .

# 4. Verificar que secrets.toml NO esté incluido
git status

# 5. Commit
git commit -m "Sistema de Análisis Educativo - ITT"

# 6. Conectar con GitHub (reemplaza con tu repo)
git remote add origin https://github.com/TU_USUARIO/sistema-analisis-educativo.git

# 7. Push
git push -u origin main
```

---

## Solución de Problemas Comunes

### Error: "No module named 'xxx'"
- Verifica que el paquete esté en `requirements.txt`

### Error: "Secrets not found"
- Configura los secrets en Streamlit Cloud (Advanced settings)

### Error: "Connection refused" (Supabase)
- Verifica que SUPABASE_URL y SUPABASE_KEY estén en Secrets

### La app tarda mucho en cargar
- Streamlit Cloud tiene un "cold start" de ~1 minuto si no se usa

### Error de memoria
- Streamlit Cloud tiene límite de 1GB RAM en plan gratuito

---

## URLs Importantes

- **Streamlit Cloud:** https://share.streamlit.io
- **Documentación:** https://docs.streamlit.io/streamlit-community-cloud
- **GitHub:** https://github.com
- **Supabase:** https://supabase.com

---

## Checklist Final

- [ ] Código en GitHub
- [ ] `.gitignore` creado (secrets.toml excluido)
- [ ] `requirements.txt` actualizado
- [ ] Secrets configurados en Streamlit Cloud
- [ ] App desplegada y funcionando
- [ ] Probar login y funcionalidades

---

*Guía creada para Sistema de Análisis Educativo - ITT*


