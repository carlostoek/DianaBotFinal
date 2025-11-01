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

# Fase 19: Subastas en Tiempo Real

### Objetivo
Sistema de subastas con mecánicas complejas y prevención de manipulación

### Componentes a Implementar

#### 19.1 Modelos de Subastas
- **Crear**: Tablas de subastas y pujas
- **Referencia**: Sección 2.3 - PostgreSQL (tablas `auctions`, `bids`)
- **Archivos**:
  - `database/models.py` (modelos Auction, Bid)
  - `database/migrations/015_create_auctions_bids.sql`
- **Campos**: auction_id, item_id, start_price, current_bid, winner_id, status, end_time

#### 19.2 Servicio de Subastas
- **Crear**: Lógica de subastas
- **Referencia**: Sección 4.4 - Mecánica de Subasta
- **Archivos**:
  - `modules/gamification/auctions.py`
- **Funciones**:
  - `create_auction(item_key, start_price, duration_minutes)`
  - `place_bid(user_id, auction_id, amount)`
  - `get_active_auctions()`
  - `close_auction(auction_id)`
  - `get_auction_status(auction_id)`

#### 19.3 Locks Distribuidos
- **Crear**: Prevención de condiciones de carrera
- **Referencia**: Sección 4.4 - Prevención de Manipulación
- **Archivos**:
  - `utils/locks.py`
- **Funcionalidad**:
  - Usar Redis para locks
  - Lock al procesar puja
  - Timeout automático

#### 19.4 Timer Dinámico
- **Crear**: Sistema de extensión de tiempo
- **Referencia**: Sección 4.4 - Mecánica de Subasta
- **Modificar**: `modules/gamification/auctions.py`
- **Funcionalidad**:
  - Si puja en últimos 60 segundos, extender 60s más
  - Prevenir "sniping"
  - Actualizar timer en tiempo real

#### 19.5 Handlers de Subastas
- **Crear**: Interface de subastas
- **Archivos**:
  - `bot/handlers/auctions.py`
  - `bot/keyboards/auction_keyboards.py`
- **Funcionalidad**:
  - Ver subastas activas
  - Pujar en subasta
  - Ver historial de pujas
  - Notificar cuando alguien supera tu puja

#### 19.6 Comando de Subastas
- **Crear**: Entry point
- **Archivos**:
  - `bot/commands/auctions.py`
- **Comandos**:
  - `/auctions`: Ver subastas activas
  - `/auction <id>`: Ver detalles de subasta específica

#### 19.7 Job de Cierre de Subastas
- **Crear**: Finalización automática
- **Referencia**: Sección 4.4 - Mecánica de Subasta
- **Archivos**:
  - `tasks/scheduled.py` (añadir job)
- **Funcionalidad**:
  - Ejecutar cada minuto
  - Cerrar subastas expiradas
  - Transferir item al ganador
  - Retornar besitos a perdedores
  - Notificar resultado

#### 19.8 Anuncios de Subastas
- **Crear**: Posts automáticos en canales
- **Referencia**: Sección 5.2 - Tipos de Publicaciones
- **Funcionalidad**:
  - Anunciar 24h antes
  - Post al iniciar subasta
  - Actualizaciones de puja importante
  - Anunciar ganador

#### 19.9 Eventos de Subastas
- **Crear**: Tracking de actividad
- **Referencia**: Sección 7.1 - Eventos de Gamificación
- **Eventos**:
  - `gamification.auction_started`
  - `gamification.bid_placed`
  - `gamification.auction_won`

### Resultado de Fase 19
✓ Sistema de subastas en tiempo real
✓ Pujas con locks distribuidos
✓ Timer dinámico anti-sniping
✓ Cierre automático
✓ Notificaciones a participantes
✓ Integrado con inventario y besitos

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

### 4.4 Subastas en Tiempo Real

Las subastas son eventos de alta tensión que crean picos de engagement.

**Mecánica de Subasta**

Anuncio: 24 horas antes, se anuncia la subasta en canales con preview del item.

Inicio: A hora programada, comienza subasta con precio inicial.

Puja: Usuarios pujan incrementando el precio en intervalos mínimos (ej: +10 besitos).

Timer dinámico: Si alguien puja en los últimos 60 segundos, el timer se extiende 60 segundos más (previene "sniping").

Cierre: Cuando el timer llega a cero sin nuevas pujas, el ganador recibe el item.

**Prevención de Manipulación**

Las subastas son vulnerables a abusos si no se protegen:

Anti-shill bidding: Usuarios no pueden pujar en sus propias subastas si el sistema permite subastas user-to-user.

Verificación de fondos: Antes de aceptar puja, verificamos que el usuario tiene los besitos necesarios.

Rate limiting: Máximo 1 puja cada 5 segundos por usuario para prevenir spam.

Historia de pujas: Todas las pujas se registran con timestamp inmutable para auditoría.

Locks distribuidos: Usamos Redis para locks que previenen pujas simultáneas que podrían causar inconsistencias.

**Tipos de Subastas**

Subastas administrativas: El sistema subasta items raros en horarios fijos (ej: todos los domingos 8pm).

Subastas de usuario a usuario: Usuarios VIP pueden subastar items de su inventario, permitiendo mercado secundario.

Subastas holandesas: El precio empieza alto y baja cada minuto hasta que alguien compra.

Subastas silenciosas: Las pujas son privadas, nadie sabe quién está pujando ni cuánto hasta el final.

### 8.1 Seguridad

**Prevención de Fraude en Besitos**

La economía virtual es vulnerable a explotación:

Rate Limiting por Usuario:
```python
def check_rate_limit(user_id, action, limit, window_seconds):
    """
    Verifica si el usuario ha excedido el límite de acciones
    """
    key = f'ratelimit:{user_id}:{action}'
    current = redis_client.incr(key)
    
    if current == 1:
        redis_client.expire(key, window_seconds)
    
    if current > limit:
        raise RateLimitExceeded(
            f"User {user_id} exceeded {action} limit: {limit}/{window_seconds}s"
        )
    
    return current

# Uso
check_rate_limit(user_id, 'trivia_answer', limit=20, window_seconds=3600)
check_rate_limit(user_id, 'purchase', limit=10, window_seconds=60)
```

Detección de Anomalías:
```python
def detect_suspicious_activity(user_id):
    """
    Detecta patrones sospechosos de fraude
    """
    # Besitos ganados en última hora
    recent_earnings = get_recent_transactions(
        user_id, 
        transaction_type='earn',
        hours=1
    )
    
    if sum(t.amount for t in recent_earnings) > 1000:
        flag_for_review(user_id, 'excessive_earnings')
    
    # Respuestas de trivia demasiado rápidas
    recent_trivias = get_recent_trivia_answers(user_id, hours=1)
    avg_response_time = mean(t.response_time for t in recent_trivias)
    
    if avg_response_time < 2.0:  # menos de 2 segundos promedio
        flag_for_review(user_id, 'impossibly_fast_trivias')
    
    # Múltiples cuentas desde misma IP
    user_ip = get_user_ip(user_id)
    users_from_ip = get_users_by_ip(user_ip, hours=24)
    
    if len(users_from_ip) > 5:
        flag_for_review(user_id, 'multiple_accounts_same_ip')
```

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