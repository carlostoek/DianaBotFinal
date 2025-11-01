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

# Fase 9: Achievements (Logros)

### Objetivo
Sistema de logros desbloqueables

### Componentes a Implementar

#### 9.1 Modelos de Achievements
- **Crear**: Tablas de logros
- **Referencia**: Sección 2.3 - PostgreSQL (tablas `achievements`, `user_achievements`)
- **Archivos**:
  - `database/models.py` (modelos Achievement, UserAchievement)
  - `database/migrations/007_create_achievements_tables.sql`
- **Campos**: achievement_id, achievement_key, name, unlock_conditions, reward_besitos

#### 9.2 Servicio de Achievements
- **Crear**: Lógica de logros
- **Referencia**: Sección 4.6 - Sistema de Logros
- **Archivos**:
  - `modules/gamification/achievements.py`
- **Funciones**:
  - `check_achievement_unlock(user_id, achievement_key)`
  - `unlock_achievement(user_id, achievement_key)`
  - `get_user_achievements(user_id)`
  - `get_achievement_progress(user_id, achievement_key)`

#### 9.3 Seeders de Achievements
- **Crear**: Logros básicos
- **Referencia**: Sección 4.6 - Categorías de Achievements
- **Archivos**:
  - `database/seeds/achievements_seed.py`
- **Achievements**:
  - "Primera Decisión": Completar primer fragmento
  - "Coleccionista Novato": Poseer 5 items
  - "Millonario": Acumular 1000 besitos lifetime
  - "Dedicado": Completar 5 misiones diarias
  - "Explorador": Completar nivel 1

#### 9.4 Detector Automático de Achievements
- **Crear**: Sistema que verifica achievements tras eventos
- **Referencia**: Sección 7.3 - Handler: Achievement Unlocked
- **Archivos**:
  - `core/event_handlers.py` (añadir handlers)
- **Funcionalidad**:
  - Escuchar múltiples eventos
  - Verificar si disparan achievements
  - Desbloquear automáticamente
  - Notificar al usuario

#### 9.5 Comandos de Achievements
- **Crear**: Visualización de logros
- **Archivos**:
  - `bot/commands/achievements.py`
- **Comandos**:
  - `/achievements`: Ver logros desbloqueados y disponibles
  - `/achievement <id>`: Ver detalles y progreso

#### 9.6 Eventos de Achievements
- **Crear**: Tracking de desbloqueos
- **Referencia**: Sección 7.1 - Eventos de Gamificación
- **Eventos**:
  - `gamification.achievement_unlocked`

#### 9.7 Recompensas de Achievements
- **Crear**: Handler que otorga recompensas al desbloquear
- **Referencia**: Sección 7.3 - Handler: Achievement Unlocked
- **Archivos**:
  - `core/event_handlers.py`
- **Funcionalidad**:
  - Escuchar `achievement_unlocked`
  - Otorgar besitos y items configurados
  - Aplicar beneficios pasivos si los hay

### Resultado de Fase 9
✓ Sistema de achievements funcional
✓ Detección automática de desbloqueos
✓ Recompensas otorgadas automáticamente
✓ Objetivos a largo plazo para usuarios

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

### 4.6 Sistema de Logros (Badges/Achievements)

Los achievements proporcionan objetivos a largo plazo y prestigio social.

**Categorías de Achievements**

Progreso Narrativo:
- "Primera Decisión": Completa tu primer fragmento con decisión
- "Explorador": Completa todos los fragmentos del nivel 1-3
- "Maestro de la Historia": Completa todos los endings posibles

Económicos:
- "Millonario de Besitos": Acumula 10,000 besitos lifetime
- "Comprador Compulsivo": Compra 50 items de la tienda
- "Ahorrador": Alcanza 1,000 besitos sin gastar por 7 días

Sociales:
- "Filántropo": Regala 500 besitos a otros usuarios
- "Popular": Recibe 100 reacciones en tus mensajes
- "Rey de Subastas": Gana 10 subastas

Habilidad:
- "Genio": Responde correctamente 100 trivias
- "Perfeccionista": Completa 20 misiones sin fallar ninguna
- "Velocista": Responde trivia en menos de 3 segundos 10 veces

Secretos:
- "???": Achievements ocultos que se revelan solo al desbloquear
- Ejemplo: "Traidor" - Toma decisiones que traicionan a todos los personajes

**Beneficios de Achievements**

Pasivos: Algunos achievements otorgan beneficios permanentes. "Collector" (posee 50 items distintos) otorga +10% besitos en todas las actividades.

Cosméticos: Badges visibles en perfil de usuario.

Narrativos: Ciertos achievements desbloquean fragmentos o decisiones exclusivas.

Económicos: Recompensas one-time de besitos o items al desbloquear.

**Progresión de Achievements**

Muchos achievements tienen niveles:

"Explorador I": Completa 10 fragmentos (25 besitos)
"Explorador II": Completa 50 fragmentos (100 besitos + item)
"Explorador III": Completa 100 fragmentos (500 besitos + badge dorado + fragmento secreto)

El sistema trackea progreso hacia achievements no completados y notifica al usuario cuando está cerca (ej: "¡Solo 5 trivias más para desbloquear 'Genio'!").

### 7.3 Handlers de Eventos Complejos

Algunos eventos desencadenan lógica compleja que involucra múltiples sistemas.

**Handler: Achievement Unlocked → Rewards and Progression**

```python
@event_handler('gamification.achievement_unlocked')
def handle_achievement_unlock(event_data):
    """
    Procesa desbloqueo de achievement y todos sus efectos
    """
    user_id = event_data['user_id']
    achievement_key = event_data['achievement_key']
    
    achievement = get_achievement(achievement_key)
    
    # 1. Otorgar recompensas del achievement
    if achievement.reward_besitos > 0:
        grant_besitos(
            user_id, 
            achievement.reward_besitos, 
            source=f'achievement:{achievement_key}'
        )
    
    if achievement.reward_item_id:
        add_item_to_inventory(user_id, achievement.reward_item_id)
    
    # 2. Aplicar beneficios pasivos
    if achievement.passive_benefits:
        apply_passive_benefits(user_id, achievement.passive_benefits)
    
    # 3. Verificar desbloqueos narrativos
    fragments_unlocked = check_fragment_unlocks_by_achievement(
        user_id, 
        achievement_key
    )
    
    if fragments_unlocked:
        for fragment_key in fragments_unlocked:
            event_bus.publish('narrative.content_unlocked', {
                'user_id': user_id,
                'fragment_key': fragment_key,
                'unlock_reason': f'achievement:{achievement_key}'
            })
    
    # 4. Enviar notificación al usuario
    send_achievement_notification(user_id, achievement)
    
    # 5. Actualizar leaderboard si es achievement competitivo
    if achievement.is_competitive:
        update_achievement_leaderboard(achievement_key)
    
    # 6. Verificar meta-achievements (achievements por desbloquear achievements)
    check_meta_achievements(user_id)
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