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

# Fase 6: Motor de Narrativa Core

### Objetivo
Sistema de fragmentos narrativos sin ramificación compleja

### Componentes a Implementar

#### 6.1 Modelos Narrativos
- **Crear**: Tablas de niveles y fragmentos
- **Referencia**: Sección 2.3 - PostgreSQL (tablas `narrative_levels`, `narrative_fragments`, `user_narrative_progress`)
- **Archivos**:
  - `database/models.py` (modelos NarrativeLevel, NarrativeFragment, UserNarrativeProgress)
  - `database/migrations/005_create_narrative_tables.sql`
- **Campos**: level_id, fragment_id, fragment_key, title, unlock_conditions, rewards

#### 6.2 Contenido Narrativo en MongoDB
- **Crear**: Colección para contenido detallado
- **Referencia**: Sección 2.3 - MongoDB (colección `narrative_content`)
- **Archivos**:
  - `database/mongo_schemas.py`
- **Estructura**: Según Apéndice F - Plantilla de Fragmento Narrativo

#### 6.3 Motor de Narrativa
- **Crear**: Engine que procesa fragmentos
- **Referencia**: Sección 3.2 - Motor de Narrativa - Implementación Conceptual
- **Archivos**:
  - `modules/narrative/engine.py`
- **Funciones**:
  - `get_current_fragment(user_id)`
  - `process_decision(user_id, fragment_key, decision_id)`
  - `get_available_fragments(user_id)`
  - `check_fragment_access(user_id, fragment_key)`

#### 6.4 Seeders de Narrativa Básica
- **Crear**: 3 fragmentos lineales de prueba
- **Referencia**: Sección 11.1 - Fase 2: Módulo de Narrativa
- **Archivos**:
  - `database/seeds/narrative_seed.py`
- **Contenido**:
  - Nivel 1 con 3 fragmentos
  - Sin ramificación compleja
  - Cada fragmento con 1-2 decisiones simples
  - Recompensas básicas de besitos

#### 6.5 Handlers de Narrativa
- **Crear**: Interface para interactuar con narrativa
- **Referencia**: Sección 3.1 - Sistema de Narrativa Ramificada
- **Archivos**:
  - `bot/handlers/narrative.py`
  - `bot/keyboards/narrative_keyboards.py`
- **Callbacks**:
  - `narrative:start`
  - `narrative:continue`
  - `narrative:decision:<fragment_key>:<decision_id>`

#### 6.6 Comando de Narrativa
- **Crear**: Entry point a la historia
- Archivos:
  - `bot/commands/story.py`
- **Comando**:
  - `/story`: Mostrar fragmento actual o comenzar narrativa

#### 6.7 Eventos Narrativos
- **Crear**: Publicar eventos de progreso narrativo
- **Referencia**: Sección 7.1 - Eventos Narrativos
- **Modificar**: `modules/narrative/engine.py`
- **Eventos**:
  - `narrative.fragment_started`
  - `narrative.decision_made`
  - `narrative.fragment_completed`

#### 6.8 Integración Narrativa-Besitos
- **Crear**: Handler que otorga besitos al completar fragmentos
- **Referencia**: Sección 7.2 - Flujo: Usuario Completa Fragmento Narrativo
- **Archivos**:
  - `core/event_handlers.py` (añadir handler)
- **Funcionalidad**:
  - Escuchar `narrative.fragment_completed`
  - Otorgar besitos configurados en rewards
  - Publicar `gamification.besitos_earned`

### Resultado de Fase 6
✓ Motor narrativo funcional
✓ 3 fragmentos jugables
✓ Decisiones afectan progreso
✓ Recompensas de besitos integradas
✓ Progreso guardado por usuario

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

### 3.2 Motor de Narrativa - Implementación Conceptual

El motor de narrativa es el componente que interpreta la estructura de fragmentos y decide qué mostrar al usuario en cada momento. Su lógica central sigue este flujo:

Cuando un usuario solicita continuar la narrativa, el motor primero recupera su estado completo: posición actual, flags, variables, inventario, achievements. Luego consulta el fragmento actual desde MongoDB.

Antes de mostrar el fragmento, el motor procesa las plantillas de texto, interpolando variables. Si el texto incluye `{{trust_level_diana > 5 ? 'querida amiga' : 'visitante'}}`, el motor evalúa la condición y sustituye el texto apropiado.

