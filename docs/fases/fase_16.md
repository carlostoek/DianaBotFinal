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

# Fase 16: Configuration Manager

### Objetivo
Sistema de configuración centralizada

### Componentes a Implementar

#### 16.1 Modelos de Configuración
- **Crear**: Tablas de templates e instances
- **Referencia**: Sección 2.3 - PostgreSQL (tablas `config_templates`, `config_instances`)
- **Archivos**:
  - `database/models.py` (modelos ConfigTemplate, ConfigInstance)
  - `database/migrations/012_create_config_tables.sql`
- **Campos**: template_id, template_type, template_schema, instance_data

#### 16.2 Configuration Manager Core
- **Crear**: Gestor centralizado
- **Referencia**: Sección 6 - Sistema de Configuración Centralizada
- **Archivos**:
  - `core/config_manager.py`
- **Funciones**:
  - `create_config_instance(template_type, data)`
  - `validate_config(template_type, data)`
  - `propagate_config(instance_id)`
  - `get_config_instance(instance_id)`

#### 16.3 Templates Básicos
- **Crear**: Schemas de configuración
- **Referencia**: Sección 6.3 - Plantillas y Asistentes
- **Archivos**:
  - `core/config_templates/`
    - `narrative_experience.json`
    - `mission_template.json`
    - `event_template.json`
- **Contenido**: Schemas según Apéndice H

#### 16.4 Sistema de Validación
- **Crear**: Validadores de configuración
- **Referencia**: Sección 6.7 - Sistema de Validación y Coherencia
- **Archivos**:
  - `core/validators.py`
- **Validadores**:
  - Referencias existen (items, achievements, etc.)
  - Rangos de valores apropiados
  - No ciclos infinitos
  - Coherencia entre módulos

#### 16.5 Sistema de Propagación
- **Crear**: Lógica de propagación a módulos
- **Referencia**: Sección 6.2 - Flujos de Configuración Unificada
- **Archivos**:
  - `core/config_propagator.py`
- **Funcionalidad**:
  - Crear registros en múltiples tablas
  - Transacciones atómicas
  - Rollback en caso de error
  - Log de cambios propagados

#### 16.6 Colección de Schemas en MongoDB
- **Crear**: Schemas de validación
- **Referencia**: Sección 2.3 - MongoDB (colección `configuration_schemas`)
- **Archivos**:
  - `database/mongo_schemas.py`
- **Contenido**: Definiciones de templates con validación

#### 16.7 Versionado de Configuración
- **Crear**: Sistema de versiones
- **Referencia**: Sección 6.6 - Historial y Versionado
- **Archivos**:
  - `database/models.py` (modelo ConfigVersion)
  - `database/migrations/013_create_config_versions.sql`
- **Funcionalidad**:
  - Guardar versión en cada cambio
  - Diff de cambios
  - Rollback a versión anterior

### Resultado de Fase 16
✓ Configuration Manager funcional
✓ Validación automática de configuraciones
✓ Propagación a múltiples módulos
✓ Versionado y rollback
✓ Base para panel administrativo

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
    achievement_id SERIAL KEY,
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

### 6. Sistema de Configuración Centralizada

Este es el corazón que hace que DianaBot sea manejable y coherente.

### 6.1 Arquitectura de Configuración Unificada

**Concepto de "Config Entity"**

En lugar de configurar elementos dispersos en múltiples sistemas, creamos "Config Entities" que son representaciones unificadas de conceptos del sistema. Por ejemplo, una "Experiencia Narrativa-Gamificada" es una Config Entity que automáticamente genera:

- Registros en la tabla de fragmentos narrativos
- Contenido en MongoDB
- Misiones asociadas en la tabla de misiones
- Items en la tienda y tabla de items
- Achievements relacionados
- Posts programados en canales

**Base de Datos de Configuración**

La tabla `config_templates` define tipos de Config Entities disponibles. Cada template especifica:

