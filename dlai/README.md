# Gatorade AB Testing Dashboard

Una aplicación completa que combina un dashboard de métricas con un chatbot inteligente para análisis de datos avanzado.

## 🚀 Características

### Frontend (React + TypeScript)
- ✅ Dashboard interactivo con métricas y gráficos
- ✅ Interfaz de chat integrada con el asistente IA
- ✅ Componentes UI responsive (shadcn/ui)
- ✅ Filtros dinámicos y visualizaciones

### Backend (Flask + Python)
- ✅ API REST para el chatbot
- ✅ **Memoria conversacional por sesión**
- ✅ **Embeddings semánticos para conceptos de negocio**
- ✅ Cache inteligente con similitud semántica
- ✅ Análisis de datos con DuckDB
- ✅ Respuestas estructuradas con insights de negocio

### Chatbot IA Avanzado
- 🤖 **Conversaciones contextuales** - Mantiene memoria entre preguntas
- 🧠 **Embeddings semánticos** - Entiende sinónimos y conceptos similares
- ⚡ **Cache inteligente** - Reutiliza respuestas similares
- 📊 **Análisis real de datos** - Conectado a base de datos de tiendas
- 🔍 **SQL transparente** - Muestra las consultas ejecutadas

## 🚀 Quick Start

### Prerequisitos
- Docker y Docker Compose instalados
- Una API key de OpenAI

### Configuración inicial
1. **Clonar el repositorio**
   ```bash
   git clone <tu-repo-url>
   cd dlai
   ```

2. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   ```
   Luego edita `.env` y agrega tu OpenAI API key:
   ```bash
   OPENAI_API_KEY=your-actual-openai-api-key-here
   ```

3. **Levantar la aplicación**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

4. **Acceder a la aplicación**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000

¡Listo! La aplicación debería estar funcionando.

## 🐳 Desarrollo Local con Docker

### Opción 1: Desarrollo completo
```bash
# Levantar toda la aplicación
docker-compose -f docker-compose.dev.yml up --build

# Acceder a:
# Frontend: http://localhost:5173 (con hot reload)
# Backend API: http://localhost:5000
```

### Opción 2: Solo backend (para desarrollo frontend local)
```bash
# Solo el backend
docker-compose -f docker-compose.dev.yml up backend-dev

# Luego en otra terminal para frontend:
cd frontend
npm install
npm run dev
```

### Opción 3: Producción local
```bash
# Build y deploy completo
docker-compose up --build

# Acceder a:
# Aplicación completa: http://localhost:3000
```

## 🛠️ Desarrollo Manual (sin Docker)

### Backend
```bash
# Activar entorno virtual
source new_cb/bin/activate

# Instalar dependencias
pip install -r backend/requirements.txt

# Verificar que .env esté configurado con tu OpenAI API key
cat .env

# Ejecutar backend
python backend/app.py
```

### Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Desarrollo
npm run dev

# Build para producción
npm run build
```

## 📊 Funcionalidades del Chatbot

### Ejemplos de Conversaciones
```
👤 "¿Cuántas tiendas tenemos por región?"
🤖 [Ejecuta SQL y muestra datos por región]

👤 "¿Cuál región tiene mejor conversión?"
🤖 [Analiza conversiones por región del contexto anterior]

👤 "Muéstrame las top 5 tiendas de esa región"
🤖 [Entiende "esa región" del contexto previo]

👤 "¿Qué tipo de tienda te mencioné anteriormente?"
🤖 "En la conversación anterior no mencionaste tipos de tienda..."
```

### Memoria Conversacional Inteligente
- ✅ Mantiene contexto entre preguntas de seguimiento
- ✅ Detecta referencias a conversaciones anteriores
- ✅ Responde honestamente cuando no hay contexto
- ✅ Maneja hasta 10 turnos de conversación por sesión

### Embeddings Semánticos
- ✅ "rendimiento por zona geográfica" → "performance por región"
- ✅ "mejores formatos de local" → "mejor tipo de tienda"
- ✅ "resultados del test A/B" → "impacto del experimento"

## 🔧 Configuración

### Variables de Entorno (.env)
```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Chatbot Configuration
SIMILARITY_THRESHOLD=0.85
MAX_RESULTS=10
TEMPERATURE=0.1

# Session Memory Configuration
MAX_MEMORY_TURNS=10
ENABLE_SESSION_MEMORY=true

# Development Settings
DEBUG=true
```

### Estructura de Archivos
```
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API integration
│   │   └── hooks/          # Custom React hooks
│   ├── package.json
│   └── vite.config.ts
├── modern_chatbot.py       # Advanced chatbot engine
├── docker-compose.yml      # Production Docker setup
├── docker-compose.dev.yml  # Development Docker setup
├── tiendas_detalle.csv     # Sample store data
└── maestro_tiendas.csv     # Store master data
```

## 🚀 Despliegue en la Nube

### Para AWS/GCP/Azure
1. **Usar Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **O contenedores separados**:
   ```bash
   # Backend
   docker build -f Dockerfile.backend -t gatorade-backend .
   
   # Frontend  
   docker build -f Dockerfile.frontend -t gatorade-frontend .
   ```

### Para Heroku
```bash
# Usar el backend Flask directamente
git subtree push --prefix=backend heroku main
```

### Para Vercel (Frontend) + Railway (Backend)
- Frontend: Deploy desde `frontend/` a Vercel
- Backend: Deploy desde root a Railway con `Dockerfile.backend`

## 🔍 API Endpoints

### Chat API
- `POST /api/chat/start` - Iniciar sesión de chat
- `POST /api/chat/message` - Enviar mensaje
- `GET /api/chat/history/{session_id}` - Obtener historial

### Analytics API
- `GET /api/analytics/sessions` - Estadísticas de sesiones
- `GET /api/data/summary` - Resumen de datos disponibles
- `GET /api/health` - Health check

## 🧪 Testing del Chatbot

### Casos de Prueba
```bash
# Conversaciones básicas
python test_interactive.py

# Follow-up questions
python test_follow_up.py

# Meta-questions
python test_meta_questions.py

# Demo completo
python modern_chatbot.py
```

## 🎯 Próximas Mejoras

- [ ] Autenticación de usuarios
- [ ] Persistencia de sesiones en Redis
- [ ] Métricas avanzadas con Prometheus
- [ ] Tests automatizados
- [ ] CI/CD pipeline
- [ ] Websockets para chat en tiempo real

## 📞 Soporte

Para cualquier pregunta sobre el setup o deployment, consultar la documentación en `/frontend/guidelines/` o revisar los logs de Docker.

---

**¡El chatbot está listo para revolucionar el análisis de datos en Gatorade!** 🥤⚡