Las decisiones mostradas se filtran según condiciones. Una decisión podría tener `"visible_if": {"has_item": "skeleton_key", "trust_level_lucien": ">= 5"}`. El motor evalúa estas condiciones y solo muestra decisiones disponibles para el usuario.

Cuando el usuario toma una decisión, el motor:

1. Aplica las consecuencias inmediatas (otorga recompensas, actualiza flags)
2. Publica eventos al Event Bus para que otros módulos reaccionen
3. Determina el siguiente fragmento según la decisión
4. Actualiza el estado del usuario en base de datos y caché
5. Pre-carga el siguiente fragmento para respuesta instantánea

### 3.1 Sistema de Narrativa Ramificada

La narrativa ramificada es el alma de DianaBot, y su implementación requiere un equilibrio cuidadoso entre flexibilidad y rendimiento. Vamos a explorar cómo estructurar esto de manera que sea potente pero manejable.

**Estructura de Grafo Dirigido**

Conceptualmente, la narrativa es un grafo dirigido donde cada nodo es un fragmento y cada arista representa una decisión o transición. Sin embargo, no es un grafo completamente libre, sino uno con restricciones y capas.

Imaginemos la narrativa como un edificio de varios pisos (niveles), donde cada piso tiene habitaciones (fragmentos). Puedes moverte libremente dentro de un piso si tienes las llaves adecuadas (condiciones de desbloqueo), pero para subir de piso necesitas cumplir requisitos especiales (completar ciertos fragmentos, tener items, ser VIP).

Cada fragmento tiene una estructura interna que incluye:

El contenido narrativo en sí: texto, imágenes, audio ambiental. Este contenido puede tener variables interpoladas basadas en decisiones previas del usuario. Por ejemplo, si el usuario tomó la decisión "approach_confident" anteriormente, Lucien podría referirse a esto: "Recuerdo tu confianza al acercarte la primera vez".

Las decisiones disponibles: cada una con su propio texto, consecuencias narrativas, y efectos en gamificación. Las consecuencias pueden ser inmediatas (siguiente fragmento) o diferidas (flags que afectan fragmentos futuros).

Condiciones de entrada: qué debe tener o haber hecho el usuario para acceder a este fragmento. Esto puede incluir besitos mínimos, items en inventario, badges desbloqueados, o decisiones previas específicas.

Recompensas al completar: besitos, items, achievements que se otorgan automáticamente.

**Persistencia del Estado Narrativo**

El estado narrativo de cada usuario se compone de varias capas:

Posición actual: en qué fragmento está el usuario en este momento. Esto se guarda en Redis para acceso ultrarrápido.

Historial de fragmentos completados: guardado en PostgreSQL, permite verificar si el usuario puede acceder a fragmentos que requieren haber completado otros.

Flags narrativos: booleanos que representan decisiones importantes. Por ejemplo, "betrayed_lucien", "found_secret_passage", "earned_diana_trust". Estos flags se usan para personalizar contenido futuro.

Variables de estado: contadores o valores numéricos que rastrean aspectos de la relación del usuario con los personajes. Por ejemplo, "trust_level_diana": 7, "intimacy_level_lucien": 3.

### 7.1 Event Bus - Sistema Nervioso Central

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

### 7.2 Ejemplos de Flujos Integrados

**Flujo: Usuario Completa Fragmento Narrativo**

1. Usuario toma decisión en fragmento narrativo
2. Módulo de Narrativa procesa decisión y actualiza estado
3. Narrativa publica evento: `narrative.fragment_completed`

```python
event_bus.publish('narrative.fragment_completed', {
    'user_id': 12345,
    'fragment_key': 'fragment_015',
    'decision_made': 'approach_confident',
    'completion_time_seconds': 180
})
```

4. Módulo de Gamificación escucha evento y:
   - Otorga besitos definidos en rewards del fragmento
   - Agrega items al inventario si corresponde
   - Verifica si se desbloquean achievements
   - Verifica si hay misiones que rastrean "completar fragmentos"
   - Publica evento: `gamification.besitos_earned`

5. Módulo de Administración escucha evento y:
   - Registra completación para analíticas
   - Verifica si usuario completó todos los fragmentos del nivel
   - Si corresponde, envía notificación de felicitación

6. Sistema de Configuración escucha evento y:
   - Verifica si hay configuraciones que se activan al completar este fragmento
   - Ejemplo: activar misión especial que solo aparece tras este fragmento