Campos requeridos y opcionales.
Validaciones de datos.
Relaciones con otros sistemas.
Acciones de propagación al guardar.

La tabla `config_instances` almacena instancias concretas de templates.

### 6.2 Flujos de Configuración Unificada

**Flujo: Crear Experiencia Narrativa-Gamificada Completa**

El administrador accede al panel unificado y selecciona "Crear Nueva Experiencia". El asistente guía paso a paso:

Paso 1 - Información Básica:
- Nombre de la experiencia: "El Secreto del Ático"
- Descripción: "Descubre lo que Lucien oculta en el ático prohibido"
- Tipo: Narrativa con Gamificación
- Requisitos: VIP, 50 besitos, poseer "Llave Maestra"

Paso 2 - Contenido Narrativo:
- Editor visual para crear 3-5 fragmentos interconectados
- Para cada fragmento:
  - Texto narrativo con preview
  - Decisiones con consecuencias
  - Media asociada (subir imágenes/audio)
  - Variables narrativas afectadas

Paso 3 - Recompensas Integradas:
Panel unificado que muestra todas las recompensas en un solo lugar:

```
Recompensas al Completar Experiencia:
├── Besitos: [100] ✓
├── Items Desbloqueados:
│   ├── [Seleccionar existente ▼] o [Crear nuevo +]
│   └── "Diario del Ático" (nuevo)
│       ├── Descripción: ...
│       ├── Categoría: Narrativo
│       └── Efecto: Desbloquea fragmento secreto F_SECRET_05
├── Achievements:
│   └── [✓] "Explorador del Ático" (existente)
│       └── Rewards: 50 besitos adicionales
└── Misiones Activadas:
    └── [Crear nueva +]
        └── "Investiga los hallazgos"
            ├── Descripción: ...
            └── Recompensa: Item "Fotografía Antigua"
```

El administrador define TODO en esta pantalla sin navegar a otras secciones.

Paso 4 - Programación de Publicación:
- ¿Publicar en qué canal? [VIP ▼]
- ¿Cuándo? [Inmediato / Programado: 2025-11-01 20:00]
- ¿Notificar usuarios? [✓ Sí]
- Plantilla de notificación: "¡Nueva experiencia disponible! El Secreto del Ático te espera..."

Paso 5 - Validación y Vista Previa:
El sistema valida automáticamente:
- ✓ Todos los fragmentos tienen al menos una decisión
- ✓ Items referenciados existen o serán creados
- ✓ Recompensas de besitos están en rango razonable (0-500)
- ⚠ Advertencia: Esta experiencia no tiene misiones recurrentes
- ✓ Coherencia narrativa verificada

Vista previa muestra cómo los usuarios experimentarán el contenido.

Paso 6 - Confirmación y Propagación:
Al confirmar, el sistema ejecuta en una transacción:

