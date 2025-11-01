# Fase 1: Bot Básico y Sistema de Usuarios

### Objetivo
Bot responde a comandos básicos y registra usuarios

### Componentes a Implementar

#### 1.1 Bot Telegram Básico
- **Crear**: Entry point del bot
- **Referencia**: Sección 2.1 - Framework del Bot
- **Archivos**:
  - `bot/main.py`
  - `bot/handlers/__init__.py`
- **Funcionalidad**:
  - Inicializar bot con python-telegram-bot
  - Handler para `/start`
  - Handler para `/help`
  - Logging básico

#### 1.2 Modelo de Usuario
- **Crear**: Tabla y modelo de usuarios
- **Referencia**: Sección 2.3 - Esquema PostgreSQL (tabla `users`)
- **Archivos**:
  - `database/models.py` (modelo User)
  - `database/migrations/001_create_users.sql`
- **Campos**: user_id, telegram_username, created_at, last_active, user_state

#### 1.3 Registro Automático de Usuarios
- **Crear**: Sistema que detecta nuevo usuario y lo registra
- **Referencia**: Sección 2.3 - Esquema PostgreSQL
- **Archivos**:
  - `bot/handlers/start.py`
  - `core/user_state.py` (funciones básicas)
- **Funcionalidad**:
  - Al recibir `/start`, verificar si usuario existe
  - Si no existe, crear registro en DB
  - Responder con mensaje de bienvenida personalizado

#### 1.4 Comandos Básicos
- **Crear**: Handlers para comandos esenciales
- **Referencia**: Sección 10.1 - Estructura del Repositorio
- **Archivos**:
  - `bot/commands/help.py`
  - `bot/commands/stats.py` (stats básicos del usuario)
- **Funcionalidad**:
  - `/help`: Mostrar ayuda
  - `/stats`: Mostrar stats básicos (fecha registro, última actividad)

### Resultado de Fase 1
✓ Bot responde a `/start`, `/help`, `/stats`
✓ Usuarios se registran automáticamente en DB
✓ Se puede consultar info básica de usuario

#### 1. Arquitectura General
**Arquitectura modular basada en eventos** que integra tres patrones clave:
- **Event-Driven**: Comunicación asíncrona entre módulos (narrativa, gamificación, administración) mediante un **Event Bus** central (Pub/Sub). Ej.: Completar un fragmento narrativo publica un evento que activa recompensas en gamificación.
- **Capas Limpias**: Cada módulo es independiente, con interfaces claras para integración.
- **Repositorio Centralizado**: **Configuration Manager** unifica reglas, recompensas y desbloqueos, sincronizando cambios entre módulos.

**Componentes Principales**:
- **Event Bus**: Sistema nervioso central para publicación/suscripción de eventos.
- **Configuration Manager**: Abstracción para crear "experiencias" coordinadas (narrativa + gamificación).
- **User State Manager**: Mantiene consistencia del estado del usuario (progreso, besitos, inventario, suscripciones).

**Patrones de Diseño**:
- **Command**: Acciones de usuario encapsuladas (deshacer, historial, asíncronas).
- **Observer**: Módulos suscritos a eventos relevantes.
- **Strategy**: Condiciones de desbloqueo intercambiables.
- **Repository**: Acceso abstraído a datos.

#### 2. Plataforma y Tecnologías
**Framework del Bot**: **python-telegram-bot (PTB) v20+**, elegido por:
- Manejo nativo de handlers, **ConversationHandler** (narrativa ramificada), callbacks y reacciones.
- **JobQueue** integrada para misiones diarias, recordatorios VIP y scheduling.
- Excelente documentación y comunidad.

**Estructura Tecnológica**:
- Backend: Python 3.11+
- Web: FastAPI (panel admin, webhooks)
- Tareas: Celery + Redis
- Cache: Redis (sesiones, rate limiting)

**Base de Datos Híbrida**:
- **PostgreSQL (Principal)**: Datos relacionales/transaccionales (estado usuario, progreso narrativo, suscripciones). Garantías ACID, JSONB para flexibilidad, índices para consultas complejas.
- **MongoDB**: Configuración dinámica y estructuras variables (fragmentos narrativos con decisiones/minijuegos, plantillas de experiencias).
- **Redis**: Estado en tiempo real (conversaciones activas, rate limiting, locks distribuidos para subastas).

## Referencias
No se encontraron referencias específicas en el documento INVESTIGACIÓN.md que correspondan exclusivamente a esta fase. La fase se basa principalmente en los componentes técnicos fundamentales descritos en las secciones generales del documento de investigación.