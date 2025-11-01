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


## FASE 3: Sistema de Besitos (Economía Base) (Días 11-14)

### Objetivo
Implementar economía virtual básica sin mecánicas complejas

### Componentes a Implementar

#### 3.1 Modelo de Balance de Besitos
- **Crear**: Tablas para balance y transacciones
- **Referencia**: Sección 2.3 - PostgreSQL (tablas `user_balances`, `transactions`)
- **Archivos**:
  - `database/models.py` (modelos UserBalance, Transaction)
  - `database/migrations/003_create_balances_transactions.sql`
- **Campos**: user_id, besitos, lifetime_besitos, transaction logs

#### 3.2 Servicio de Besitos
- **Crear**: Lógica de negocio para manejar besitos
- **Referencia**: Sección 4.1 - Economía de Besitos
- **Archivos**:
  - `modules/gamification/besitos.py`
- **Funciones**:
  - `grant_besitos(user_id, amount, source)`
  - `spend_besitos(user_id, amount, purpose)`
  - `get_balance(user_id)`
  - `get_transaction_history(user_id)`
- **Validaciones**: Balance no negativo, transacciones atómicas

#### 3.3 Eventos de Besitos
- **Crear**: Publicar eventos al otorgar/gastar besitos
- **Referencia**: Sección 7.1 - Eventos de Gamificación
- **Modificar**: `modules/gamification/besitos.py`
- **Eventos**:
  - `gamification.besitos_earned`
  - `gamification.besitos_spent`

#### 3.4 Comandos de Besitos
- **Crear**: Comandos para consultar y testear besitos
- **Referencia**: Sección 4.1 - Economía de Besitos
- **Archivos**:
  - `bot/commands/balance.py`
  - `bot/commands/history.py` (historial de transacciones)
- **Comandos**:
  - `/balance`: Mostrar besitos actuales
  - `/history`: Mostrar últimas transacciones

#### 3.5 Regalo Diario (Daily Reward)
- **Crear**: Sistema que otorga besitos diarios
- **Referencia**: Sección 4.1 - Economía de Besitos (fuentes de entrada)
- **Archivos**:
  - `modules/gamification/daily_rewards.py`
  - `bot/commands/daily.py`
- **Funcionalidad**:
  - Comando `/daily` otorga 10 besitos
  - Solo una vez por día por usuario
  - Usar Redis para tracking diario

### Resultado de Fase 3
✓ Sistema de besitos funcional
✓ Transacciones atómicas y auditadas
✓ Usuarios pueden ganar y consultar besitos
✓ Daily reward implementado


REFERENCIAS

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

**MongoDB - Colecciones de Contenido Flexible**

```javascript
// Colección: narrative_content
{
  _id: ObjectId,
  fragment_key: "fragment_001_decision",
  level_id: 1,
  content: {
    narrator: "lucien",
    text: "Lucien te observa con intensidad...",
    media: [
      { type: "image", url: "...", alt: "..." }
    ],
    decisions: [
      {
        decision_id: "dec_001",
        text: "Acercarte con confianza",
        consequences: {
          narrative_flags: ["confident_approach"],
          next_fragment: "fragment_002_confident",
          immediate_rewards: { besitos: 5 }
        }
      },
      {
        decision_id: "dec_002",
        text: "Mantener distancia cautelosa",
        consequences: {
          narrative_flags: ["cautious_approach"],
          next_fragment: "fragment_002_cautious",
          immediate_rewards: { besitos: 3, item: "observation_note" }
        }
      }
    ]
  },
  metadata: {
    emotional_tone: "tension",
    soundtrack: "mysterious_ambient.mp3",
    reading_time_seconds: 45
  },
  version: 1,
  updated_at: ISODate()
}

// Colección: trivia_questions
{
  _id: ObjectId,
  question_key: "trivia_001",
  category: "narrative_lore",
  difficulty: "medium",
  question: {
    text: "¿Cuál es el verdadero nombre de Diana antes de su transformación?",
    media_url: null
  },
  options: [
    { option_id: "a", text: "Elena", is_correct: false },
    { option_id: "b", text: "Sofía", is_correct: true },
    { option_id: "c", text: "Isabella", is_correct: false },
    { option_id: "d", text: "Desconocido", is_correct: false }
  ],
  rewards: {
    correct: { besitos: 10, hint_item: "diana_diary_page" },
    incorrect: { besitos: 2 }
  },
  time_limit_seconds: 30,
  available_after_fragment: "fragment_005",
  created_at: ISODate()
}

// Colección: configuration_schemas
{
  _id: ObjectId,
  schema_type: "narrative_experience",
  version: "1.0",
  fields: [
    {
      field_name: "experience_title",
      field_type: "string",
      required: true,
      validation: { min_length: 5, max_length: 100 }
    },
    {
      field_name: "narrative_fragments",
      field_type: "array",
      required: true,
      item_schema: {
        fragment_content: "text",
        decisions: "array",
        unlock_conditions: "object"
      }
    },
    {
      field_name: "gamification_rewards",
      field_type: "object",
      required: false,
      properties: {
        besitos_on_completion: "integer",
        items_unlocked: "array",
        achievements: "array"
      }
    },
    {
      field_name: "vip_requirements",
      field_type: "boolean",
      required: true,
      default: false
    }
  ],
  validation_rules: [
    {
      rule: "if vip_requirements is true, besitos_on_completion must be >= 20",
      error_message: "Las experiencias VIP deben otorgar al menos 20 besitos"
    }
  ],
  propagation_targets: [
    "narrative_fragments",
    "missions",
    "items",
    "achievements",
    "channel_posts"
  ],
  created_at: ISODate()
}
```