```python
def create_narrative_experience(config_data):
    with transaction.atomic():
        # 1. Crear nivel narrativo si no existe
        level = create_or_get_level(config_data['level_number'])
        
        # 2. Crear fragmentos en PostgreSQL
        fragments = []
        for frag_data in config_data['fragments']:
            fragment = NarrativeFragment.objects.create(
                level=level,
                fragment_key=generate_key(frag_data['title']),
                title=frag_data['title'],
                unlock_conditions=config_data['requirements'],
                rewards=config_data['rewards']
            )
            fragments.append(fragment)
            
            # 3. Crear contenido detallado en MongoDB
            mongo_db.narrative_content.insert_one({
                'fragment_key': fragment.fragment_key,
                'content': frag_data['content'],
                'decisions': frag_data['decisions']
            })
        
        # 4. Crear items nuevos
        created_items = []
        for item_data in config_data['new_items']:
            item = Item.objects.create(**item_data)
            created_items.append(item)
        
        # 5. Vincular achievements existentes
        for achievement_key in config_data['achievements']:
            achievement = Achievement.objects.get(achievement_key=achievement_key)
            # Vincular al primer fragmento de la experiencia
            fragments[0].rewards['achievements'].append(achievement.achievement_id)
            fragments[0].save()
        
        # 6. Crear misiones activadas
        for mission_data in config_data['activated_missions']:
            mission = Mission.objects.create(
                **mission_data,
                requirements={'completed_fragments': [f.fragment_id for f in fragments]}
            )
        
        # 7. Programar publicación en canal
        if config_data['publish_immediately']:
            publish_to_channel(config_data['channel'], fragments[0])
        else:
            schedule_post(
                channel=config_data['channel'],
                content=fragments[0],
                scheduled_for=config_data['publish_at']
            )
        
        # 8. Guardar config instance para historial
        ConfigInstance.objects.create(
            template=config_data['template'],
            instance_data=config_data,
            created_by=config_data['admin_id'],
            status='active'
        )
        
        # 9. Publicar evento para otros sistemas
        event_bus.publish('narrative_experience_created', {
            'experience_name': config_data['name'],
            'fragments': [f.fragment_key for f in fragments],
            'items': [i.item_key for i in created_items]
        })
        
        return {
            'success': True,
            'fragments_created': len(fragments),
            'items_created': len(created_items),
            'experience_id': fragments[0].fragment_id
        }
```

Todo esto sucede en una sola operación atómica. Si cualquier paso falla, nada se guarda (rollback automático).

### 6.3 Plantillas y Asistentes

**Plantillas Predefinidas**

El sistema viene con plantillas para casos de uso comunes:

"Experiencia Narrativa Simple": 3 fragmentos lineales + recompensas básicas.
"Misión con Trivia": Misión que incluye trivia integrada como parte de los requisitos.
"Evento de Canal Gamificado": Post con reacciones que otorgan besitos + mini-competencia.
"Cadena de Misiones": Serie de 5 misiones donde completar una desbloquea la siguiente.
"Subasta de Item Legendario": Setup completo para subasta including item, anuncios, y post-subasta.

Los administradores pueden:
- Usar plantillas tal cual
- Modificarlas según necesidades
- Crear plantillas personalizadas para reusar

**Asistentes Inteligentes**

Los asistentes guían al administrador con validación en tiempo real y sugerencias contextuales.

Asistente de Coherencia Narrativa:
Mientras el administrador escribe fragmentos, el asistente analiza:
- "Este fragmento menciona 'el medallón de Diana', pero no hay un item con ese nombre. ¿Crear item automáticamente?"
- "Has usado el flag 'trusts_lucien' pero ningún fragmento anterior lo establece. ¿Agregar decisión que lo active?"
- "El fragmento F_008 tiene decisiones que llevan a F_010 y F_012, pero F_009 no es alcanzable. ¿Es intencional?"

Asistente de Balance Económico:
Analiza recompensas y alerta sobre desequilibrios:
- "Esta experiencia otorga 500 besitos. El promedio de experiencias similares otorga 150. ¿Confirmar?"
- "El item 'Espada Legendaria' cuesta 50 besitos, pero items legendarios promedio cuestan 300+. ¿Ajustar precio?"
- "Usuarios completarán esta misión en ~5 minutos pero otorga 200 besitos. Recompensa puede ser excesiva."

Asistente de Engagement:
Sugiere mejoras para aumentar interacción:
- "Esta experiencia no tiene elementos sociales. ¿Agregar misión que requiera interacción con otro usuario?"
- "Fragmentos sin media visual tienen 40% menos engagement. ¿Agregar imágenes?"
- "Considera agregar decisión de moralidad para aumentar rejugabilidad."

### 6.4 API de Configuración Centralizada

La API expone endpoints para gestionar configuración programáticamente.

**Endpoints Principales**

