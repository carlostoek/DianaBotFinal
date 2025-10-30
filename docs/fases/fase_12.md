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

# Fase 12: Canales de Telegram

### Objetivo
Gestión de canales free y VIP

### Componentes a Implementar

#### 12.1 Modelo de Canales
- **Crear**: Tabla de configuración de canales
- **Referencia**: Sección 2.3 - PostgreSQL (tabla `channels`)
- **Archivos**:
  - `database/models.py` (modelo Channel)
  - `database/migrations/009_create_channels.sql`
- **Campos**: channel_id, channel_type, channel_username, settings

#### 12.2 Servicio de Canales
- **Crear**: Gestión de canales
- **Referencia**: Sección 5.2 - Gestión de Contenido en Canales
- **Archivos**:
  - `modules/admin/channels.py`
- **Funciones**:
  - `configure_channel(channel_id, channel_type, settings)`
  - `get_channel_config(channel_id)`
  - `verify_channel_membership(user_id, channel_id)`

#### 12.3 Invitaciones Automáticas
- **Crear**: Sistema de invitación a canales VIP
- **Referencia**: Sección 5.1 - Flujo de Suscripción VIP
- **Modificar**: `modules/admin/subscriptions.py`
- **Funcionalidad**:
  - Al activar VIP, generar link de invitación único
  - Enviar link por DM
  - Verificar que usuario se unió

#### 12.4 Expulsión Automática
- **Crear**: Job que remueve usuarios expirados
- **Referencia**: Sección 5.1 - Jobs de Gestión VIP
- **Archivos**:
  - `tasks/scheduled.py` (añadir job)
- **Funcionalidad**:
  - Detectar suscripciones expiradas
  - Remover de canal VIP
  - Mantener en canal free

#### 12.5 Handlers de Canales
- **Crear**: Respuestas a eventos en canales
- **Archivos**:
  - `bot/handlers/channels.py`
- **Funcionalidad**:
  - Detectar nuevos miembros
  - Mensaje de bienvenida personalizado
  - Detectar usuarios que salieron

### Resultado de Fase 12
✓ Canales free y VIP gestionados
✓ Invitaciones automáticas a VIP
✓ Expulsión automática al expirar
✓ Verificación de membresía funcional

## Referencias
### 2.3 Esquema de Bases de Datos

**PostgreSQL - Esquema Principal**

