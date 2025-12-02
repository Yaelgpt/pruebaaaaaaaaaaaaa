# Investigación: Software de Calidad y Fuentes para Dislexia

## 1. Software para Medir Calidad de Software (Streamlit/Python)

### Herramientas Recomendadas:

#### 1.1 **SonarQube**
- **Descripción**: Plataforma de análisis estático de código que detecta bugs, vulnerabilidades y code smells
- **Compatibilidad**: Soporta Python y puede integrarse con proyectos Streamlit
- **Características**:
  - Análisis de código estático
  - Detección de bugs y vulnerabilidades
  - Métricas de calidad de código
  - Integración con CI/CD
- **Instalación**: Docker, servidor local o SonarCloud (SaaS)
- **URL**: https://www.sonarqube.org/

#### 1.2 **Pylint**
- **Descripción**: Linter para Python que verifica el código según estándares de estilo PEP 8
- **Compatibilidad**: Nativo para Python
- **Características**:
  - Verificación de estilo de código
  - Detección de errores
  - Análisis de complejidad
- **Instalación**: `pip install pylint`
- **Uso**: `pylint app.py components/ services/`

#### 1.3 **Flake8**
- **Descripción**: Herramienta que combina PyFlakes, pycodestyle y mccabe
- **Compatibilidad**: Nativo para Python
- **Características**:
  - Detección de errores de sintaxis
  - Verificación de estilo PEP 8
  - Análisis de complejidad ciclomática
- **Instalación**: `pip install flake8`
- **Uso**: `flake8 .`

#### 1.4 **Black**
- **Descripción**: Formateador de código Python
- **Compatibilidad**: Nativo para Python
- **Características**:
  - Formateo automático de código
  - Consistencia en estilo
- **Instalación**: `pip install black`
- **Uso**: `black .`

#### 1.5 **pytest**
- **Descripción**: Framework de testing para Python
- **Compatibilidad**: Nativo para Python
- **Características**:
  - Testing unitario
  - Testing de integración
  - Cobertura de código
- **Instalación**: `pip install pytest pytest-cov`
- **Uso**: `pytest --cov=. tests/`

#### 1.6 **Bandit**
- **Descripción**: Analizador de seguridad para código Python
- **Compatibilidad**: Nativo para Python
- **Características**:
  - Detección de vulnerabilidades de seguridad
  - Análisis de patrones inseguros
- **Instalación**: `pip install bandit`
- **Uso**: `bandit -r .`

#### 1.7 **mypy**
- **Descripción**: Verificador de tipos estático para Python
- **Compatibilidad**: Nativo para Python
- **Características**:
  - Verificación de tipos
  - Detección de errores de tipo antes de ejecución
- **Instalación**: `pip install mypy`
- **Uso**: `mypy .`

### Configuración Recomendada para el Proyecto:

```bash
# requirements-dev.txt
pylint>=2.15.0
flake8>=6.0.0
black>=23.0.0
pytest>=7.2.0
pytest-cov>=4.0.0
bandit>=1.7.0
mypy>=1.0.0
```

### Script de Análisis Completo:

```bash
#!/bin/bash
# analyze.sh

echo "Ejecutando análisis de calidad..."

echo "1. Formateando código con Black..."
black .

echo "2. Verificando estilo con Flake8..."
flake8 . --max-line-length=100 --exclude=.venv,__pycache__

echo "3. Analizando con Pylint..."
pylint app.py components/ services/ --max-line-length=100

echo "4. Verificando tipos con mypy..."
mypy . --ignore-missing-imports

echo "5. Analizando seguridad con Bandit..."
bandit -r . -f json -o bandit-report.json

echo "6. Ejecutando tests..."
pytest --cov=. --cov-report=html tests/

echo "Análisis completado!"
```

## 2. Tipografías para Dislexia

### Fuentes Recomendadas:

#### 2.1 **OpenDyslexic**
- **Descripción**: Fuente diseñada específicamente para personas con dislexia
- **Características**:
  - Letras con base pesada para evitar rotación
  - Formas únicas para cada letra
  - Mejora la legibilidad
- **Licencia**: Open Source (SIL Open Font License)
- **URL**: https://opendyslexic.org/
- **Uso en CSS**: `@import url('https://fonts.googleapis.com/css2?family=OpenDyslexic:wght@400;700&display=swap');`

#### 2.2 **Lexend**
- **Descripción**: Fuente diseñada para mejorar la velocidad de lectura
- **Características**:
  - Espaciado optimizado
  - Formas claras y distintivas
  - Múltiples pesos (300-800)
- **Licencia**: Open Source (SIL Open Font License)
- **URL**: https://www.lexend.com/
- **Uso en CSS**: `@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600&display=swap');`

#### 2.3 **Comic Neue**
- **Descripción**: Fuente sans-serif con formas amigables
- **Características**:
  - Formas redondeadas
  - Buena legibilidad
  - Estilo informal pero profesional