```
POST /api/config/templates
GET /api/config/templates/{template_id}
POST /api/config/instances
PUT /api/config/instances/{instance_id}
DELETE /api/config/instances/{instance_id}
POST /api/config/validate
POST /api/config/propagate/{instance_id}
GET /api/config/dependencies/{instance_id}
```

**Validación antes de Guardar**

El endpoint `/api/config/validate` permite verificar configuración sin guardarla:

```python
{
  "template": "narrative_experience",
  "data": {
    "name": "Test Experience",
    "fragments": [...],
    "rewards": {...}
  }
}
```

Respuesta:

```python
{
  "valid": true,
  "warnings": [
    {
      "field": "rewards.besitos",
      "message": "Value is above recommended range",
      "severity": "warning"
    }
  ],
  "errors": [],
  "suggestions": [
    {
      "field": "fragments[2].decisions",
      "message": "Consider adding a third decision for more depth",
      "auto_fix_available": true
    }
  ]
}
```

**Propagación Controlada**

Cuando se actualiza una configuración, el administrador puede controlar qué cambios se propagan:

```python
PUT /api/config/instances/123
{
  "data": {
    "rewards": {
      "besitos": 150  // aumentado de 100
    }
  },
  "propagation_options": {
    "apply_to_existing_users": false,  // solo nuevos usuarios
    "notify_affected_users": true,
    "create_migration": true,  // guardar cambio como migración
    "rollback_on_error": true
  }
}
```

El sistema ejecuta la propagación y responde con reporte detallado:

```python
{
  "success": true,
  "changes_applied": [
    "Updated fragments table: 3 records",
    "Updated MongoDB narrative_content: 3 documents",
    "Scheduled notification to 45 affected users",
    "Created migration record: MIG_2025_10_28_001"
  ],
  "rollback_token": "RB_xyz789",  // para rollback manual si necesario
  "affected_systems": ["narrativa", "gamificación", "admin_canales"]
}
```

### 6.5 Panel de Administración Unificado

**Dashboard Principal**

El dashboard muestra vista holística del sistema:

```
┌─────────────────────────────────────────────────────┐
│  DianaBot - Dashboard Administrativo                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  📊 Métricas en Tiempo Real                        │
│  ├─ Usuarios activos (últimas 24h): 1,247         │
│  ├─ Suscriptores VIP: 156 (↑ 12 esta semana)      │
│  ├─ Besitos en circulación: 3,456,789             │
│  └─ Fragmentos completados hoy: 3,421              │
│                                                     │
│  ⚠️ Alertas del Sistema                            │
│  ├─ 3 suscripciones expiran en 24h                │
│  ├─ Misión "Búsqueda Semanal" completada por 78%  │
│  └─ Item "Espada Legendaria" sin stock en tienda  │
│                                                     │
│  🎯 Acciones Rápidas                               │
│  ├─ [+ Crear Experiencia]                         │
│  ├─ [📅 Programar Evento]                         │
│  ├─ [🎁 Lanzar Recompensa Masiva]                 │
│  └─ [📊 Ver Analíticas Detalladas]                │
│                                                     │
│  📝 Configuraciones Recientes                      │
│  ├─ "El Misterio del Jardín" - hace 2 horas       │
│  │   Status: Activo | Usuarios: 89               │
│  ├─ "Misión Halloween" - hace 5 horas             │
│  │   Status: Programado para 31/10 00:00         │
│  └─ "Subasta Corona Dorada" - hace 1 día          │
│      Status: Completado | Ganador: @usuario123   │
└─────────────────────────────────────────────────────┘
```

**Navegación Contextual**

El panel usa navegación inteligente que comprende relaciones:

Al ver un fragmento narrativo, el panel muestra enlaces directos a:
- Items que desbloquea
- Misiones que activa
- Posts de canal asociados
- Usuarios que lo han completado
- Analíticas específicas de ese fragmento

Al ver una misión, muestra:
- Fragmentos narrativos relacionados
- Items como recompensa
- Usuarios con la misión activa/completada
- Tasa de completación histórica

