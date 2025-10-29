# DianaBot - Sistema Narrativo Gamificado para Telegram

DianaBot es un sistema integral que combina tres módulos interconectados: **Narrativa Inmersiva**, **Gamificación** y **Administración de Canales**, diseñados para ofrecer una experiencia interactiva, personalizada y gamificada en un entorno narrativo atractivo, con un enfoque emocional, psicológico y erótico.

## 🌟 Características Principales

### 1. Narrativa Inmersiva
- **Historia ramificada**: Decisiones que alteran el rumbo de la narrativa
- **Personajes carismáticos**: Lucien (mayordomo) y Diana (musa enigmática)
- **Niveles de acceso**: Contenido gratuito (niveles 1-3) y VIP (niveles 4-6)
- **Sistema de desbloqueos**: Basado en besitos, items y logros

### 2. Sistema de Gamificación
- **Economía interna**: Moneda de "besitos" para recompensar interacción
- **Misiones diarias/semanales**: Actividades para ganar besitos
- **Inventario (mochila)**: Almacenamiento de items coleccionables
- **Logros y recompensas**: Sistemas de reconocimiento
- **Subastas y trivias**: Eventos interactivos

### 3. Administración de Canales
- **Gestión VIP**: Acceso restringido por suscripción
- **Publicaciones programadas**: Contenido automatizado
- **Moderación avanzada**: Control de usuarios y contenido
- **Integración con narrativa**: Contenido exclusivo para VIP

## 🛠️ Arquitectura Técnica

### Stack Tecnológico
- **Backend**: Python 3.11+
- **Bot Framework**: python-telegram-bot 20.x
- **Web Framework**: FastAPI
- **Base de Datos Principal**: PostgreSQL 15+ (datos relacionales)
- **Base de Datos Flexible**: MongoDB 7+ (contenido narrativo)
- **Caché/Eventos**: Redis 7+
- **Tareas Asincrónicas**: Celery
- **Contenedores**: Docker & Docker Compose

### Arquitectura de Datos
- **PostgreSQL**: Usuarios, balances, misiones, logros, transacciones
- **MongoDB**: Contenido narrativo detallado, preguntas de trivias
- **Redis**: Caché de estado, event bus, rate limiting

### Patrones de Diseño
- **Event-Driven Architecture**: Comunicación entre módulos
- **Modular Design**: Separación clara de responsabilidades
- **Repository Pattern**: Abstracción de acceso a datos
- **Strategy Pattern**: Condiciones de desbloqueo intercambiables

## 📁 Estructura del Proyecto

```
dianabot/
├── bot/                    # Componentes del bot de Telegram
│   ├── core/               # Handlers y lógica central del bot
│   ├── commands/           # Comandos del bot
│   └── keyboards/          # Teclados inline
├── modules/                # Módulos funcionales
│   ├── narrative/          # Motor de narrativa
│   ├── gamification/       # Sistema de gamificación
│   └── admin/              # Gestión de canales y usuarios
├── core/                   # Componentes centrales
│   ├── event_bus.py        # Sistema de eventos
│   ├── config_manager.py   # Configuración unificada
│   └── models.py           # Modelos de base de datos
├── api/                    # API REST para panel admin
├── dashboard/              # Panel de administración web
├── tasks/                  # Tareas asincrónicas
├── tests/                  # Pruebas unitarias/integración
├── config/                 # Configuración de la aplicación
├── utils/                  # Utilidades y helpers
└── docs/                   # Documentación
```

## 🚀 Configuración Inicial

### 1. Pre-requisitos
- Python 3.11+
- PostgreSQL 15+
- MongoDB 7+
- Redis 7+
- Docker y Docker Compose (opcional pero recomendado)

### 2. Instalación

```bash
# Clonar el repositorio
git clone https://github.com/your-username/dianabot.git
cd dianabot

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus propias credenciales
```

### 3. Configuración de Bases de Datos

```bash
# Iniciar servicios con Docker Compose (recomendado)
docker-compose up -d

# O configurar manualmente PostgreSQL, MongoDB y Redis
```

### 4. Ejecución

```bash
# Iniciar el bot
python -m bot.main

# O iniciar con el proceso completo (recomendado para desarrollo)
docker-compose up --build
```

## 🔐 Variables de Entorno

Crear archivo `.env` con las siguientes variables:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_URL=your_webhook_url_here

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=dianabot
POSTGRES_USER=dianabot_user
POSTGRES_PASSWORD=your_secure_password_here

# MongoDB
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=dianabot_narrative

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Payment
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
TELEGRAM_PAYMENT_PROVIDER_TOKEN=your_provider_token_here

# Security
SECRET_KEY=your_very_secure_secret_key_here
CALLBACK_SECRET=your_callback_secret_here

# Application
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
```

## 🛡️ Seguridad

- **Encriptación en reposo**: Datos sensibles encriptados con AES-256
- **Encriptación en tránsito**: HTTPS/TLS 1.3 para todas las comunicaciones
- **Rate Limiting**: Protección contra abuso de endpoints
- **Validación de datos**: Validación y sanitización de todos los inputs
- **Firmas de seguridad**: HMAC para protección de callback data
- **Auditoría**: Logs inmutables de todas las transacciones

## 📊 Monetización

- **Suscripciones VIP**: Acceso a contenido premium (niveles 4-6)
- **Micro-transacciones**: Compra de besitos y items exclusivos
- **Contenido diferenciado**: 40% gratuito, 30% con esfuerzo, 30% exclusivo VIP

## 📈 Escalabilidad

- **Sharding de base de datos**: Distribución horizontal por user_id
- **Redis Cluster**: Para datasets mayores a la RAM de un solo servidor
- **Carga balanceada**: Múltiples instancias detrás de un load balancer
- **Colas de tareas**: Celery para operaciones asíncronas
- **Caché inteligente**: TTLs y pre-carga de datos frecuentes

## 🧪 Testing

```bash
# Ejecutar pruebas unitarias
pytest tests/unit/

# Ejecutar pruebas de integración
pytest tests/integration/

# Ejecutar todas las pruebas
pytest
```

## 🚢 Despliegue

Para despliegue en producción:

```bash
# Construir imagen Docker
docker build -t dianabot .

# Iniciar con Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

## 📋 Roadmap

### Fase 1 (Semanas 1-3): Fundamentos
- Configuración de infraestructura básica
- Bot básico con sistema de usuarios
- Event bus funcional

### Fase 2 (Semanas 4-6): Narrativa
- Motor de narrativa ramificada
- Sistema de fragmentos y decisiones
- Desbloqueos condicionales

### Fase 3 (Semanas 7-9): Gamificación
- Economía de besitos
- Sistema de inventario
- Misiones y logros

### Fase 4 (Semanas 10-12): Administración
- Gestión de suscripciones VIP
- Sistema de canales
- Publicación programada

### Fase 5 (Semanas 13-15): Configuración Unificada
- Panel de administración
- Asistentes de creación
- Validación y propagación

## 🤝 Contribución

1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Haz commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Haz push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Distribuido bajo la licencia MIT. Consulta `LICENSE` para más información.

## 📞 Contacto

Proyecto DianaBot - [tu-email@ejemplo.com](mailto:tu-email@ejemplo.com)

Enlace del proyecto: [https://github.com/your-username/dianabot](https://github.com/your-username/dianabot)
```