```sql
-- Usuarios y Autenticación
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    telegram_username VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP,
    user_state VARCHAR(50), -- 'free', 'vip', 'banned'
    metadata JSONB -- información adicional flexible
);

-- Gamificación - Economía
CREATE TABLE user_balances (
    user_id BIGINT PRIMARY KEY REFERENCES users(user_id),
    besitos INTEGER DEFAULT 0 CHECK (besitos >= 0),
    lifetime_besitos INTEGER DEFAULT 0, -- para estadísticas
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    amount INTEGER NOT NULL,
    transaction_type VARCHAR(50), -- 'earn', 'spend', 'gift'
    source VARCHAR(100), -- 'mission', 'purchase', 'daily_reward'
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Inventario (Mochila)
CREATE TABLE items (
    item_id SERIAL PRIMARY KEY,
    item_key VARCHAR(100) UNIQUE NOT NULL, -- identificador único
    name VARCHAR(255),
    description TEXT,
    item_type VARCHAR(50), -- 'narrative_key', 'collectible', 'power_up'
    rarity VARCHAR(50), -- 'common', 'rare', 'epic', 'legendary'
    price_besitos INTEGER,
    metadata JSONB, -- efectos, requisitos, etc.
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_inventory (
    inventory_id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    item_id INTEGER REFERENCES items(item_id),
    quantity INTEGER DEFAULT 1,
    acquired_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, item_id)
);

-- Logros (Badges)
CREATE TABLE achievements (
    achievement_id SERIAL PRIMARY KEY,
    achievement_key VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255),
    description TEXT,
    icon_emoji VARCHAR(50),
    points INTEGER DEFAULT 0,
    reward_besitos INTEGER DEFAULT 0,
    reward_item_id INTEGER REFERENCES items(item_id),
    unlock_conditions JSONB, -- criterios para desbloquear
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_achievements (
    user_id BIGINT REFERENCES users(user_id),
    achievement_id INTEGER REFERENCES achievements(achievement_id),
    unlocked_at TIMESTAMP DEFAULT NOW(),
    progress JSONB, -- para logros progresivos
    PRIMARY KEY (user_id, achievement_id)
);

-- Narrativa
CREATE TABLE narrative_levels (
    level_id SERIAL PRIMARY KEY,
    level_number INTEGER UNIQUE NOT NULL,
    title VARCHAR(255),
    is_vip BOOLEAN DEFAULT FALSE,
    unlock_conditions JSONB, -- besitos, items, achievements requeridos
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE narrative_fragments (
    fragment_id SERIAL PRIMARY KEY,
    level_id INTEGER REFERENCES narrative_levels(level_id),
    fragment_key VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255),
    content_type VARCHAR(50), -- 'story', 'decision', 'mini_game'
    unlock_conditions JSONB,
    rewards JSONB, -- besitos, items, achievements otorgados
    created_at TIMESTAMP DEFAULT NOW()
);

-- El contenido narrativo va en MongoDB por su complejidad

CREATE TABLE user_narrative_progress (
    user_id BIGINT REFERENCES users(user_id),
    fragment_id INTEGER REFERENCES narrative_fragments(fragment_id),
    completed_at TIMESTAMP DEFAULT NOW(),
    choices_made JSONB, -- decisiones tomadas en este fragmento
    PRIMARY KEY (user_id, fragment_id)
);

-- Misiones
CREATE TABLE missions (
    mission_id SERIAL PRIMARY KEY,
    mission_key VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255),
    description TEXT,
    mission_type VARCHAR(50), -- 'daily', 'weekly', 'narrative', 'special'
    recurrence VARCHAR(50), -- 'once', 'daily', 'weekly'
    requirements JSONB, -- qué debe hacer el usuario
    rewards JSONB, -- besitos, items, achievements
    expiry_date TIMESTAMP, -- para misiones temporales
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_missions (
    user_id BIGINT REFERENCES users(user_id),
    mission_id INTEGER REFERENCES missions(mission_id),
    status VARCHAR(50), -- 'active', 'completed', 'expired'
    progress JSONB, -- progreso actual hacia requisitos
    assigned_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    PRIMARY KEY (user_id, mission_id)
);

-- Suscripciones VIP
CREATE TABLE subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE REFERENCES users(user_id),
    subscription_type VARCHAR(50), -- 'monthly', 'yearly', etc.
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    status VARCHAR(50), -- 'active', 'expired', 'cancelled'
    payment_reference VARCHAR(255),
    auto_renew BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Administración de Canales
CREATE TABLE channels (
    channel_id BIGINT PRIMARY KEY,
    channel_type VARCHAR(50), -- 'free', 'vip'
    channel_username VARCHAR(255),
    settings JSONB, -- configuraciones específicas del canal
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE channel_posts (
    post_id SERIAL PRIMARY KEY,
    channel_id BIGINT REFERENCES channels(channel_id),
    post_type VARCHAR(50), -- 'narrative', 'mission', 'trivia', 'announcement'
    content JSONB, -- texto, media, botones
    scheduled_for TIMESTAMP,
    published_at TIMESTAMP,
    is_protected BOOLEAN DEFAULT FALSE,
    linked_mission_id INTEGER REFERENCES missions(mission_id),
    linked_fragment_id INTEGER REFERENCES narrative_fragments(fragment_id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Configuración Unificada
CREATE TABLE config_templates (
    template_id SERIAL PRIMARY KEY,
    template_key VARCHAR(100) UNIQUE NOT NULL,
    template_type VARCHAR(50), -- 'experience', 'event', 'mission_chain'
    name VARCHAR(255),
    description TEXT,
    template_schema JSONB, -- estructura del template
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE config_instances (
    instance_id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES config_templates(template_id),
    instance_data JSONB, -- configuración específica
    created_by INTEGER, -- admin user
    status VARCHAR(50), -- 'draft', 'active', 'archived'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 5.2 Gestión de Contenido en Canales

Los canales son la interfaz principal donde los usuarios experimentan DianaBot.

**Tipos de Publicaciones**

Publicaciones Narrativas: Fragmentos de historia publicados secuencialmente, con botones inline para decisiones.

Publicaciones de Misiones: Anuncios de nuevas misiones con botones para aceptar.

Publicaciones de Trivias: Preguntas con botones de opción, cierran automáticamente después del tiempo límite.

Publicaciones de Eventos: Anuncios de subastas, eventos especiales, actualizaciones del sistema.

Publicaciones Multimedia: Imágenes, audio, video relacionados con la narrativa para enriquecer inmersión.

**Programación de Contenido**

El calendario de publicaciones permite planificar contenido con anticipación:

```json
{
  "post_id": 123,
  "channel_id": -1001234567890,
  "post_type": "narrative",
  "content": {
    "text": "Lucien te observa desde las sombras...",
    "media": [
      {"type": "photo", "file_id": "AgACAgIAAxk..."}
    ],
    "inline_buttons": [
      [
        {"text": "Acercarte", "callback_data": "decision:f015:a"}
      ],
      [
        {"text": "Alejarte", "callback_data": "decision:f015:b"}
      ]
    ]
  },
  "scheduled_for": "2025-10-29T20:00:00Z",
  "recurrence": null,
  "linked_fragment_id": 15,
  "is_protected": true,
  "status": "scheduled"
}
```

Un job cron revisa cada minuto posts programados cuyo `scheduled_for` ha llegado y los publica.

**Publicaciones Recurrentes**

Algunas publicaciones se repiten:

Misión diaria: Publicada cada día a las 9 AM.
Trivia de la noche: Publicada cada día a las 8 PM.
Resumen semanal: Publicado cada lunes con estadísticas de la semana anterior.

Estas se configuran con `recurrence: "daily"` o `recurrence: "weekly"` y el sistema las re-programa automáticamente después de publicar.

**Protección de Contenido**

Para contenido sensible o premium, habilitamos protección de Telegram:

```python
bot.send_message(
    chat_id=channel_id,
    text=content,
    protect_content=True  # Previene forward y screenshots
)
```

Adicionalmente, para contenido ultra-sensible, podemos:

Enviar mensajes que se auto-destruyen después de ser leídos (Telegram soporta esto).
Usar watermarks invisibles en imágenes para rastrear filtraciones.
Limitar acceso a contenido específico solo a usuarios con cierto nivel de trust.