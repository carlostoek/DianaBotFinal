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

# Fase 11: Sistema de Suscripciones VIP

### Objetivo
Gestión de usuarios VIP y contenido premium

### Componentes a Implementar

#### 11.1 Modelo de Suscripciones
- **Crear**: Tabla de suscripciones
- **Referencia**: Sección 2.3 - PostgreSQL (tabla `subscriptions`)
- **Archivos**:
  - `database/models.py` (modelo Subscription)
  - `database/migrations/008_create_subscriptions.sql`
- **Campos**: subscription_id, user_id, subscription_type, start_date, end_date, status

#### 11.2 Servicio de Suscripciones
- **Crear**: Lógica de gestión de VIP
- **Referencia**: Sección 5.1 - Gestión de Suscripciones VIP
- **Archivos**:
  - `modules/admin/subscriptions.py`
- **Funciones**:
  - `create_subscription(user_id, type, duration_days)`
  - `get_active_subscription(user_id)`
  - `is_vip(user_id)`
  - `cancel_subscription(subscription_id)`
  - `get_expiring_subscriptions(days_before)`

#### 11.3 Verificación de Acceso VIP
- **Crear**: Middleware de verificación
- **Referencia**: Sección 8.1 - Control de Acceso VIP
- **Archivos**:
  - `modules/admin/vip_access.py`
- **Funciones**:
  - `verify_vip_access(user_id, resource_type, resource_id)`
  - Verificación multicapa (DB + caché)

#### 11.4 Contenido VIP
- **Crear**: Fragmentos de nivel 4 (VIP)
- **Referencia**: Sección 11.1 - Fase 4: Módulo de Administración
- **Archivos**:
  - `database/seeds/narrative_seed.py` (añadir nivel 4)
- **Contenido**:
  - Nivel 4 marcado como VIP
  - 5 fragmentos exclusivos
  - Verificación de VIP antes de acceso

#### 11.5 Jobs de Gestión VIP
- **Crear**: Tareas programadas para suscripciones
- **Referencia**: Sección 5.1 - Recordatorios y Expiraciones
- **Archivos**:
  - `tasks/scheduled.py` (añadir jobs)
- **Jobs**:
  - Recordatorio 7 días antes de expirar
  - Recordatorio 24 horas antes
  - Expiración automática al vencer
  - Actualizar user_state a 'free'

#### 11.6 Comandos VIP
- **Crear**: Gestión de suscripción desde bot
- **Archivos**:
  - `bot/commands/vip.py`
- **Comandos**:
  - `/vip`: Ver status de suscripción
  - `/upgrade`: Info sobre beneficios VIP

#### 11.7 Notificaciones VIP
- **Crear**: Mensajes automáticos sobre suscripción
- **Referencia**: Sección 5.1 - Recordatorios y Expiraciones
- **Archivos**:
  - `modules/admin/notifications.py`
- **Funcionalidad**:
  - Notificar al activar VIP
  - Recordatorios antes de expirar
  - Mensaje al expirar con opción de renovar

### Resultado de Fase 11
✓ Sistema VIP funcional
✓ Contenido exclusivo para suscriptores
✓ Verificación automática de acceso
✓ Notificaciones de expiración
✓ Diferenciación clara entre free y VIP

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

### 5.1 Gestión de Suscripciones VIP

El módulo de administración es el guardián que asegura que solo usuarios autorizados accedan a contenido premium.

**Flujo de Suscripción VIP**

Registro de suscripción: Cuando un usuario paga (proceso externo a Telegram), el administrador registra la suscripción en el sistema:

```json
{
  "user_id": 12345,
  "subscription_type": "monthly",
  "start_date": "2025-10-28T00:00:00Z",
  "end_date": "2025-11-28T23:59:59Z",
  "payment_reference": "STRIPE_CH_123ABC",
  "auto_renew": true,
  "status": "active"
}
```

Invitación automática: El bot invita al usuario al canal VIP usando `createChatInviteLink` con `member_limit=1` para un link único.

Verificación de membresía: Cada vez que el usuario intenta acceder a contenido VIP (fragmentos, misiones), el sistema verifica:
1. ¿La suscripción está activa? (status = 'active')
2. ¿La fecha actual está dentro del rango? (start_date <= now <= end_date)
3. ¿El usuario está en el canal VIP? (caché de `getChatMember`)

**Recordatorios y Expiraciones**

Jobs programados manejan el ciclo de vida de suscripciones:

Job de recordatorio (7 días antes): "Tu suscripción VIP expira en 7 días. Renueva para seguir disfrutando..."

Job de recordatorio (24 horas antes): "¡Última oportunidad! Tu suscripción expira mañana."

Job de expiración (al expirar): 
- Cambia status a 'expired'
- Expulsa al usuario del canal VIP
- Envía mensaje de despedida con opción de renovar
- Bloquea acceso a contenido VIP en narrativa

Job de limpieza (30 días después): Archiva suscripciones expiradas para mantener queries eficientes.

**Auto-renovación**

Si el usuario configuró auto-renovación:

2 días antes de expirar: El sistema intenta procesar el pago (esto requiere integración con procesador de pagos).

Si el pago es exitoso: Se crea nueva suscripción automáticamente, el usuario no experimenta interrupción.

Si el pago falla: Se notifica al usuario para que actualice método de pago, dando 48 horas de gracia.

### 8.1 Seguridad

**Control de Acceso VIP**

El acceso a contenido VIP requiere múltiples capas de verificación:

```python
def verify_vip_access(user_id, resource_type, resource_id):
    """
    Verificación en múltiples capas para contenido VIP
    """
    # Capa 1: Verificar suscripción en DB
    subscription = get_active_subscription(user_id)
    if not subscription or subscription.status != 'active':
        return False, "No active VIP subscription"
    
    # Capa 2: Verificar fechas
    now = datetime.now()
    if not (subscription.start_date <= now <= subscription.end_date):
        return False, "Subscription expired"
    
    # Capa 3: Verificar membresía en canal VIP (con caché)
    cache_key = f'vip_member:{user_id}'
    is_member = redis_client.get(cache_key)
    
    if is_member is None:
        # No en caché, verificar con Telegram
        is_member = check_telegram_membership(user_id, VIP_CHANNEL_ID)
        redis_client.setex(cache_key, 3600, '1' if is_member else '0')
    else:
        is_member = is_member == b'1'
    
    if not is_member:
        return False, "Not member of VIP channel"
    
    # Capa 4: Verificar permisos específicos del recurso
    if resource_type == 'fragment':
        fragment = NarrativeFragment.objects.get(fragment_id=resource_id)
        if not fragment.is_vip:
            return True, "Resource is not VIP-restricted"
    
    return True, "Access granted"
```