- **Licencia**: Open Source (SIL Open Font License)
- **URL**: https://comicneue.com/
- **Uso en CSS**: `@import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@400;700&display=swap');`

#### 2.4 **Dyslexie**
- **Descripción**: Fuente comercial diseñada específicamente para dislexia
- **Características**:
  - Letras con base pesada
  - Formas únicas
  - Investigación científica detrás
- **Licencia**: Comercial (requiere licencia)
- **URL**: https://www.dyslexiefont.com/

#### 2.5 **Sylexiad**
- **Descripción**: Fuente diseñada para lectores con dislexia
- **Características**:
  - Formas distintivas
  - Buena legibilidad
- **Licencia**: Comercial/Educativa
- **URL**: https://www.readregular.com/

### Mejores Prácticas para Tipografías en Dislexia:

1. **Espaciado entre letras**: 0.02em - 0.1em
2. **Espaciado entre palabras**: 0.1em - 0.2em
3. **Espaciado entre líneas (line-height)**: 1.5 - 2.5
4. **Tamaño de fuente**: Mínimo 14px, preferiblemente 16px o más
5. **Peso de fuente**: Regular (400) o Medium (500), evitar Light o Thin
6. **Evitar**: Fuentes decorativas, cursivas, o con serifas complejas

### Investigación Científica:

#### Estudios Relevantes:

1. **"The effect of font type on screen readability by people with dyslexia"** (2016)
   - Conclusión: Fuentes sans-serif con espaciado aumentado mejoran la legibilidad
   - Fuentes recomendadas: Arial, Verdana, Comic Sans

2. **"Dyslexia-friendly fonts: do they actually work?"** (2013)
   - Conclusión: El espaciado es más importante que la fuente específica
   - Recomendación: Aumentar espaciado entre letras y palabras

3. **"Typography for Children May Be Inappropriately Designed"** (2010)
   - Conclusión: Fuentes más grandes y con mayor espaciado mejoran la lectura
   - Recomendación: Tamaño mínimo 14pt, line-height 1.5-2.0

### Implementación en el Proyecto:

El proyecto ya implementa:
- ✅ Fuente Lexend (recomendada para dislexia)
- ✅ Ajuste de espaciado entre letras (letter-spacing)
- ✅ Ajuste de espaciado entre palabras (word-spacing)
- ✅ Ajuste de espaciado entre líneas (line-height)
- ✅ Tamaño de texto ajustable

## 3. Recursos Adicionales

### Estándares de Accesibilidad:

- **WCAG 2.1** (Web Content Accessibility Guidelines)
  - Nivel AA recomendado para proyectos educativos
  - URL: https://www.w3.org/WAI/WCAG21/quickref/

- **Section 508** (Estándar de accesibilidad para gobierno de EE.UU.)
  - Aplicable si el proyecto recibe fondos gubernamentales

### Herramientas de Testing de Accesibilidad:

1. **WAVE** (Web Accessibility Evaluation Tool)
   - URL: https://wave.webaim.org/
   - Extensión de navegador disponible

2. **axe DevTools**
   - URL: https://www.deque.com/axe/devtools/
   - Extensión de navegador para Chrome/Firefox

3. **Lighthouse** (Google)
   - Incluido en Chrome DevTools
   - Incluye auditoría de accesibilidad

### Referencias:

1. Rello, L., & Baeza-Yates, R. (2013). "Good fonts for dyslexia"
2. Wery, J. J., & Diliberto, J. A. (2016). "The effect of font type on screen readability"
3. British Dyslexia Association. "Dyslexia Style Guide"
4. WebAIM. "Typefaces and Fonts"

## 4. Recomendaciones para el Proyecto

### Implementación Inmediata:

1. ✅ **TTS mejorado** - Implementado con descripciones de gráficos, botones y menús
2. ✅ **Tipografías para dislexia** - Implementado con Lexend y ajustes de espaciado
3. ✅ **Modo oscuro/claro** - Implementado
4. ✅ **Alto contraste** - Implementado
5. ✅ **Modo daltonismo** - Implementado (protanopia, deuteranopia, tritanopia)
6. ✅ **Modo concentración** - Implementado con icono
7. ✅ **Configuración por usuario** - Implementado con guardado en base de datos
8. ✅ **Tamaño de texto en login** - Implementado

### Próximos Pasos:

1. **Testing de Accesibilidad**:
   - Ejecutar WAVE en todas las páginas
   - Verificar con lectores de pantalla (NVDA, JAWS)
   - Probar con usuarios reales con dislexia

2. **Análisis de Calidad de Código**:
   - Configurar SonarQube o usar herramientas locales
   - Ejecutar análisis regularmente
   - Integrar en CI/CD si está disponible

3. **Documentación**:
   - Crear guía de usuario para funciones de accesibilidad
   - Documentar cómo usar cada modo
   - Proporcionar ejemplos de uso

4. **Mejoras Continuas**:
   - Recopilar feedback de usuarios
   - Ajustar configuraciones según necesidades
   - Agregar más opciones de personalización si es necesario

