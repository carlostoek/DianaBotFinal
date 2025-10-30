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

# Fase 8: Misiones Básicas

### Objetivo
Sistema de misiones sin complejidad excesiva

### Componentes a Implementar

#### 8.1 Modelos de Misiones
- **Crear**: Tablas de misiones y progreso
- **Referencia**: Sección 2.3 - PostgreSQL (tablas `missions`, `user_missions`)
- **Archivos**:
  - `database/models.py` (modelos Mission, UserMission)
  - `database/migrations/006_create_missions_tables.sql`
- **Campos**: mission_id, mission_key, title, requirements, rewards, recurrence

#### 8.2 Servicio de Misiones
- **Crear**: Lógica de misiones
- **Referencia**: Sección 4.2 - Sistema de Misiones
- **Archivos**:
  - `modules/gamification/missions.py`
- **Funciones**:
  - `assign_mission(user_id, mission_key)`
  - `update_mission_progress(user_id, mission_id, progress)`
  - `complete_mission(user_id, mission_id)`
  - `get_active_missions(user_id)`
  - `get_available_missions(user_id)`

#### 8.3 Seeders de Misiones
- **Crear**: Misiones de prueba
- **Referencia**: Apéndice G - Ejemplo de Configuración de Misión
- **Archivos**:
  - `database/seeds/missions_seed.py`
- **Misiones**:
  - Misión diaria: "Completa 1 fragmento" (20 besitos)
  - Misión diaria: "Reclama tu regalo diario" (10 besitos)
  - Misión semanal: "Completa 5 fragmentos" (100 besitos)
  - Misión narrativa: "Alcanza nivel 2" (50 besitos + item)

#### 8.4 Tracking Automático de Misiones
- **Crear**: Handlers que detectan progreso en misiones
- **Referencia**: Sección 4.2 - Tracking de Progreso
- **Archivos**:
  - `core/event_handlers.py` (añadir handlers)
- **Funcionalidad**:
  - Escuchar eventos relevantes (fragment_completed, besitos_earned, etc.)
  - Actualizar progreso de misiones activas
  - Auto-completar cuando se alcanza target
  - Otorgar recompensas automáticamente

#### 8.5 Comandos de Misiones
- **Crear**: Interface para ver y gestionar misiones
- **Archivos**:
  - `bot/commands/missions.py`
- **Comandos**:
  - `/missions`: Ver misiones activas con progreso
  - `/mission <id>`: Ver detalles de misión específica

#### 8.6 Sistema de Asignación Diaria
- **Crear**: Job que asigna misiones diarias
- **Referencia**: Sección 4.2 - Asignación Inteligente de Misiones
- **Archivos**:
  - `tasks/scheduled.py`
  - `tasks/celery_app.py`
- **Funcionalidad**:
  - Cron job a las 9 AM (configurable)
  - Asignar misiones diarias a todos los usuarios activos
  - Resetear progreso de misiones expiradas

#### 8.7 Eventos de Misiones
- **Crear**: Tracking de eventos de misiones
- **Referencia**: Sección 7.1 - Eventos de Gamificación
- **Eventos**:
  - `gamification.mission_assigned`
  - `gamification.mission_progress_updated`
  - `gamification.mission_completed`

### Resultado de Fase 8
✓ Sistema de misiones funcional
✓ Tracking automático de progreso
✓ Misiones diarias y semanales funcionando
✓ Recompensas automáticas al completar
✓ Engagement diario incentivado

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

### 4.2 Sistema de Misiones

Las misiones son el motor de engagement diario. Su diseño debe balancear desafío, variedad y recompensa.

**Tipos de Misiones**

Misiones Diarias: Se resetean cada 24 horas. Ejemplos:
- "Reacciona a 3 publicaciones en el canal principal" (10 besitos)
- "Completa 1 fragmento narrativo" (20 besitos)
- "Responde correctamente 2 trivias" (15 besitos)

Misiones Semanales: Se resetean cada lunes. Ejemplos:
- "Completa 5 misiones diarias" (100 besitos + item raro)
- "Avanza 3 niveles narrativos" (150 besitos + badge)
- "Gana 500 besitos de cualquier fuente" (item épico)

Misiones Narrativas: Activadas por progreso en la historia. Ejemplos:
- Tras completar fragmento 8: "Encuentra la carta oculta de Diana" (pista + 50 besitos)
- Tras tomar decisión específica: "Investiga el pasado de Lucien" (fragmento secreto desbloqueado)

Misiones Sociales: Fomentan interacción con otros usuarios. Ejemplos:
- "Regala 50 besitos a otro usuario" (25 besitos de recompensa + badge "Generoso")
- "Participa en una subasta" (item especial)

Misiones de Eventos: Limitadas temporalmente, asociadas a eventos especiales. Ejemplos:
- Durante evento de aniversario: "Completa la búsqueda del tesoro" (item legendario único)

**Asignación Inteligente de Misiones**

No todos los usuarios reciben las mismas misiones diarias. El sistema de asignación considera:

Nivel de progreso narrativo: Usuarios en nivel 1 reciben misiones más simples que usuarios en nivel 6.

Patrón de juego: Si un usuario juega mayormente por las noches, sus misiones diarias se asignan considerando ese horario.

Preferencias detectadas: Si un usuario raramente participa en trivias pero completa muchos fragmentos, recibe más misiones narrativas.

Balance de economía: Si un usuario tiene muy pocos besitos, el sistema prioriza misiones con recompensas más generosas.

**Tracking de Progreso**

El progreso de misiones se trackea en tiempo real usando una combinación de base de datos y caché:

```json
{
  "user_id": 12345,
  "mission_id": 67,
  "mission_type": "daily",
  "requirements": {
    "react_to_posts": {
      "target": 3,
      "current": 1,
      "tracked_posts": [98765]
    }
  },
  "status": "active",
  "expires_at": "2025-10-29T00:00:00Z"
}
```

Cada vez que el usuario realiza una acción relevante (reacciona a un post), el sistema:
1. Busca misiones activas del usuario
2. Verifica si la acción contribuye a alguna misión
3. Actualiza el progreso
4. Si se completa la misión, otorga recompensas automáticamente y publica evento

### 7.1 Event Bus - Sistema Nervioso Central

Eventos de Gamificación:
- `gamification.besitos_earned`: Usuario ganó besitos
- `gamification.besitos_spent`: Usuario gastó besitos
- `gamification.item_purchased`: Usuario compró item
- `gamification.item_used`: Usuario usó item consumible
- `gamification.achievement_unlocked`: Usuario desbloqueó achievement
- `gamification.mission_assigned`: Misión asignada a usuario
- `gamification.mission_completed`: Usuario completó misión
- `gamification.auction_won`: Usuario ganó subasta
- `gamification.trivia_answered`: Usuario respondió trivia