### 4.1 Economía de Besitos

La economía de besitos es el sistema circulatorio de DianaBot. Su diseño determina la salud del ecosistema completo.

**Principios de Diseño Económico**

Una economía virtual saludable balancea tres flujos: entrada (earning), circulación (spending) y sumideros (sinks). DianaBot necesita mantener a los usuarios con suficientes besitos para sentir progreso, pero no tantos que pierdan valor.

Las fuentes de entrada de besitos incluyen:

Recompensas diarias automáticas: 10 besitos por día simplemente por iniciar sesión. Esto asegura que usuarios inactivos puedan regresar y tener algo para gastar.

Misiones completadas: 20-50 besitos según complejidad. Las misiones diarias otorgan menos, las semanales más, las narrativas especiales aún más.

Trivias correctas: 5-15 besitos dependiendo de dificultad y tiempo de respuesta.

Reacciones en canales: 2 besitos por reaccionar a publicaciones específicas (limitado a 3 por día para prevenir farming).

Achievements desbloqueados: 50-200 besitos según rareza del logro.

Los sumideros de besitos incluyen:

Tienda virtual: Items cosméticos, pistas narrativas, power-ups temporales.

Desbloqueo de fragmentos premium: Ciertos fragmentos pueden desbloquearse con besitos como alternativa a requisitos complejos.

Subastas: Usuarios compiten por items exclusivos.

Regalos a otros usuarios: Mecánica social que consume besitos del donante.

**Prevención de Inflación**

Para prevenir que besitos pierdan valor con el tiempo, implementamos:

Límites de farming: Cada fuente de besitos tiene caps diarios o semanales. No puedes ganar infinitos besitos repitiendo trivias.

Besitos que expiran: Los besitos "bonus" obtenidos de eventos especiales expiran en 30 días si no se usan. Esto incentiva gasto activo.

Items de alto valor: La tienda siempre ofrece items premium caros (500-1000 besitos) para que usuarios avanzados tengan objetivos de ahorro.

Impuestos en subastas: Las subastas cobran una pequeña comisión del 10% que se elimina del sistema, actuando como sumidero.

**Transacciones y Auditoría**

Cada transacción de besitos genera un registro inmutable en la tabla `transactions`. Esto permite:

Auditoría completa del flujo de besitos de cada usuario.
Detección de patrones anómalos (usuarios ganando besitos demasiado rápido).
Análisis de qué fuentes son más populares y efectivas.
Rollback en caso de bugs que otorguen besitos incorrectamente.

Las transacciones usan locks de base de datos para prevenir condiciones de carrera. Cuando un usuario intenta gastar 50 besitos, usamos:

```python
with transaction.atomic():
    balance = UserBalance.objects.select_for_update().get(user_id=user_id)
    if balance.besitos >= 50:
        balance.besitos -= 50
        balance.save()
        # proceder con la compra
    else:
        # fondos insuficientes
```

El `select_for_update()` asegura que nadie más puede modificar ese balance hasta que la transacción complete


### 7.1 Event Bus - Sistema Nervioso Central

El Event Bus es el mecanismo que permite comunicación desacoplada entre módulos.

**Arquitectura del Event Bus**

Usamos Redis Pub/Sub como infraestructura del Event Bus por su velocidad y confiabilidad. La estructura es:

```python
class EventBus:
    def __init__(self):
        self.redis_client = redis.Redis()
        self.handlers = defaultdict(list)
    
    def publish(self, event_type, event_data):
        """Publica un evento para que otros módulos lo consuman"""
        event = {
            'type': event_type,
            'data': event_data,
            'timestamp': datetime.now().isoformat(),
            'event_id': generate_event_id()
        }
        
        # Publicar en Redis
        self.redis_client.publish(
            f'dianabot:events:{event_type}', 
            json.dumps(event)
        )
        
        # También guardar en DB para auditoría
        EventLog.objects.create(
            event_type=event_type,
            event_data=event_data
        )
    
    def subscribe(self, event_type, handler_func):
        """Registra un handler para un tipo de evento"""
        self.handlers[event_type].append(handler_func)
        
        # Suscribirse al canal de Redis
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(f'dianabot:events:{event_type}')
        
        # Escuchar eventos en thread separado
        thread = pubsub.run_in_thread(sleep_time=0.01)
        return thread
```

**Eventos Principales del Sistema**

Eventos Narrativos:
- `narrative.fragment_started`: Usuario comenzó un fragmento
- `narrative.decision_made`: Usuario tomó una decisión
- `narrative.fragment_completed`: Usuario completó un fragmento
- `narrative.level_completed`: Usuario completó un nivel completo
- `narrative.secret_discovered`: Usuario descubrió contenido secreto

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

Eventos Administrativos:
- `admin.subscription_started`: Nueva suscripción VIP
- `admin.subscription_expiring`: Suscripción cerca de expirar
- `admin.subscription_expired`: Suscripción expiró
- `admin.user_joined_channel`: Usuario se unió a canal
- `admin.user_left_channel`: Usuario salió de canal
- `admin.content_published`: Nuevo contenido publicado