Esto elimina la necesidad de navegar por múltiples secciones para entender cómo un elemento se relaciona con el resto del sistema.

**Editor Visual de Flujos**

Para experiencias complejas, el panel incluye editor visual de flujos:

```
[Fragmento 1: Entrada] 
    ├─[Decisión A]─→ [Fragmento 2A: Confianza]
    │                    ├─[Obtiene: Medallón]
    │                    └─[Activa: Misión "Buscar Verdad"]
    │
    └─[Decisión B]─→ [Fragmento 2B: Cautela]
                         ├─[Obtiene: 50 besitos]
                         └─[Desbloquea: Fragmento Secreto]
```

El administrador puede:
- Arrastrar y conectar fragmentos visualmente
- Ver condiciones de desbloqueo en cada conexión
- Identificar caminos huérfanos o sin salida
- Simular recorridos de usuario

### 6.6 Historial y Versionado de Configuración

**Control de Versiones**

Cada cambio a configuración se versiona automáticamente:

```sql
CREATE TABLE config_versions (
    version_id SERIAL PRIMARY KEY,
    config_instance_id INTEGER REFERENCES config_instances(instance_id),
    version_number INTEGER NOT NULL,
    changed_by INTEGER,
    changes JSONB,  -- diff de cambios
    change_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    can_rollback BOOLEAN DEFAULT TRUE
);
```

El administrador puede:
- Ver historial completo de cambios a cualquier configuración
- Comparar versiones (diff visual)
- Rollback a versión anterior con un click
- Clonar versión antigua como nueva configuración

**Audit Trail**

Todo cambio administrativo se registra para accountability:

```
Usuario: admin@dianabot.com
Acción: Modificó experiencia "El Secreto del Ático"
Cambios:
  - rewards.besitos: 100 → 150 (+50)
  - fragments[1].decisions: agregó tercera opción
Razón: "Balance de recompensas tras feedback de usuarios"
Timestamp: 2025-10-28 14:23:45
IP: 192.168.1.100
```

### 6.7 Sistema de Validación y Coherencia

**Validadores de Integridad**

El sistema ejecuta validadores automáticos que verifican coherencia:

Validador de Referencias:
- Todos los item_ids referenciados existen en la tabla items
- Todos los achievement_keys referenciados existen
- Todos los fragment_keys en decisiones existen

Validador de Ciclos:
- No hay ciclos infinitos en la narrativa (fragmento A lleva a B, B a C, C a A)
- Identifica fragmentos sin salida

Validador de Balance:
- Recompensas de besitos están en rangos aceptables
- Items no tienen precios negativos o cero
- Misiones tienen requisitos alcanzables

Validador de Accesibilidad:
- Todo contenido VIP está protegido por verificación de suscripción
- Contenido gratuito no requiere accidentalmente VIP
- No hay fragmentos que requieren items imposibles de obtener

**Simulador de Experiencias**

Antes de activar una configuración, el administrador puede simular:

```python
POST /api/config/simulate
{
  "instance_id": 123,
  "user_profile": {
    "besitos": 200,
    "inventory": ["item_001", "item_005"],
    "completed_fragments": ["f_001", "f_002", "f_003"],
    "is_vip": true
  }
}
```

El simulador ejecuta la experiencia como si fuera ese usuario y retorna:

```python
{
  "simulation_result": {
    "accessible": true,
    "blocked_fragments": [],
    "path_taken": ["f_010", "f_011", "f_012"],
    "decisions_available": [
      {"fragment": "f_010", "decisions": 2},
      {"fragment": "f_011", "decisions": 3}
    ],
    "rewards_earned": {
      "besitos": 150,
      "items": ["item_010"],
      "achievements": ["achievement_003"]
    },
    "final_state": {
      "besitos": 350,
      "inventory": ["item_001", "item_005", "item_010"]
    }
  }
}
```

Esto permite detectar problemas antes de que usuarios reales los encuentren.