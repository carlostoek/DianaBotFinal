# DianaBot: Investigación Técnica Integral

## Índice
1. Arquitectura General del Sistema
2. Plataforma y Tecnologías
3. Módulo de Narrativa Inmersiva
4. Módulo de Gamificación
5. Módulo de Administración de Canales
6. Sistema de Configuración Centralizada
7. Integración y Flujos Cruzados
8. Seguridad y Escalabilidad
9. Monetización y Roles

---

## 1. Arquitectura General del Sistema

### 1.1 Propuesta Arquitectónica: Event-Driven Modular Architecture

La arquitectura más apropiada para DianaBot combina tres patrones fundamentales que trabajan en armonía. Primero, necesitamos una arquitectura basada en eventos porque los tres módulos deben comunicarse sin crear dependencias rígidas entre ellos. Cuando un usuario toma una decisión narrativa, ese evento debe poder desencadenar recompensas en gamificación sin que el módulo narrativo necesite conocer los detalles internos del sistema de besitos.

Segundo, adoptamos un enfoque de capas limpias donde cada módulo tiene su propia lógica de negocio independiente pero expone interfaces claras para la comunicación. Esto significa que el módulo de narrativa puede operar completamente solo si fuera necesario, pero cuando está integrado, puede enviar y recibir eventos del resto del sistema.

Tercero, implementamos un patrón de repositorio centralizado para la configuración, lo que permite que todos los módulos consulten una única fuente de verdad para reglas, recompensas y condiciones de desbloqueo.

### 1.2 Componentes Principales

**Core del Sistema (Event Bus)**
El corazón de DianaBot es un bus de eventos que actúa como sistema nervioso central. Cada módulo publica eventos cuando ocurren acciones importantes y se suscribe a eventos que le interesan. Por ejemplo, cuando un usuario completa un fragmento narrativo, el módulo de narrativa publica un evento "NarrativeFragmentCompleted". El módulo de gamificación escucha este evento y otorga automáticamente los besitos correspondientes. El módulo de administración registra el progreso para análisis.

**Configuration Manager (Gestor de Configuración Unificada)**
Este componente es absolutamente crítico para cumplir con el requisito de configuración centralizada. Funciona como una capa de abstracción que permite definir elementos complejos como "experiencias" que automáticamente crean registros en narrativa, gamificación y administración de forma coordinada. Cuando un administrador crea una nueva misión que desbloquea un fragmento narrativo, el Configuration Manager asegura que ambos sistemas estén sincronizados desde el momento de la creación.

**Estado del Usuario (User State Manager)**
Mantiene el contexto completo de cada usuario a través de todos los módulos. Esto incluye su posición en la narrativa, su inventario, sus besitos, sus logros y su estado de suscripción. Este componente garantiza consistencia cuando diferentes módulos necesitan verificar o modificar el estado del usuario.

### 1.3 Diagrama de Comunicación

```
┌─────────────────────────────────────────────────────┐
│           Configuration Manager (Unificado)         │
│    - Plantillas de experiencias                     │
│    - Validación de coherencia                       │
│    - Propagación de cambios                         │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │    Event Bus      │
         │  (Pub/Sub System) │
         └─────────┬─────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐    ┌───▼────┐    ┌───▼────┐
│Narrativa│◄──►│Gamifi- │◄──►│Admin.  │
│         │    │cación  │    │Canales │
└───┬────┘    └───┬────┘    └───┬────┘
    │             │             │
    └─────────────┼─────────────┘
                  │
          ┌───────▼───────┐
          │  User State   │
          │   Manager     │
          └───────────────┘
```

### 1.4 Patrones de Diseño Recomendados

**Command Pattern para Acciones de Usuario**
Cada acción del usuario (tomar decisión, comprar ítem, reaccionar) se encapsula como un comando. Esto permite deshacer acciones, registrar historial y procesar comandos de manera asíncrona si el sistema está bajo carga.

**Observer Pattern para Eventos**
Los módulos actúan como observadores de eventos específicos. El módulo de narrativa observa eventos de compra de ítems para verificar si se deben desbloquear nuevos fragmentos. El módulo de gamificación observa eventos narrativos para otorgar recompensas.

**Strategy Pattern para Condiciones de Desbloqueo**
Las condiciones para desbloquear contenido (tener X besitos, poseer cierto ítem, tener badge específico) se implementan como estrategias intercambiables. Esto facilita agregar nuevos tipos de condiciones sin modificar el código existente.

**Repository Pattern para Acceso a Datos**
Cada módulo accede a la base de datos a través de repositorios que abstraen las consultas SQL. Esto permite cambiar la base de datos subyacente sin afectar la lógica de negocio.

---

## 2. Plataforma y Tecnologías

### 2.1 Framework del Bot: python-telegram-bot vs Telethon vs pyrogramming

Después de analizar las características requeridas, la biblioteca más apropiada es **python-telegram-bot (PTB) v20+**. Esta elección se fundamenta en varios aspectos críticos para DianaBot.

Primero, PTB ofrece manejo nativo de handlers complejos que se adaptan perfectamente a la estructura de comandos, callbacks inline y reacciones que necesitamos. Su sistema de ConversationHandler es ideal para la narrativa ramificada, permitiendo mantener estados de conversación de manera natural.

Segundo, PTB tiene soporte robusto para Jobs y scheduling, esencial para misiones diarias, recordatorios de suscripción VIP y eventos programados en canales. Su JobQueue integrada puede manejar tareas recurrentes sin dependencias externas adicionales.

Tercero, la documentación y comunidad de PTB son excepcionales, lo que reduce significativamente el tiempo de desarrollo y resolución de problemas.

**Estructura Tecnológica Recomendada:**

```
Backend: Python 3.11+
Bot Framework: python-telegram-bot 20.x
Web Framework: FastAPI (para panel admin y webhooks)
Task Queue: Celery con Redis (para procesos pesados)
Cache: Redis (para estado de sesiones y rate limiting)
```

### 2.2 Base de Datos: Enfoque Híbrido

La naturaleza de DianaBot requiere un enfoque híbrido que aproveche las fortalezas de diferentes paradigmas de almacenamiento.

**PostgreSQL como Base de Datos Principal**

PostgreSQL es ideal para los datos relacionales y transaccionales de DianaBot. Su soporte para JSONB permite flexibilidad cuando la necesitamos sin sacrificar integridad referencial. Veamos por qué es la elección correcta:

Para el estado del usuario, necesitamos garantizar consistencia transaccional. Cuando un usuario gasta besitos para comprar un ítem, debemos asegurar que el balance de besitos se decremente exactamente en la misma transacción que agrega el ítem al inventario. PostgreSQL maneja esto perfectamente con sus garantías ACID.

El progreso narrativo se beneficia enormemente de las relaciones. Un usuario está en un fragmento, ese fragmento pertenece a un nivel, ese nivel tiene condiciones de desbloqueo. Estas relaciones naturales se modelan eficientemente en SQL.

Las suscripciones VIP requieren consultas complejas con fechas (usuarios que expiran en 3 días, usuarios activos en rango de fechas). PostgreSQL excele en estas operaciones con índices apropiados.

**MongoDB como Almacén de Configuración Dinámica**

MongoDB complementa a PostgreSQL para aspectos específicos donde la flexibilidad de esquema es valiosa:

Los fragmentos narrativos pueden tener estructuras variables. Un fragmento puede tener dos decisiones, otro puede tener cinco, algunos incluyen minijuegos. Almacenar esto en JSONB de PostgreSQL es posible, pero MongoDB ofrece consultas más expresivas sobre estructuras anidadas.

Las plantillas de configuración del sistema unificado se benefician de la flexibilidad de documentos. Una plantilla de "experiencia narrativa-gamificada" puede tener campos opcionales según el tipo de experiencia.

**Redis para Estado en Tiempo Real**

Redis maneja todo lo que necesita velocidad extrema:

El estado de conversación activa (en qué fragmento está el usuario AHORA) se cachea en Redis. Cuando el usuario toma una decisión, consultamos Redis primero, evitando latencia de base de datos.

Rate limiting de acciones (prevenir spam de compras o decisiones) se implementa eficientemente con INCR y EXPIRE de Redis.

Locks distribuidos para operaciones críticas como subastas en tiempo real previenen condiciones de carrera.

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

### 2.4 Integración con API de Telegram

**Manejo de Canales y Suscripciones**

Telegram proporciona APIs específicas para gestionar membresías en canales, pero hay aspectos críticos que debemos entender profundamente.

Para validar suscripciones VIP, usamos el método `getChatMember` que devuelve el estado de un usuario en un canal específico. Sin embargo, esta validación debe ser inteligente y no bloquear la experiencia del usuario. Implementamos un sistema de caché donde verificamos la membresía una vez por sesión y guardamos el resultado en Redis con un TTL de 1 hora. Solo re-verificamos si el usuario intenta acceder a contenido VIP o si ha pasado el tiempo de caché.

La expulsión automática al expirar suscripción requiere un job programado que consulta la base de datos cada hora buscando suscripciones que expiran. Para cada una, llamamos a `banChatMember` con `revoke_messages=False` para remover al usuario sin eliminar su historial de mensajes. Inmediatamente después, enviamos un mensaje directo al usuario informándole y ofreciendo renovación.

**Reacciones y Engagement**

Las reacciones a mensajes son una característica relativamente nueva en Telegram. Para vincularlas con gamificación, usamos `MessageReactionUpdated` handlers que detectan cuando un usuario agrega una reacción específica. Por ejemplo, si el administrador configura que reaccionar con ❤️ a un mensaje narrativo otorga 2 besitos, el handler verifica que es la primera vez que ese usuario reacciona a ese mensaje específico, previene duplicados consultando Redis, y otorga la recompensa.

**Botones Inline y Callbacks**

Los botones inline son el mecanismo principal de interacción para decisiones narrativas y compras. Cada botón incluye un `callback_data` que codifica la acción. Por ejemplo: `"decision:fragment_005:choice_b:user_12345"`. El handler de callback decodifica esto, verifica que el usuario tenga acceso al fragmento, procesa la decisión, actualiza el estado y responde con el siguiente fragmento.

Para prevenir que usuarios maliciosos manipulen callbacks, incluimos un hash HMAC en cada callback_data que valida la integridad del mensaje.

---

## 3. Módulo de Narrativa Inmersiva

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

### 3.3 Desbloqueos Condicionales Complejos

Los desbloqueos van más allá de simples verificaciones. Un fragmento podría tener condiciones como:

```json
{
  "unlock_conditions": {
    "operator": "AND",
    "conditions": [
      {
        "type": "subscription",
        "value": "vip"
      },
      {
        "operator": "OR",
        "conditions": [
          {
            "type": "besitos",
            "operator": ">=",
            "value": 100
          },
          {
            "type": "has_item",
            "item_key": "golden_invitation"
          }
        ]
      },
      {
        "type": "completed_fragments",
        "fragments": ["fragment_012", "fragment_013"],
        "operator": "ALL"
      },
      {
        "type": "narrative_flag",
        "flag": "earned_diana_trust",
        "value": true
      }
    ]
  }
}
```

Esta condición se lee: "El usuario debe ser VIP Y (tener 100+ besitos O poseer el item 'golden_invitation') Y haber completado los fragmentos 12 y 13 Y tener el flag 'earned_diana_trust' activo".

El motor evalúa estas condiciones recursivamente usando un intérprete de expresiones booleanas. Cuando un desbloqueo falla, el motor no solo dice "acceso denegado", sino que explica específicamente qué falta: "Necesitas la invitación dorada o 100 besitos para continuar".

### 3.4 Fragmentos Ocultos y Metajuego

Algunos fragmentos son "secretos" y no aparecen en el flujo normal. Los usuarios los descubren mediante:

Pistas en otros canales: Un mensaje en el canal VIP contiene un código encriptado. Resolverlo revela el `fragment_key` de un fragmento secreto.

Combinaciones de items: Poseer simultáneamente "ancient_map" y "decoder_ring" desbloquea automáticamente un fragmento oculto sobre el pasado de Lucien.

Exploración de paths alternativos: Si el usuario toma decisiones contraintuitivas en varios fragmentos, desbloquea un "bad ending" alternativo.

El motor verifica periódicamente si el estado del usuario satisface condiciones de fragmentos ocultos y los hace aparecer dinámicamente en el mapa de narrativa del usuario.

---

## 4. Módulo de Gamificación

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

El `select_for_update()` asegura que nadie más puede modificar ese balance hasta que la transacción complete.

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

### 4.3 Inventario (Mochila) y Sistema de Items

El inventario es más que una lista de posesiones, es un sistema que conecta gamificación con narrativa.

**Categorías de Items**

Items Narrativos (Narrative Keys):
- Desbloquean fragmentos específicos
- Ejemplos: "Llave del Ático Prohibido", "Diario de Diana Joven"
- No se consumen al usar, permanecen en inventario

Items Consumibles:
- Se usan una vez y desaparecen
- Ejemplos: "Poción de Doble Besitos" (duplica besitos ganados por 1 hora)
- Afectan temporalmente las mecánicas de juego

Coleccionables:
- No tienen función mecánica, solo valor de colección
- Completan sets que otorgan achievements
- Ejemplos: "Fragmento de Espejo Antiguo" (5 fragmentos forman espejo completo)

Power-ups:
- Mejoran capacidades temporalmente
- Ejemplos: "Intuición de Lucien" (revela consecuencias de decisiones por 3 usos)

Items de Subasta:
- Únicos o muy raros
- Solo obtenibles en subastas
- Ejemplos: "Retrato Firmado de Diana" (solo 1 existe en todo el sistema)

**Efectos Cruzados Narrativa-Items**

Los items no son estáticos. Su presencia en el inventario puede:

Cambiar diálogos: Si tienes "Anillo de Compromiso Antiguo", Lucien comenta sobre él.

Desbloquear opciones de decisión: Una tercera opción aparece solo si posees "Pergamino de Ritual".

Modificar endings: Tener ciertos items combinados lleva a finales alternativos.

Activar fragmentos secretos: Poseer "Mapa del Laberinto" + "Linterna Eterna" revela entrada a nivel oculto.

**Gestión de Inventario**

El inventario tiene mecánicas propias:

Límite de espacio: Los usuarios free tienen 20 slots, VIP tienen 50. Esto incentiva decisiones sobre qué conservar.

Almacén: Items que no caben en inventario activo van a almacén, pero no afectan narrativa hasta ser transferidos.

Intercambio: Usuarios pueden intercambiar items con otros (por besitos o por trueque), creando economía secundaria.

Reciclaje: Items no deseados pueden "reciclarse" por una porción de su valor en besitos.

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

### 4.5 Sistema de Trivias

Las trivias combinan educación sobre el lore narrativo con recompensas inmediatas.

**Formato de Trivias**

Trivias rápidas: Una pregunta, 4 opciones, 30 segundos para responder. Aparecen aleatoriamente en canales.

Trivia diaria: Publicada a hora fija, todos los usuarios tienen 24 horas para responder. Recompensas basadas en velocidad de respuesta.

Trivia en cadena: 5 preguntas consecutivas. Respuestas correctas consecutivas multiplican recompensa (2x, 3x, 5x).

Trivia PvP: Dos usuarios compiten respondiendo la misma secuencia. El más rápido y preciso gana.

**Categorías de Preguntas**

Lore narrativo: "¿En qué año se construyó la mansión de Lucien?"

Detalles de personajes: "¿Cuál es el color favorito de Diana?"

Decisiones narrativas: "¿Qué pasó cuando elegiste confrontar a Lucien en el capítulo 3?"

Meta-juego: "¿Cuántos besitos cuesta el item 'Rosa Eterna'?"

**Recompensas Dinámicas**

Las trivias ajustan recompensas según múltiples factores:

Dificultad: Preguntas difíciles otorgan más besitos.

Velocidad: Responder en 5 segundos vs 25 segundos multiplica recompensa.

Racha: Responder correctamente 10 trivias seguidas otorga bonus.

Rareza: Primera persona en responder correctamente una trivia ultra-rara recibe item único.

**Generación de Preguntas**

Las trivias pueden ser:

Estáticas: Pre-escritas por administradores en MongoDB.

Dinámicas: Generadas basándose en el progreso narrativo del usuario. "¿Qué decisión tomaste en el fragmento que acabas de completar?"

Adaptativas: El sistema detecta qué temas el usuario responde mejor y ajusta dificultad.

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

---

## 5. Módulo de Administración de Canales

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

### 5.3 Sistema de Reacciones Vinculadas

Las reacciones no son solo feedback, son parte del gameplay.

**Configuración de Reacciones Gamificadas**

Al publicar un post, el administrador puede configurar:

```json
{
  "post_id": 456,
  "reaction_rewards": {
    "❤️": {
      "besitos": 2,
      "limit_per_user": 1,
      "achievement_trigger": {
        "achievement_key": "romantic_soul",
        "condition": "react_heart_50_times"
      }
    },
    "🔥": {
      "besitos": 3,
      "limit_per_user": 1,
      "unlock_hint": "You seem passionate. Check your DMs."
    },
    "🤔": {
      "besitos": 1,
      "trigger_trivia": "trivia_about_this_post"
    }
  }
}
```

Cuando un usuario reacciona:
1. El bot recibe `MessageReactionUpdated`
2. Verifica configuración de reacciones para ese post
3. Verifica que el usuario no haya excedido límites
4. Otorga recompensas definidas
5. Dispara triggers especiales (enviar DM, activar trivia, etc.)

**Análisis de Engagement**

El sistema recopila métricas de reacciones:

Posts con más reacciones de cada tipo.
Usuarios más activos reaccionando.
Correlación entre tipo de contenido y reacciones recibidas.
Efectividad de reacciones gamificadas vs no gamificadas.

Estas métricas informan decisiones sobre qué tipo de contenido publicar.

### 5.4 Moderación y Control de Acceso

**Sistema de Roles**

Además de Free vs VIP, el sistema maneja roles administrativos:

Owner: Control total del bot y configuración.
Admin: Puede publicar contenido, gestionar suscripciones, moderar usuarios.
Content Creator: Puede crear y programar contenido pero no acceder a configuración del sistema.
Moderator: Puede moderar usuarios (banear, advertir) pero no modificar contenido.

Los permisos se verifican antes de cada acción administrativa usando decorators:

```python
@require_role('admin')
def publish_content(user_id, content):
    # Solo admins pueden ejecutar esto
    pass
```

**Moderación de Usuarios**

El sistema incluye herramientas para manejar usuarios problemáticos:

Advertencias: Sistema de tres strikes antes de ban.
Bans temporales: Suspender acceso por días/semanas.
Bans permanentes: Bloqueo total con opción de apelar.
Shadowban: Usuario cree que participa normalmente pero sus acciones no afectan al sistema.

Cada acción de moderación se registra con razón, evidencia y admin responsable para accountability.

---

## 6. Sistema de Configuración Centralizada

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

---

## 7. Integración y Flujos Cruzados

La verdadera potencia de DianaBot emerge cuando los módulos trabajan en conjunto perfectamente sincronizados.

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

**Flujo: Usuario Gana Subasta**

1. Subasta termina, el módulo de Gamificación determina ganador
2. Gamificación publica evento: `gamification.auction_won`

```python
event_bus.publish('gamification.auction_won', {
    'user_id': 67890,
    'auction_id': 42,
    'item_key': 'legendary_sword',
    'final_bid': 750
})
```

3. Gamificación ejecuta transacción:
   - Debita 750 besitos del ganador
   - Agrega item al inventario del ganador
   - Retorna besitos a otros pujadores

4. Módulo de Narrativa escucha evento y:
   - Verifica si el item ganado desbloquea fragmentos narrativos
   - Si sí, actualiza disponibilidad de fragmentos para ese usuario
   - Publica evento: `narrative.content_unlocked`

5. Módulo de Administración escucha evento y:
   - Envía notificación al ganador
   - Envía notificación a otros participantes
   - Registra resultados de subasta para analíticas
   - Programa siguiente subasta si es recurrente

6. Sistema de Achievements escucha evento y:
   - Verifica si usuario desbloqueó "Primera Subasta Ganada"
   - Verifica si usuario desbloqueó "Coleccionista de Legendarios" (por poseer 5 items legendarios)

**Flujo: Suscripción VIP Expira**

1. Job programado detecta suscripción que expira
2. Módulo de Administración publica evento: `admin.subscription_expired`

```python
event_bus.publish('admin.subscription_expired', {
    'user_id': 11111,
    'subscription_type': 'monthly',
    'expiry_date': '2025-10-28T23:59:59Z',
    'had_auto_renew': false
})
```

3. Administración ejecuta:
   - Actualiza status de suscripción a 'expired'
   - Remueve usuario del canal VIP
   - Envía mensaje de despedida con link de renovación

4. Módulo de Narrativa escucha evento y:
   - Marca fragmentos VIP como inaccesibles para ese usuario
   - Si usuario está en medio de fragmento VIP, guarda progreso pero bloquea continuación
   - Publica evento: `narrative.access_revoked`

5. Módulo de Gamificación escucha evento y:
   - Desactiva misiones exclusivas VIP del usuario
   - Mantiene items y besitos ganados (no se pierden al expirar VIP)
   - Marca achievements VIP como "inaccesibles actualmente"

6. Sistema de Notificaciones:
   - Programa reminder en 7 días: "Te extrañamos, renueva tu VIP..."
   - Programa reminder en 30 días con oferta especial

### 7.3 Handlers de Eventos Complejos

Algunos eventos desencadenan lógica compleja que involucra múltiples sistemas.

**Handler: Decision Made → Cascade Effects**

```python
@event_handler('narrative.decision_made')
def handle_decision_cascade(event_data):
    """
    Maneja los efectos en cascada de una decisión narrativa
    """
    user_id = event_data['user_id']
    fragment_key = event_data['fragment_key']
    decision = event_data['decision_made']
    
    # 1. Obtener configuración de consecuencias
    fragment = get_fragment(fragment_key)
    consequences = fragment.get_decision_consequences(decision)
    
    # 2. Aplicar cambios narrativos
    if 'narrative_flags' in consequences:
        update_user_narrative_flags(user_id, consequences['narrative_flags'])
    
    if 'trust_changes' in consequences:
        update_trust_levels(user_id, consequences['trust_changes'])
    
    # 3. Otorgar recompensas inmediatas
    if 'immediate_rewards' in consequences:
        rewards = consequences['immediate_rewards']
        
        if 'besitos' in rewards:
            grant_besitos(user_id, rewards['besitos'], source='decision_reward')
        
        if 'items' in rewards:
            for item_key in rewards['items']:
                add_item_to_inventory(user_id, item_key)
        
        if 'unlock_fragments' in rewards:
            for fragment_key in rewards['unlock_fragments']:
                unlock_fragment(user_id, fragment_key)
    
    # 4. Activar misiones condicionales
    if 'trigger_missions' in consequences:
        for mission_key in consequences['trigger_missions']:
            assign_mission(user_id, mission_key)
    
    # 5. Verificar achievements
    check_decision_based_achievements(user_id, fragment_key, decision)
    
    # 6. Publicar eventos derivados
    if consequences.get('important', False):
        event_bus.publish('narrative.major_decision', {
            'user_id': user_id,
            'decision': decision,
            'consequences': consequences
        })
```

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

### 7.4 Manejo de Fallos y Resiliencia

Los eventos pueden fallar al procesarse. El sistema debe ser resiliente:

**Dead Letter Queue**

Si un handler falla repetidamente, el evento va a una Dead Letter Queue para revisión manual:

```python
class ResilientEventHandler:
    def __init__(self, handler_func, max_retries=3):
        self.handler_func = handler_func
        self.max_retries = max_retries
    
    def handle(self, event):
        retries = 0
        while retries < self.max_retries:
            try:
                self.handler_func(event)
                return True
            except Exception as e:
                retries += 1
                log_error(f"Handler failed (attempt {retries})", e)
                
                if retries < self.max_retries:
                    time.sleep(2 ** retries)  # exponential backoff
                else:
                    # Mover a Dead Letter Queue
                    self.move_to_dlq(event, str(e))
                    return False
    
    def move_to_dlq(self, event, error):
        redis_client.lpush('dianabot:dlq', json.dumps({
            'event': event,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }))
        
        # Notificar a administradores
        notify_admins('Event processing failed', event, error)
```

**Idempotencia**

Los handlers deben ser idempotentes (ejecutarlos múltiples veces con el mismo evento produce el mismo resultado):

```python
@idempotent_handler
def grant_besitos_handler(event_data):
    """
    Este handler es idempotente usando el event_id como deduplication key
    """
    event_id = event_data['event_id']
    user_id = event_data['user_id']
    amount = event_data['amount']
    
    # Verificar si ya procesamos este evento
    if redis_client.exists(f'processed_event:{event_id}'):
        log_info(f"Event {event_id} already processed, skipping")
        return
    
    # Procesar
    grant_besitos(user_id, amount)
    
    # Marcar como procesado (expira en 7 días)
    redis_client.setex(
        f'processed_event:{event_id}', 
        604800,  # 7 días en segundos
        '1'
    )
```

---

## 8. Seguridad y Escalabilidad

### 8.1 Seguridad

**Protección de Datos de Usuario**

Los datos de usuarios deben protegerse rigurosamente:

Encriptación en reposo: Datos sensibles en la base de datos se encriptan usando AES-256. Esto incluye información de pago, información personal identificable, y mensajes privados.

Encriptación en tránsito: Todas las comunicaciones con la API de Telegram usan HTTPS/TLS 1.3.

Tokens y Secretos: El bot token de Telegram nunca se hardcodea, siempre se almacena en variables de entorno o servicios de gestión de secretos como AWS Secrets Manager o HashiCorp Vault.

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

Transacciones Atómicas: Todas las operaciones con besitos usan transacciones de base de datos para prevenir duplicación o pérdida.

Audit Logs Inmutables: Cada transacción de besitos genera registro que no puede editarse ni eliminarse, solo agregarse.

**Control de Acceso VIP

# Verificar si item desbloquea contenido
            check_unlocks_by_item(user_id, item_key)
    
    # Verificar achievements
    check_fragment_achievements(user_id, fragment_key)
```

6. Sistema verifica si María desbloqueó achievement "Primera Decisión Confiada":
```python
def check_fragment_achievements(user_id, fragment_key):
    fragment = get_fragment(fragment_key)
    
    # Achievement: completar primer fragmento con decisión confiada
    user_progress = get_user_progress(user_id)
    if user_progress.decisions_confident == 1:  # primera vez
        unlock_achievement(user_id, 'first_confident_decision')
```

7. Achievement desbloqueado publica evento:
```python
event_bus.publish('gamification.achievement_unlocked', {
    'user_id': 67890,
    'achievement_key': 'first_confident_decision'
})
```

8. Handler de achievement otorga recompensas adicionales:
```python
achievement = Achievement.objects.get(achievement_key='first_confident_decision')
# Otorga 25 besitos + item "Badge de Valentía"
grant_besitos(user_id, 25, 'achievement')
add_to_inventory(user_id, 'badge_valentia')
```

9. Bot envía respuesta a María con animación:
```python
await update.callback_query.answer()
await update.callback_query.edit_message_text(
    text=next_fragment.content,
    reply_markup=create_decision_keyboard(next_fragment.decisions)
)

# Notificación de recompensas
await context.bot.send_message(
    chat_id=user_id,
    text=(
        "🎉 ¡Fragmento completado!\n\n"
        "📊 Recompensas:\n"
        "• 50 besitos\n"
        "• Item: Nota de Lucien\n\n"
        "🏆 ¡Achievement desbloqueado!\n"
        "• 'Primera Decisión Confiada'\n"
        "• +25 besitos\n"
        "• Badge de Valentía"
    )
)
```

10. Sistema registra analíticas:
```python
# En background
analytics.track('fragment_completed', {
    'user_id': user_id,
    'fragment_key': fragment_key,
    'decision': decision,
    'time_spent_seconds': 120,
    'rewards_earned': {'besitos': 75, 'items': 2}
})
```

11. María ahora tiene 75 besitos más y 2 items nuevos. El sistema verifica automáticamente si esto desbloquea contenido:
```python
# Verificación automática tras cambio en inventario
fragments_unlocked = check_all_unlocks(user_id)

if fragments_unlocked:
    for fragment_key in fragments_unlocked:
        send_notification(
            user_id,
            f"✨ ¡Nuevo contenido desbloqueado!\n"
            f"Tu progreso ha revelado: {get_fragment_title(fragment_key)}"
        )
```

12. María ve notificación: "✨ ¡Nuevo contenido desbloqueado! Tu progreso ha revelado: El Jardín Secreto"

Todo este flujo ocurre en menos de 500ms desde la perspectiva de María. El sistema procesó:
- 1 decisión narrativa
- 2 recompensas de besitos (fragmento + achievement)
- 2 items agregados al inventario
- 1 achievement desbloqueado
- Verificación de desbloqueos
- 2 notificaciones enviadas
- Eventos publicados y manejados por 3 módulos
- Analíticas registradas

---

## 11. Plan de Implementación Recomendado

### 11.1 Fases de Desarrollo

**Fase 1: Fundamentos (Semanas 1-3)**

Objetivos:
- Configurar infraestructura básica (PostgreSQL, Redis, MongoDB)
- Implementar bot básico con python-telegram-bot
- Crear sistema de usuarios y autenticación
- Implementar Event Bus básico
- Configurar base de datos con esquema inicial

Entregables:
- Bot que responde a /start, /help
- Base de datos funcional con tablas core
- Sistema de usuarios con registro automático
- Event Bus publicando y recibiendo eventos test
- Docker Compose para desarrollo local

**Fase 2: Módulo de Narrativa (Semanas 4-6)**

Objetivos:
- Implementar motor de narrativa ramificada
- Crear sistema de fragmentos y decisiones
- Implementar desbloqueos condicionales
- Integrar MongoDB para contenido narrativo
- Crear 3 niveles de narrativa de prueba

Entregables:
- Motor de narrativa funcional
- Usuarios pueden navegar fragmentos y tomar decisiones
- Sistema de desbloqueos por besitos/items/flags
- 3 niveles completos con ~15 fragmentos totales
- Tests unitarios para motor de narrativa

**Fase 3: Módulo de Gamificación (Semanas 7-9)**

Objetivos:
- Implementar economía de besitos
- Crear sistema de inventario
- Implementar misiones (daily, weekly, narrative)
- Crear sistema de achievements
- Implementar tienda básica

Entregables:
- Sistema de besitos con transacciones
- Inventario funcional con items
- Misiones asignadas automáticamente y rastreadas
- 10+ achievements implementados
- Tienda con 20+ items comprables
- Integración con narrativa (recompensas automáticas)

**Fase 4: Módulo de Administración (Semanas 10-12)**

Objetivos:
- Implementar gestión de suscripciones VIP
- Crear sistema de canales (free y VIP)
- Implementar publicación programada de contenido
- Crear sistema de moderación básico
- Implementar verificación de membresía

Entregables:
- Gestión completa de suscripciones VIP
- Canales configurados con acceso controlado
- Scheduler para contenido programado
- Herramientas de moderación (ban, warn)
- Jobs para recordatorios y expiraciones

**Fase 5: Sistema de Configuración Unificada (Semanas 13-15)**

Objetivos:
- Crear Configuration Manager
- Implementar plantillas de configuración
- Desarrollar asistentes de creación
- Crear sistema de validación
- Implementar propagación de cambios

Entregables:
- Panel de configuración unificado
- 5+ plantillas predefinidas
- Asistentes para experiencias, misiones, eventos
- Validación en tiempo real
- Historial y versionado de configuraciones

**Fase 6: Panel de Administración Web (Semanas 16-18)**

Objetivos:
- Desarrollar FastAPI backend
- Crear dashboard administrativo
- Implementar analíticas visuales
- Crear editores visuales
- Implementar gestión de contenido

Entregables:
- Dashboard completo con métricas en tiempo real
- Editor visual de flujos narrativos
- Gestión de contenido desde web
- Sistema de analíticas con gráficas
- Autenticación y autorización de admins

**Fase 7: Funcionalidades Avanzadas (Semanas 19-21)**

Objetivos:
- Implementar sistema de trivias
- Crear sistema de subastas en tiempo real
- Implementar fragmentos secretos y metajuego
- Agregar funcionalidades sociales (gifts, PvP)
- Optimizar rendimiento

Entregables:
- Trivias funcionales con tipos variados
- Sistema de subastas completo
- 5+ fragmentos secretos con mecánicas únicas
- Features sociales implementadas
- Optimizaciones de performance aplicadas

**Fase 8: Integración de Pagos (Semanas 22-23)**

Objetivos:
- Integrar Telegram Stars
- Integrar Stripe como alternativa
- Implementar flujo completo de suscripción
- Crear sistema de refunds
- Testing exhaustivo de pagos

Entregables:
- Pagos funcionales con ambos procesadores
- Flujo de suscripción end-to-end
- Webhooks configurados y testeados
- Políticas de refund implementadas
- Documentación de manejo de pagos

**Fase 9: Testing y Refinamiento (Semanas 24-26)**

Objetivos:
- Testing exhaustivo de todos los módulos
- Testing de integración entre módulos
- Testing de carga y performance
- Corrección de bugs
- Refinamiento de UX

Entregables:
- Suite completa de tests (unitarios, integración, E2E)
- Performance optimizado (< 500ms response time)
- Bugs críticos resueltos
- Documentación completa de código
- UX refinada basada en feedback

**Fase 10: Despliegue y Monitoreo (Semanas 27-28)**

Objetivos:
- Configurar producción (servidores, dominios)
- Implementar CI/CD pipeline
- Configurar monitoreo y alertas
- Realizar despliegue gradual
- Capacitar administradores

Entregables:
- Sistema desplegado en producción
- Pipeline de CI/CD funcional
- Monitoreo con Prometheus/Grafana
- Alertas configuradas
- Documentación operativa

### 11.2 Consideraciones de Desarrollo

**Desarrollo Iterativo**

Cada fase debe seguir ciclo de desarrollo ágil:
1. Planificación detallada de features
2. Desarrollo incremental
3. Testing continuo
4. Review y refinamiento
5. Integración con fases anteriores

**Testing Estratégico**

Priorizar testing en áreas críticas:

Tests Unitarios (70% cobertura mínima):
```python
# Ejemplo: Test de economía de besitos
def test_grant_besitos():
    user = create_test_user()
    initial_balance = user.balance
    
    grant_besitos(user.id, 100, 'test')
    
    assert user.balance == initial_balance + 100
    assert Transaction.objects.filter(
        user_id=user.id,
        amount=100
    ).exists()

def test_insufficient_funds():
    user = create_test_user(balance=50)
    
    with pytest.raises(InsufficientFundsException):
        spend_besitos(user.id, 100)
    
    # Balance no debe cambiar
    assert user.balance == 50
```

Tests de Integración:
```python
# Ejemplo: Test de flujo completo narrativo
def test_narrative_flow_with_rewards():
    user = create_test_user()
    fragment = create_test_fragment(
        rewards={'besitos': 50, 'items': ['test_item']}
    )
    
    # Usuario completa fragmento
    result = narrative_engine.complete_fragment(
        user.id, fragment.fragment_key, 'decision_a'
    )
    
    # Verificar recompensas otorgadas
    assert get_balance(user.id) == 50
    assert has_item(user.id, 'test_item')
    
    # Verificar evento publicado
    assert event_bus.was_published('narrative.fragment_completed')
```

Tests de Carga:
```python
# Usando locust para load testing
from locust import HttpUser, task, between

class DianaBot User(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def complete_fragment(self):
        self.client.post('/api/narrative/complete', json={
            'user_id': self.user_id,
            'fragment_key': 'test_fragment',
            'decision': 'choice_a'
        })
    
    @task
    def check_balance(self):
        self.client.get(f'/api/users/{self.user_id}/balance')
```

**Seguridad desde el Principio**

Integrar seguridad en cada fase:
- Code reviews obligatorios para todo código
- Escaneo automático de vulnerabilidades
- Validación de input en todos los endpoints
- Sanitización de output antes de enviar a usuarios
- Auditoría de acceso a datos sensibles

**Documentación Continua**

Mantener documentación actualizada:
- Docstrings en todas las funciones
- README actualizado con setup instructions
- Documentación de API con OpenAPI/Swagger
- Diagramas de arquitectura actualizados
- Runbooks para operaciones comunes

---

## 12. Métricas de Éxito y KPIs

### 12.1 Métricas de Producto

**Engagement:**
- DAU (Daily Active Users): Usuarios que interactúan al menos 1 vez al día
- WAU (Weekly Active Users): Usuarios que interactúan al menos 1 vez a la semana
- MAU (Monthly Active Users): Usuarios que interactúan al menos 1 vez al mes
- Session Length: Tiempo promedio de interacción por sesión
- Sessions per User: Cuántas veces regresa un usuario por día/semana

**Retención:**
- Day 1 Retention: % de usuarios que regresan al día siguiente
- Day 7 Retention: % de usuarios que siguen activos después de 7 días
- Day 30 Retention: % de usuarios que siguen activos después de 30 días
- Churn Rate: % de usuarios que dejan de usar el bot

**Narrativa:**
- Fragments Completed per User: Promedio de fragmentos completados
- Decision Distribution: Distribución de decisiones tomadas (¿todas las opciones son elegidas?)
- Level Completion Rate: % de usuarios que completan cada nivel
- Time to Complete Level: Tiempo promedio para completar cada nivel
- Drop-off Points: Dónde abandonan usuarios la narrativa

**Gamificación:**
- Besitos per User: Promedio de besitos por usuario
- Transaction Velocity: Transacciones de besitos por día
- Shop Conversion: % de usuarios que compran en la tienda
- Mission Completion Rate: % de misiones asignadas que se completan
- Achievement Unlock Rate: % de achievements desbloqueados vs total

**Monetización:**
- Free to VIP Conversion: % de usuarios free que se convierten a VIP
- ARPU (Average Revenue Per User): Ingreso promedio por usuario
- ARPPU (Average Revenue Per Paying User): Ingreso promedio por usuario pagador
- LTV (Lifetime Value): Valor total de un usuario durante su vida
- CAC (Customer Acquisition Cost): Costo de adquirir un usuario
- LTV/CAC Ratio: Idealmente > 3:1

### 12.2 Métricas Técnicas

**Performance:**
- Response Time: Tiempo de respuesta promedio (objetivo: < 500ms)
- 95th Percentile Response Time: Tiempo de respuesta del 95% de requests (objetivo: < 1s)
- Error Rate: % de requests que fallan (objetivo: < 0.1%)
- Uptime: % de tiempo que el sistema está disponible (objetivo: > 99.9%)

**Escalabilidad:**
- Requests per Second: Capacidad de procesar requests
- Database Query Time: Tiempo promedio de queries (objetivo: < 100ms)
- Cache Hit Rate: % de requests servidos desde caché (objetivo: > 80%)
- Background Job Processing Time: Tiempo para procesar jobs en cola

**Recursos:**
- CPU Usage: Uso de CPU de servidores (objetivo: < 70% promedio)
- Memory Usage: Uso de RAM (objetivo: < 80%)
- Database Connections: Conexiones activas a DB (monitorear pool)
- Redis Memory: Memoria usada por Redis (objetivo: < 90%)

### 12.3 Dashboard de KPIs

Implementar dashboard que muestre métricas críticas en tiempo real:

```python
# Ejemplo de endpoint para métricas
@app.get('/api/metrics/summary')
async def get_metrics_summary():
    now = datetime.now()
    
    return {
        'engagement': {
            'dau': count_active_users(hours=24),
            'wau': count_active_users(days=7),
            'mau': count_active_users(days=30),
            'avg_session_length_minutes': get_avg_session_length()
        },
        'monetization': {
            'active_vip_subs': count_active_subscriptions(),
            'conversion_rate': calculate_conversion_rate(),
            'mrr': calculate_monthly_recurring_revenue(),
            'arpu': calculate_arpu()
        },
        'narrative': {
            'fragments_completed_today': count_completions(hours=24),
            'avg_level_completion': get_avg_level_completion(),
            'most_popular_decision': get_most_popular_decisions(limit=1)[0]
        },
        'gamification': {
            'besitos_in_circulation': get_total_besitos(),
            'transactions_today': count_transactions(hours=24),
            'missions_completed_today': count_mission_completions(hours=24),
            'achievements_unlocked_today': count_achievement_unlocks(hours=24)
        },
        'technical': {
            'avg_response_time_ms': get_avg_response_time(),
            'error_rate_percent': get_error_rate(),
            'uptime_percent': get_uptime(),
            'cache_hit_rate_percent': get_cache_hit_rate()
        }
    }
```

---

## 13. Riesgos y Mitigaciones

### 13.1 Riesgos Técnicos

**Riesgo: Escalabilidad Insuficiente**

Descripción: El sistema no soporta crecimiento rápido de usuarios.

Mitigación:
- Arquitectura diseñada para escalar horizontalmente desde el inicio
- Load testing regular para identificar cuellos de botella
- Monitoreo proactivo de métricas de performance
- Plan de escalado automático basado en carga
- Database sharding preparado pero no activado hasta necesario

**Riesgo: Pérdida de Datos**

Descripción: Fallo de base de datos o corrupción de datos críticos.

Mitigación:
- Backups automáticos diarios de PostgreSQL y MongoDB
- Replicación de base de datos en tiempo real
- Transaction logs para recovery point-in-time
- Testing regular de procedimientos de restore
- Redundancia geográfica de datos críticos

**Riesgo: Downtime Prolongado**

Descripción: Sistema inaccesible por fallo de infraestructura.

Mitigación:
- Alta disponibilidad con múltiples instancias
- Health checks y auto-restart de servicios
- Failover automático a servidores backup
- Plan de recuperación ante desastres documentado
- Acuerdos de SLA con proveedores de infraestructura

**Riesgo: Bugs en Economía de Besitos**

Descripción: Bug permite a usuarios generar besitos infinitos o perderlos incorrectamente.

Mitigación:
- Testing exhaustivo de toda lógica económica
- Transacciones atómicas para prevenir estados inconsistentes
- Audit logs completos de todas las transacciones
- Monitoreo de anomalías en ganancia de besitos
- Sistema de rollback para corrección de bugs económicos
- Rate limiting en todas las fuentes de besitos

### 13.2 Riesgos de Producto

**Riesgo: Baja Conversión a VIP**

Descripción: Pocos usuarios convierten de free a VIP.

Mitigación:
- A/B testing de mensajes de conversión
- Free trial de 7 días para enganchar usuarios
- Contenido free de alta calidad que genera interés en premium
- Clear value proposition para VIP
- Descuentos y promociones estratégicas
- Análisis de friction points en el funnel de conversión

**Riesgo: Economía Desequilibrada**

Descripción: Besitos pierden valor o son muy escasos, frustrando usuarios.

Mitigación:
- Simulaciones económicas pre-launch
- Monitoreo continuo de métricas económicas
- Ajustes dinámicos de recompensas basados en datos
- Encuestas a usuarios sobre percepción de valor
- Sistema de faucets y sinks balanceados

**Riesgo: Contenido Insuficiente**

Descripción: Usuarios consumen contenido más rápido de lo que se puede crear.

Mitigación:
- Pipeline de contenido planificado con 3 meses de adelanto
- Herramientas de creación de contenido eficientes
- Contenido procedural o replayable donde sea apropiado
- Comunidad de content creators (si escala)
- Eventos temporales para extender contenido existente

**Riesgo: Churn Alto**

Descripción: Usuarios abandonan rápidamente después de registrarse.

Mitigación:
- Onboarding claro y enganchador
- Primeras experiencias pulidas y atractivas
- Rewards tempranos para crear hábito
- Notificaciones push estratégicas para reengagement
- Análisis de cohorts para identificar patrones de churn
- Win-back campaigns para usuarios inactivos

### 13.3 Riesgos de Negocio

**Riesgo: Cambios en Políticas de Telegram**

Descripción: Telegram cambia políticas que afectan funcionalidad del bot.

Mitigación:
- Mantenerse actualizado con announcements de Telegram
- Diseño modular que permite adaptación rápida
- Contingencias para funcionalidades críticas
- Diversificación eventual a otras plataformas

**Riesgo: Competencia**

Descripción: Aparecen bots competidores con features similares.

Mitigación:
- Innovación continua en features
- Enfoque en calidad de narrativa y experiencia
- Construcción de comunidad leal
- Propiedad intelectual de contenido original
- Velocidad de iteración superior

**Riesgo: Regulaciones de Monetización**

Descripción: Nuevas regulaciones afectan capacidad de monetizar.

Mitigación:
- Cumplimiento estricto de regulaciones existentes
- Consultoría legal preventiva
- Modelos de monetización alternativos preparados
- Transparencia con usuarios sobre uso de fondos

---

## 14. Roadmap Post-Launch

### 14.1 Features Fase 2 (Meses 4-6)

**Funcionalidades Sociales Avanzadas:**
- Sistema de amigos dentro del bot
- Regalos de items entre usuarios
- Leaderboards públicos y de amigos
- Misiones cooperativas (2+ usuarios)
- Chat entre usuarios (si Telegram lo permite)

**Contenido Expandido:**
- Niveles 7-9 (continuación narrativa)
- 50+ nuevos items coleccionables
- 30+ nuevos achievements
- Eventos narrativos temporales mensuales
- Side stories de personajes secundarios

**Gamificación Avanzada:**
- Sistema de clans/guilds
- Torneos y competencias periódicas
- Crafting de items (combinar items para crear nuevos)
- Pets o compañeros virtuales
- Sistema de prestigio (reset con beneficios permanentes)

### 14.2 Features Fase 3 (Meses 7-12)

**Personalización:**
- Avatares customizables
- Titles y badges cosméticos
- Temas visuales para la interfaz
- Playlist de música ambiental personalizada

**Contenido Generado por Usuarios:**
- Herramientas para usuarios crear mini-historias
- Sistema de moderación de contenido user-generated
- Marketplace de contenido creado por usuarios
- Recompensas para content creators populares

**Analíticas para Usuarios:**
- Estadísticas personales detalladas
- Comparación con promedios globales
- Achievements earned timeline
- Replay de decisiones narrativas tomadas

**Multiplataforma:**
- Web app complementaria
- Progressive Web App (PWA)
- Consideración de expansión a Discord, WhatsApp

### 14.3 Innovaciones Futuras

**IA Generativa (Experimental):**
- Narrativa adaptativa generada por IA basada en preferencias
- NPCs con conversaciones dinámicas
- Personalización profunda de contenido

**Realidad Aumentada:**
- Integración con cámara para experiencias AR
- Búsquedas de tesoros en el mundo real
- Items coleccionables geolocalizados

**Blockchain (Opcional):**
- NFTs para items ultra-raros
- Economía descentralizada
- Ownership verdadero de assets digitales

---

## 15. Conclusiones y Recomendaciones Finales

### 15.1 Síntesis de la Investigación

DianaBot representa un ecosistema complejo pero perfectamente viable que combina:

✅ **Narrativa Inmersiva**: Motor robusto de historias ramificadas con decisiones significativas
✅ **Gamificación Profunda**: Economía interna, misiones, achievements, inventario
✅ **Administración Centralizada**: Control unificado de todos los aspectos del sistema
✅ **Monetización Sostenible**: Modelo freemium balanceado con múltiples fuentes de ingreso
✅ **Escalabilidad**: Arquitectura preparada para crecer de usuarios iniciales a millones
✅ **Seguridad**: Múltiples capas de protección para datos y economía

### 15.2 Viabilidad Técnica

**Alta Viabilidad** basada en:

Tecnologías Maduras: Todas las tecnologías recomendadas (Python, PostgreSQL, Redis, MongoDB, python-telegram-bot) son maduras, bien documentadas y tienen ecosistemas robustos.

Arquitectura Probada: Los patrones arquitectónicos propuestos (event-driven, modular, microservicios opcionales) son usados exitosamente por productos similares.

Telegram como Plataforma: Telegram Bot API es poderosa, estable y activamente mantenida. La plataforma tiene millones de usuarios activos.

Stack Unificado: Python en todo el stack (bot, API, tasks) reduce complejidad y facilita mantenimiento.

### 15.3 Viabilidad de Producto

**Alta Viabilidad** considerando:

Demanda Probada: Bots de narrativa interactiva y gamificación tienen traction comprobada en Telegram.

Nicho Específico: El enfoque emocional/psicológico/erótico define un nicho con audiencia dedicada.

Value Proposition Clara: Combinar narrativa + gamificación + comunidad ofrece valor único.

Monetización Validada: Modelos de suscripción y microtransacciones funcionan en plataformas similares.

### 15.4 Recomendaciones Críticas

**1. Comenzar con MVP Enfocado**

No implementar todo de una vez. Prioridades del MVP:
- Narrativa básica funcional (3 niveles)
- Economía de besitos simple
- Misiones básicas
- Suscripción VIP con distinción clara de valor
- Panel admin mínimo pero funcional

Expandir después basado en feedback real de usuarios.

**2. Obsesionarse con la Calidad de Narrativa**

La narrativa es el diferenciador principal. Invertir en:
- Escritores talentosos
- Edición rigurosa
- Testing de narrativa con usuarios beta
- Coherencia de personajes y trama
- Multimedia de alta calidad (imágenes, audio)

Una narrativa mediocre matará el producto, sin importar qué tan buena sea la tecnología.

**3. Balancear Economía Desde el Inicio**

La economía de besitos debe ser cuidadosamente tuneada:
- Comenzar conservador (fácil ajustar hacia arriba recompensas)
- Monitorear métricas económicas obsesivamente en primeras semanas
- Estar preparado para ajustes rápidos
- Comunicar cambios claramente a usuarios

Una economía rota puede arruinar la experiencia y es difícil de arreglar post-launch.

**4. Configuración Unificada es No-Negociable**

El sistema de configuración centralizada no es opcional - es absolutamente crítico para:
- Velocidad de creación de contenido
- Coherencia de experiencia
- Reducción de errores
- Escalabilidad operativa

Invertir tiempo adecuado en esta infraestructura desde el principio pagará dividendos enormes.

**5. Seguridad desde el Día 1**

No tratar seguridad como algo para "agregar después":
- Implementar autenticación y autorización robustas desde el inicio
- Auditar toda lógica económica con extreme rigor
- Rate limiting en todos los endpoints vulnerables
- Logging y monitoreo de actividad sospechosa

Un exploit de besitos o acceso no autorizado a contenido VIP puede destruir la confianza del usuario.

**6. Métricas y Analytics Tempranos**

Implementar tracking de métricas desde el primer usuario:
- Toda acción importante debe generar evento
- Dashboard de KPIs accesible en todo momento
- Alertas automáticas para anomalías
- A/B testing framework desde temprano

Las decisiones deben ser data-driven, no basadas en intuición.

**7. Comunidad como Asset Estratégico**

Construir comunidad desde el inicio:
- Canal de Discord/Telegram para usuarios
- Solicitar feedback activamente
- Reconocer y recompensar early adopters
- Beta testers VIP con acceso anticipado

La comunidad puede ser defensora del producto, fuente de ideas y evangelistas.

### 15.5 Factores de Éxito Críticos

1. **Narrativa de Calidad Excepcional**: Si la historia no engancha, nada más importa
2. **First Hour Experience**: Los primeros 60 minutos determinan retención
3. **Clear Value Ladder**: Usuarios deben entender claramente qué ganan con VIP
4. **Technical Stability**: Bugs destruyen inmersión y confianza
5. **Responsive Development**: Capacidad de iterar rápido basado en feedback
6. **Sustainable Economics**: Balance entre generosidad y incentivo a pagar

### 15.6 Consideraciones Finales

DianaBot es técnicamente complejo pero absolutamente implementable con el approach correcto. La clave es:

**Comenzar Pequeño, Pensar Grande**: Implementar MVP funcional en 3-4 meses, luego iterar basado en datos reales.

**Priorizar Experiencia sobre Features**: Mejor tener 3 features pulidas que 10 a medias.

**Construir para Escalar**: Arquitectura preparada para crecer, pero no sobre-ingeniería prematura.

**Mantener Flexibilidad**: El mercado y usuarios dirán qué funciona. Estar listo para pivotar.

**Invertir en Tooling**: Herramientas internas de calidad aceleran todo el desarrollo posterior.

Con ejecución disciplinada, atención al detalle y enfoque en experiencia del usuario, DianaBot tiene potencial de convertirse en un producto altamente exitoso y diferenciado en el espacio de bots de Telegram.

---

## Próximos Pasos Inmediatos

Para comenzar la implementación:

1. **Semana 1**: Setup de repositorio, infraestructura Docker, bases de# DianaBot: Investigación Técnica Integral

## Índice
1. Arquitectura General del Sistema
2. Plataforma y Tecnologías
3. Módulo de Narrativa Inmersiva
4. Módulo de Gamificación
5. Módulo de Administración de Canales
6. Sistema de Configuración Centralizada
7. Integración y Flujos Cruzados
8. Seguridad y Escalabilidad
9. Monetización y Roles

---

## 1. Arquitectura General del Sistema

### 1.1 Propuesta Arquitectónica: Event-Driven Modular Architecture

La arquitectura más apropiada para DianaBot combina tres patrones fundamentales que trabajan en armonía. Primero, necesitamos una arquitectura basada en eventos porque los tres módulos deben comunicarse sin crear dependencias rígidas entre ellos. Cuando un usuario toma una decisión narrativa, ese evento debe poder desencadenar recompensas en gamificación sin que el módulo narrativo necesite conocer los detalles internos del sistema de besitos.

Segundo, adoptamos un enfoque de capas limpias donde cada módulo tiene su propia lógica de negocio independiente pero expone interfaces claras para la comunicación. Esto significa que el módulo de narrativa puede operar completamente solo si fuera necesario, pero cuando está integrado, puede enviar y recibir eventos del resto del sistema.

Tercero, implementamos un patrón de repositorio centralizado para la configuración, lo que permite que todos los módulos consulten una única fuente de verdad para reglas, recompensas y condiciones de desbloqueo.

### 1.2 Componentes Principales

**Core del Sistema (Event Bus)**
El corazón de DianaBot es un bus de eventos que actúa como sistema nervioso central. Cada módulo publica eventos cuando ocurren acciones importantes y se suscribe a eventos que le interesan. Por ejemplo, cuando un usuario completa un fragmento narrativo, el módulo de narrativa publica un evento "NarrativeFragmentCompleted". El módulo de gamificación escucha este evento y otorga automáticamente los besitos correspondientes. El módulo de administración registra el progreso para análisis.

**Configuration Manager (Gestor de Configuración Unificada)**
Este componente es absolutamente crítico para cumplir con el requisito de configuración centralizada. Funciona como una capa de abstracción que permite definir elementos complejos como "experiencias" que automáticamente crean registros en narrativa, gamificación y administración de forma coordinada. Cuando un administrador crea una nueva misión que desbloquea un fragmento narrativo, el Configuration Manager asegura que ambos sistemas estén sincronizados desde el momento de la creación.

**Estado del Usuario (User State Manager)**
Mantiene el contexto completo de cada usuario a través de todos los módulos. Esto incluye su posición en la narrativa, su inventario, sus besitos, sus logros y su estado de suscripción. Este componente garantiza consistencia cuando diferentes módulos necesitan verificar o modificar el estado del usuario.

### 1.3 Diagrama de Comunicación

```
┌─────────────────────────────────────────────────────┐
│           Configuration Manager (Unificado)         │
│    - Plantillas de experiencias                     │
│    - Validación de coherencia                       │
│    - Propagación de cambios                         │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │    Event Bus      │
         │  (Pub/Sub System) │
         └─────────┬─────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐    ┌───▼────┐    ┌───▼────┐
│Narrativa│◄──►│Gamifi- │◄──►│Admin.  │
│         │    │cación  │    │Canales │
└───┬────┘    └───┬────┘    └───┬────┘
    │             │             │
    └─────────────┼─────────────┘
                  │
          ┌───────▼───────┐
          │  User State   │
          │   Manager     │
          └───────────────┘
```

### 1.4 Patrones de Diseño Recomendados

**Command Pattern para Acciones de Usuario**
Cada acción del usuario (tomar decisión, comprar ítem, reaccionar) se encapsula como un comando. Esto permite deshacer acciones, registrar historial y procesar comandos de manera asíncrona si el sistema está bajo carga.

**Observer Pattern para Eventos**
Los módulos actúan como observadores de eventos específicos. El módulo de narrativa observa eventos de compra de ítems para verificar si se deben desbloquear nuevos fragmentos. El módulo de gamificación observa eventos narrativos para otorgar recompensas.

**Strategy Pattern para Condiciones de Desbloqueo**
Las condiciones para desbloquear contenido (tener X besitos, poseer cierto ítem, tener badge específico) se implementan como estrategias intercambiables. Esto facilita agregar nuevos tipos de condiciones sin modificar el código existente.

**Repository Pattern para Acceso a Datos**
Cada módulo accede a la base de datos a través de repositorios que abstraen las consultas SQL. Esto permite cambiar la base de datos subyacente sin afectar la lógica de negocio.

---

## 2. Plataforma y Tecnologías

### 2.1 Framework del Bot: python-telegram-bot vs Telethon vs pyrogramming

Después de analizar las características requeridas, la biblioteca más apropiada es **python-telegram-bot (PTB) v20+**. Esta elección se fundamenta en varios aspectos críticos para DianaBot.

Primero, PTB ofrece manejo nativo de handlers complejos que se adaptan perfectamente a la estructura de comandos, callbacks inline y reacciones que necesitamos. Su sistema de ConversationHandler es ideal para la narrativa ramificada, permitiendo mantener estados de conversación de manera natural.

Segundo, PTB tiene soporte robusto para Jobs y scheduling, esencial para misiones diarias, recordatorios de suscripción VIP y eventos programados en canales. Su JobQueue integrada puede manejar tareas recurrentes sin dependencias externas adicionales.

Tercero, la documentación y comunidad de PTB son excepcionales, lo que reduce significativamente el tiempo de desarrollo y resolución de problemas.

**Estructura Tecnológica Recomendada:**

```
Backend: Python 3.11+
Bot Framework: python-telegram-bot 20.x
Web Framework: FastAPI (para panel admin y webhooks)
Task Queue: Celery con Redis (para procesos pesados)
Cache: Redis (para estado de sesiones y rate limiting)
```

### 2.2 Base de Datos: Enfoque Híbrido

La naturaleza de DianaBot requiere un enfoque híbrido que aproveche las fortalezas de diferentes paradigmas de almacenamiento.

**PostgreSQL como Base de Datos Principal**

PostgreSQL es ideal para los datos relacionales y transaccionales de DianaBot. Su soporte para JSONB permite flexibilidad cuando la necesitamos sin sacrificar integridad referencial. Veamos por qué es la elección correcta:

Para el estado del usuario, necesitamos garantizar consistencia transaccional. Cuando un usuario gasta besitos para comprar un ítem, debemos asegurar que el balance de besitos se decremente exactamente en la misma transacción que agrega el ítem al inventario. PostgreSQL maneja esto perfectamente con sus garantías ACID.

El progreso narrativo se beneficia enormemente de las relaciones. Un usuario está en un fragmento, ese fragmento pertenece a un nivel, ese nivel tiene condiciones de desbloqueo. Estas relaciones naturales se modelan eficientemente en SQL.

Las suscripciones VIP requieren consultas complejas con fechas (usuarios que expiran en 3 días, usuarios activos en rango de fechas). PostgreSQL excele en estas operaciones con índices apropiados.

**MongoDB como Almacén de Configuración Dinámica**

MongoDB complementa a PostgreSQL para aspectos específicos donde la flexibilidad de esquema es valiosa:

Los fragmentos narrativos pueden tener estructuras variables. Un fragmento puede tener dos decisiones, otro puede tener cinco, algunos incluyen minijuegos. Almacenar esto en JSONB de PostgreSQL es posible, pero MongoDB ofrece consultas más expresivas sobre estructuras anidadas.

Las plantillas de configuración del sistema unificado se benefician de la flexibilidad de documentos. Una plantilla de "experiencia narrativa-gamificada" puede tener campos opcionales según el tipo de experiencia.

**Redis para Estado en Tiempo Real**

Redis maneja todo lo que necesita velocidad extrema:

El estado de conversación activa (en qué fragmento está el usuario AHORA) se cachea en Redis. Cuando el usuario toma una decisión, consultamos Redis primero, evitando latencia de base de datos.

Rate limiting de acciones (prevenir spam de compras o decisiones) se implementa eficientemente con INCR y EXPIRE de Redis.

Locks distribuidos para operaciones críticas como subastas en tiempo real previenen condiciones de carrera.

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

### 2.4 Integración con API de Telegram

**Manejo de Canales y Suscripciones**

Telegram proporciona APIs específicas para gestionar membresías en canales, pero hay aspectos críticos que debemos entender profundamente.

Para validar suscripciones VIP, usamos el método `getChatMember` que devuelve el estado de un usuario en un canal específico. Sin embargo, esta validación debe ser inteligente y no bloquear la experiencia del usuario. Implementamos un sistema de caché donde verificamos la membresía una vez por sesión y guardamos el resultado en Redis con un TTL de 1 hora. Solo re-verificamos si el usuario intenta acceder a contenido VIP o si ha pasado el tiempo de caché.

La expulsión automática al expirar suscripción requiere un job programado que consulta la base de datos cada hora buscando suscripciones que expiran. Para cada una, llamamos a `banChatMember` con `revoke_messages=False` para remover al usuario sin eliminar su historial de mensajes. Inmediatamente después, enviamos un mensaje directo al usuario informándole y ofreciendo renovación.

**Reacciones y Engagement**

Las reacciones a mensajes son una característica relativamente nueva en Telegram. Para vincularlas con gamificación, usamos `MessageReactionUpdated` handlers que detectan cuando un usuario agrega una reacción específica. Por ejemplo, si el administrador configura que reaccionar con ❤️ a un mensaje narrativo otorga 2 besitos, el handler verifica que es la primera vez que ese usuario reacciona a ese mensaje específico, previene duplicados consultando Redis, y otorga la recompensa.

**Botones Inline y Callbacks**

Los botones inline son el mecanismo principal de interacción para decisiones narrativas y compras. Cada botón incluye un `callback_data` que codifica la acción. Por ejemplo: `"decision:fragment_005:choice_b:user_12345"`. El handler de callback decodifica esto, verifica que el usuario tenga acceso al fragmento, procesa la decisión, actualiza el estado y responde con el siguiente fragmento.

Para prevenir que usuarios maliciosos manipulen callbacks, incluimos un hash HMAC en cada callback_data que valida la integridad del mensaje.

---

## 3. Módulo de Narrativa Inmersiva

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

### 3.3 Desbloqueos Condicionales Complejos

Los desbloqueos van más allá de simples verificaciones. Un fragmento podría tener condiciones como:

```json
{
  "unlock_conditions": {
    "operator": "AND",
    "conditions": [
      {
        "type": "subscription",
        "value": "vip"
      },
      {
        "operator": "OR",
        "conditions": [
          {
            "type": "besitos",
            "operator": ">=",
            "value": 100
          },
          {
            "type": "has_item",
            "item_key": "golden_invitation"
          }
        ]
      },
      {
        "type": "completed_fragments",
        "fragments": ["fragment_012", "fragment_013"],
        "operator": "ALL"
      },
      {
        "type": "narrative_flag",
        "flag": "earned_diana_trust",
        "value": true
      }
    ]
  }
}
```

Esta condición se lee: "El usuario debe ser VIP Y (tener 100+ besitos O poseer el item 'golden_invitation') Y haber completado los fragmentos 12 y 13 Y tener el flag 'earned_diana_trust' activo".

El motor evalúa estas condiciones recursivamente usando un intérprete de expresiones booleanas. Cuando un desbloqueo falla, el motor no solo dice "acceso denegado", sino que explica específicamente qué falta: "Necesitas la invitación dorada o 100 besitos para continuar".

### 3.4 Fragmentos Ocultos y Metajuego

Algunos fragmentos son "secretos" y no aparecen en el flujo normal. Los usuarios los descubren mediante:

Pistas en otros canales: Un mensaje en el canal VIP contiene un código encriptado. Resolverlo revela el `fragment_key` de un fragmento secreto.

Combinaciones de items: Poseer simultáneamente "ancient_map" y "decoder_ring" desbloquea automáticamente un fragmento oculto sobre el pasado de Lucien.

Exploración de paths alternativos: Si el usuario toma decisiones contraintuitivas en varios fragmentos, desbloquea un "bad ending" alternativo.

El motor verifica periódicamente si el estado del usuario satisface condiciones de fragmentos ocultos y los hace aparecer dinámicamente en el mapa de narrativa del usuario.

---

## 4. Módulo de Gamificación

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

El `select_for_update()` asegura que nadie más puede modificar ese balance hasta que la transacción complete.

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

### 4.3 Inventario (Mochila) y Sistema de Items

El inventario es más que una lista de posesiones, es un sistema que conecta gamificación con narrativa.

**Categorías de Items**

Items Narrativos (Narrative Keys):
- Desbloquean fragmentos específicos
- Ejemplos: "Llave del Ático Prohibido", "Diario de Diana Joven"
- No se consumen al usar, permanecen en inventario

Items Consumibles:
- Se usan una vez y desaparecen
- Ejemplos: "Poción de Doble Besitos" (duplica besitos ganados por 1 hora)
- Afectan temporalmente las mecánicas de juego

Coleccionables:
- No tienen función mecánica, solo valor de colección
- Completan sets que otorgan achievements
- Ejemplos: "Fragmento de Espejo Antiguo" (5 fragmentos forman espejo completo)

Power-ups:
- Mejoran capacidades temporalmente
- Ejemplos: "Intuición de Lucien" (revela consecuencias de decisiones por 3 usos)

Items de Subasta:
- Únicos o muy raros
- Solo obtenibles en subastas
- Ejemplos: "Retrato Firmado de Diana" (solo 1 existe en todo el sistema)

**Efectos Cruzados Narrativa-Items**

Los items no son estáticos. Su presencia en el inventario puede:

Cambiar diálogos: Si tienes "Anillo de Compromiso Antiguo", Lucien comenta sobre él.

Desbloquear opciones de decisión: Una tercera opción aparece solo si posees "Pergamino de Ritual".

Modificar endings: Tener ciertos items combinados lleva a finales alternativos.

Activar fragmentos secretos: Poseer "Mapa del Laberinto" + "Linterna Eterna" revela entrada a nivel oculto.

**Gestión de Inventario**

El inventario tiene mecánicas propias:

Límite de espacio: Los usuarios free tienen 20 slots, VIP tienen 50. Esto incentiva decisiones sobre qué conservar.

Almacén: Items que no caben en inventario activo van a almacén, pero no afectan narrativa hasta ser transferidos.

Intercambio: Usuarios pueden intercambiar items con otros (por besitos o por trueque), creando economía secundaria.

Reciclaje: Items no deseados pueden "reciclarse" por una porción de su valor en besitos.

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

### 4.5 Sistema de Trivias

Las trivias combinan educación sobre el lore narrativo con recompensas inmediatas.

**Formato de Trivias**

Trivias rápidas: Una pregunta, 4 opciones, 30 segundos para responder. Aparecen aleatoriamente en canales.

Trivia diaria: Publicada a hora fija, todos los usuarios tienen 24 horas para responder. Recompensas basadas en velocidad de respuesta.

Trivia en cadena: 5 preguntas consecutivas. Respuestas correctas consecutivas multiplican recompensa (2x, 3x, 5x).

Trivia PvP: Dos usuarios compiten respondiendo la misma secuencia. El más rápido y preciso gana.

**Categorías de Preguntas**

Lore narrativo: "¿En qué año se construyó la mansión de Lucien?"

Detalles de personajes: "¿Cuál es el color favorito de Diana?"

Decisiones narrativas: "¿Qué pasó cuando elegiste confrontar a Lucien en el capítulo 3?"

Meta-juego: "¿Cuántos besitos cuesta el item 'Rosa Eterna'?"

**Recompensas Dinámicas**

Las trivias ajustan recompensas según múltiples factores:

Dificultad: Preguntas difíciles otorgan más besitos.

Velocidad: Responder en 5 segundos vs 25 segundos multiplica recompensa.

Racha: Responder correctamente 10 trivias seguidas otorga bonus.

Rareza: Primera persona en responder correctamente una trivia ultra-rara recibe item único.

**Generación de Preguntas**

Las trivias pueden ser:

Estáticas: Pre-escritas por administradores en MongoDB.

Dinámicas: Generadas basándose en el progreso narrativo del usuario. "¿Qué decisión tomaste en el fragmento que acabas de completar?"

Adaptativas: El sistema detecta qué temas el usuario responde mejor y ajusta dificultad.

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

---

## 5. Módulo de Administración de Canales

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

### 5.3 Sistema de Reacciones Vinculadas

Las reacciones no son solo feedback, son parte del gameplay.

**Configuración de Reacciones Gamificadas**

Al publicar un post, el administrador puede configurar:

```json
{
  "post_id": 456,
  "reaction_rewards": {
    "❤️": {
      "besitos": 2,
      "limit_per_user": 1,
      "achievement_trigger": {
        "achievement_key": "romantic_soul",
        "condition": "react_heart_50_times"
      }
    },
    "🔥": {
      "besitos": 3,
      "limit_per_user": 1,
      "unlock_hint": "You seem passionate. Check your DMs."
    },
    "🤔": {
      "besitos": 1,
      "trigger_trivia": "trivia_about_this_post"
    }
  }
}
```

Cuando un usuario reacciona:
1. El bot recibe `MessageReactionUpdated`
2. Verifica configuración de reacciones para ese post
3. Verifica que el usuario no haya excedido límites
4. Otorga recompensas definidas
5. Dispara triggers especiales (enviar DM, activar trivia, etc.)

**Análisis de Engagement**

El sistema recopila métricas de reacciones:

Posts con más reacciones de cada tipo.
Usuarios más activos reaccionando.
Correlación entre tipo de contenido y reacciones recibidas.
Efectividad de reacciones gamificadas vs no gamificadas.

Estas métricas informan decisiones sobre qué tipo de contenido publicar.

### 5.4 Moderación y Control de Acceso

**Sistema de Roles**

Además de Free vs VIP, el sistema maneja roles administrativos:

Owner: Control total del bot y configuración.
Admin: Puede publicar contenido, gestionar suscripciones, moderar usuarios.
Content Creator: Puede crear y programar contenido pero no acceder a configuración del sistema.
Moderator: Puede moderar usuarios (banear, advertir) pero no modificar contenido.

Los permisos se verifican antes de cada acción administrativa usando decorators:

```python
@require_role('admin')
def publish_content(user_id, content):
    # Solo admins pueden ejecutar esto
    pass
```

**Moderación de Usuarios**

El sistema incluye herramientas para manejar usuarios problemáticos:

Advertencias: Sistema de tres strikes antes de ban.
Bans temporales: Suspender acceso por días/semanas.
Bans permanentes: Bloqueo total con opción de apelar.
Shadowban: Usuario cree que participa normalmente pero sus acciones no afectan al sistema.

Cada acción de moderación se registra con razón, evidencia y admin responsable para accountability.

---

## 6. Sistema de Configuración Centralizada

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

---

## 7. Integración y Flujos Cruzados

La verdadera potencia de DianaBot emerge cuando los módulos trabajan en conjunto perfectamente sincronizados.

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

**Flujo: Usuario Gana Subasta**

1. Subasta termina, el módulo de Gamificación determina ganador
2. Gamificación publica evento: `gamification.auction_won`

```python
event_bus.publish('gamification.auction_won', {
    'user_id': 67890,
    'auction_id': 42,
    'item_key': 'legendary_sword',
    'final_bid': 750
})
```

3. Gamificación ejecuta transacción:
   - Debita 750 besitos del ganador
   - Agrega item al inventario del ganador
   - Retorna besitos a otros pujadores

4. Módulo de Narrativa escucha evento y:
   - Verifica si el item ganado desbloquea fragmentos narrativos
   - Si sí, actualiza disponibilidad de fragmentos para ese usuario
   - Publica evento: `narrative.content_unlocked`

5. Módulo de Administración escucha evento y:
   - Envía notificación al ganador
   - Envía notificación a otros participantes
   - Registra resultados de subasta para analíticas
   - Programa siguiente subasta si es recurrente

6. Sistema de Achievements escucha evento y:
   - Verifica si usuario desbloqueó "Primera Subasta Ganada"
   - Verifica si usuario desbloqueó "Coleccionista de Legendarios" (por poseer 5 items legendarios)

**Flujo: Suscripción VIP Expira**

1. Job programado detecta suscripción que expira
2. Módulo de Administración publica evento: `admin.subscription_expired`

```python
event_bus.publish('admin.subscription_expired', {
    'user_id': 11111,
    'subscription_type': 'monthly',
    'expiry_date': '2025-10-28T23:59:59Z',
    'had_auto_renew': false
})
```

3. Administración ejecuta:
   - Actualiza status de suscripción a 'expired'
   - Remueve usuario del canal VIP
   - Envía mensaje de despedida con link de renovación

4. Módulo de Narrativa escucha evento y:
   - Marca fragmentos VIP como inaccesibles para ese usuario
   - Si usuario está en medio de fragmento VIP, guarda progreso pero bloquea continuación
   - Publica evento: `narrative.access_revoked`

5. Módulo de Gamificación escucha evento y:
   - Desactiva misiones exclusivas VIP del usuario
   - Mantiene items y besitos ganados (no se pierden al expirar VIP)
   - Marca achievements VIP como "inaccesibles actualmente"

6. Sistema de Notificaciones:
   - Programa reminder en 7 días: "Te extrañamos, renueva tu VIP..."
   - Programa reminder en 30 días con oferta especial

### 7.3 Handlers de Eventos Complejos

Algunos eventos desencadenan lógica compleja que involucra múltiples sistemas.

**Handler: Decision Made → Cascade Effects**

```python
@event_handler('narrative.decision_made')
def handle_decision_cascade(event_data):
    """
    Maneja los efectos en cascada de una decisión narrativa
    """
    user_id = event_data['user_id']
    fragment_key = event_data['fragment_key']
    decision = event_data['decision_made']
    
    # 1. Obtener configuración de consecuencias
    fragment = get_fragment(fragment_key)
    consequences = fragment.get_decision_consequences(decision)
    
    # 2. Aplicar cambios narrativos
    if 'narrative_flags' in consequences:
        update_user_narrative_flags(user_id, consequences['narrative_flags'])
    
    if 'trust_changes' in consequences:
        update_trust_levels(user_id, consequences['trust_changes'])
    
    # 3. Otorgar recompensas inmediatas
    if 'immediate_rewards' in consequences:
        rewards = consequences['immediate_rewards']
        
        if 'besitos' in rewards:
            grant_besitos(user_id, rewards['besitos'], source='decision_reward')
        
        if 'items' in rewards:
            for item_key in rewards['items']:
                add_item_to_inventory(user_id, item_key)
        
        if 'unlock_fragments' in rewards:
            for fragment_key in rewards['unlock_fragments']:
                unlock_fragment(user_id, fragment_key)
    
    # 4. Activar misiones condicionales
    if 'trigger_missions' in consequences:
        for mission_key in consequences['trigger_missions']:
            assign_mission(user_id, mission_key)
    
    # 5. Verificar achievements
    check_decision_based_achievements(user_id, fragment_key, decision)
    
    # 6. Publicar eventos derivados
    if consequences.get('important', False):
        event_bus.publish('narrative.major_decision', {
            'user_id': user_id,
            'decision': decision,
            'consequences': consequences
        })
```

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

### 7.4 Manejo de Fallos y Resiliencia

Los eventos pueden fallar al procesarse. El sistema debe ser resiliente:

**Dead Letter Queue**

Si un handler falla repetidamente, el evento va a una Dead Letter Queue para revisión manual:

```python
class ResilientEventHandler:
    def __init__(self, handler_func, max_retries=3):
        self.handler_func = handler_func
        self.max_retries = max_retries
    
    def handle(self, event):
        retries = 0
        while retries < self.max_retries:
            try:
                self.handler_func(event)
                return True
            except Exception as e:
                retries += 1
                log_error(f"Handler failed (attempt {retries})", e)
                
                if retries < self.max_retries:
                    time.sleep(2 ** retries)  # exponential backoff
                else:
                    # Mover a Dead Letter Queue
                    self.move_to_dlq(event, str(e))
                    return False
    
    def move_to_dlq(self, event, error):
        redis_client.lpush('dianabot:dlq', json.dumps({
            'event': event,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }))
        
        # Notificar a administradores
        notify_admins('Event processing failed', event, error)
```

**Idempotencia**

Los handlers deben ser idempotentes (ejecutarlos múltiples veces con el mismo evento produce el mismo resultado):

```python
@idempotent_handler
def grant_besitos_handler(event_data):
    """
    Este handler es idempotente usando el event_id como deduplication key
    """
    event_id = event_data['event_id']
    user_id = event_data['user_id']
    amount = event_data['amount']
    
    # Verificar si ya procesamos este evento
    if redis_client.exists(f'processed_event:{event_id}'):
        log_info(f"Event {event_id} already processed, skipping")
        return
    
    # Procesar
    grant_besitos(user_id, amount)
    
    # Marcar como procesado (expira en 7 días)
    redis_client.setex(
        f'processed_event:{event_id}', 
        604800,  # 7 días en segundos
        '1'
    )
```

---

## 8. Seguridad y Escalabilidad

### 8.1 Seguridad

**Protección de Datos de Usuario**

Los datos de usuarios deben protegerse rigurosamente:

Encriptación en reposo: Datos sensibles en la base de datos se encriptan usando AES-256. Esto incluye información de pago, información personal identificable, y mensajes privados.

Encriptación en tránsito: Todas las comunicaciones con la API de Telegram usan HTTPS/TLS 1.3.

Tokens y Secretos: El bot token de Telegram nunca se hardcodea, siempre se almacena en variables de entorno o servicios de gestión de secretos como AWS Secrets Manager o HashiCorp Vault.

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

Transacciones Atómicas: Todas las operaciones con besitos usan transacciones de base de datos para prevenir duplicación o pérdida.

Audit Logs Inmutables: Cada transacción de besitos genera registro que no puede editarse ni eliminarse, solo agregarse.

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

**Protección contra Ataques**

SQL Injection: Usar siempre queries parametrizadas con ORM. Nunca interpolar strings directamente en SQL.

XSS en Panel Admin: Sanitizar todo input de usuarios antes de renderizar en HTML. Usar Content Security Policy headers.

CSRF: Implementar tokens CSRF para todas las acciones administrativas.

Callback Data Tampering: Firmar callback_data con HMAC:

```python
import hmac
import hashlib

SECRET_KEY = os.getenv('CALLBACK_SECRET')

def create_secure_callback(data):
    """Crea callback data con firma de seguridad"""
    payload = json.dumps(data)
    signature = hmac.new(
        SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()[:16]  # primeros 16 chars de la firma
    
    return f"{signature}:{base64.b64encode(payload.encode()).decode()}"

def verify_callback(callback_data):
    """Verifica y decodifica callback data"""
    try:
        signature, encoded_payload = callback_data.split(':', 1)
        payload = base64.b64decode(encoded_payload).decode()
        
        expected_signature = hmac.new(
            SECRET_KEY.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        
        if not hmac.compare_digest(signature, expected_signature):
            raise SecurityException("Invalid callback signature")
        
        return json.loads(payload)
    except Exception as e:
        log_security_event('callback_tampering_attempt', callback_data)
        raise SecurityException("Callback verification failed")
```

DDoS Protection: Usar rate limiting agresivo para endpoints públicos. Implementar CAPTCHA para acciones sensibles tras múltiples intentos fallidos.

### 8.2 Escalabilidad

DianaBot debe escalar de decenas a miles o millones de usuarios sin degradación.

**Escalabilidad de Base de Datos**

Particionamiento (Sharding): Para escalar PostgreSQL horizontalmente, particionar por user_id:

```python
# Usuarios 0-999999 → DB Shard 1
# Usuarios 1000000-1999999 → DB Shard 2
# etc.

def get_db_shard(user_id):
    shard_number = user_id // 1000000
    return f'dianabot_shard_{shard_number}'
```

Índices Estratégicos: Crear índices en columnas frecuentemente consultadas:

```sql
CREATE INDEX idx_user_balances_user_id ON user_balances(user_id);
CREATE INDEX idx_transactions_user_id_created ON transactions(user_id, created_at DESC);
CREATE INDEX idx_user_inventory_user_id ON user_inventory(user_id);
CREATE INDEX idx_narrative_progress_user ON user_narrative_progress(user_id);
CREATE INDEX idx_subscriptions_status_end_date ON subscriptions(status, end_date) 
    WHERE status = 'active';
```

Connection Pooling: Usar pgBouncer para gestionar conexiones eficientemente:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'pgbouncer',  # no directamente a PostgreSQL
        'PORT': 6432,
        'CONN_MAX_AGE': 600,  # conexiones persistentes
        'OPTIONS': {
            'MAX_CONNS': 100,
            'POOL_MODE': 'transaction'
        }
    }
}
```

Read Replicas: Consultas de solo lectura (analíticas, dashboard) se dirigen a réplicas:

```python
class UserBalance(models.Model):
    class Meta:
        db_table = 'user_balances'
    
    # Para lecturas
    @classmethod
    def get_balance(cls, user_id):
        return cls.objects.using('read_replica').get(user_id=user_id)
    
    # Para escrituras
    def save(self, *args, **kwargs):
        return super().save(*args, using='default', **kwargs)
```

**Escalabilidad de Caché**

Redis debe escalar con el sistema. Estrategias:

Redis Cluster: Para datasets mayores a la RAM de un solo servidor:

```python
from rediscluster import RedisCluster

startup_nodes = [
    {"host": "redis-1", "port": "6379"},
    {"host": "redis-2", "port": "6379"},
    {"host": "redis-3", "port": "6379"}
]

redis_client = RedisCluster(
    startup_nodes=startup_nodes,
    decode_responses=True
)
```

Cache Warming: Pre-cargar datos frecuentemente accedidos:

```python
def warm_cache_for_active_users():
    """Pre-carga datos de usuarios activos en caché"""
    active_user_ids = get_active_users_last_hour()
    
    for user_id in active_user_ids:
        # Pre-cargar balance
        balance = UserBalance.objects.get(user_id=user_id)
        cache.set(f'balance:{user_id}', balance.besitos, timeout=3600)
        
        # Pre-cargar inventario
        inventory = list(UserInventory.objects.filter(user_id=user_id)
                        .values_list('item_id', flat=True))
        cache.set(f'inventory:{user_id}', inventory, timeout=3600)
        
        # Pre-cargar progreso narrativo
        progress = get_narrative_progress(user_id)
        cache.set(f'narrative:{user_id}', progress, timeout=3600)
```

TTL Inteligente: Datos que cambian raramente tienen TTL más largo:

```python
cache.set(f'item_catalog', all_items, timeout=86400)  # 24 horas
cache.set(f'balance:{user_id}', balance, timeout=300)  # 5 minutos
cache.set(f'current_fragment:{user_id}', fragment, timeout=60)  # 1 minuto
```

**Escalabilidad de Procesamiento**

Celery para Tareas Pesadas: Operaciones que no requieren respuesta inmediata se procesan asíncronamente:

```python
@celery_app.task
def process_mission_completion(user_id, mission_id):
    """Procesa completación de misión de manera asíncrona"""
    mission = Mission.objects.get(mission_id=mission_id)
    
    # Otorgar recompensas
    grant_besitos(user_id, mission.rewards['besitos'])
    
    # Agregar items
    for item_key in mission.rewards.get('items', []):
        add_item_to_inventory(user_id, item_key)
    
    # Verificar achievements
    check_mission_achievements(user_id)
    
    # Enviar notificación
    send_notification(user_id, f"¡Misión '{mission.title}' completada!")

# Invocar de manera asíncrona
process_mission_completion.delay(user_id, mission_id)
```

Worker Pools: Múltiples workers de Celery procesan tareas en paralelo:

```bash
# 4 workers generales
celery -A dianabot worker --concurrency=4 -Q general

# 2 workers para tareas pesadas de narrativa
celery -A dianabot worker --concurrency=2 -Q narrative_heavy

# 2 workers para gamificación
celery -A dianabot worker --concurrency=2 -Q gamification
```

Load Balancing: Múltiples instancias del bot detrás de un load balancer:

```
         ┌──────────────┐
Usuario ─┤ Load Balancer├─┐
         └──────────────┘ │
                          ├─→ Bot Instance 1
                          ├─→ Bot Instance 2
                          ├─→ Bot Instance 3
                          └─→ Bot Instance 4
```

Cada instancia puede manejar requests independientemente. El estado compartido está en Redis y PostgreSQL.

**Escalabilidad de Telegram Bot**

Webhook vs Long Polling: Para alta escala, usar webhooks:

```python
# En lugar de long polling
# updater.start_polling()

# Usar webhook
application.run_webhook(
    listen='0.0.0.0',
    port=8443,
    url_path='telegram_webhook',
    webhook_url=f'https://dianabot.com/telegram_webhook'
)
```

Los webhooks escalan mejor porque Telegram envía actualizaciones directamente a tu servidor, eliminando la necesidad de polling constante.

Request Batching: Agrupar múltiples operaciones similares:

```python
def send_bulk_notifications(user_notifications):
    """Envía notificaciones en batch para eficiencia"""
    for batch in chunks(user_notifications, 30):  # Telegram permite ~30 req/s
        for user_id, message in batch:
            bot.send_message(user_id, message)
        time.sleep(1)  # respetar rate limits
```

**Monitoreo y Alertas**

Implementar monitoreo robusto para detectar problemas antes de que afecten usuarios:

```python
import prometheus_client as prom

# Métricas personalizadas
besitos_transactions = prom.Counter(
    'besitos_transactions_total',
    'Total besitos transactions',
    ['transaction_type']
)

narrative_fragment_completions = prom.Counter(
    'narrative_fragments_completed_total',
    'Total narrative fragments completed'
)

active_users = prom.Gauge(
    'active_users_current',
    'Currently active users'
)

response_time = prom.Histogram(
    'response_time_seconds',
    'Response time for bot interactions'
)

# Uso
besitos_transactions.labels(transaction_type='earn').inc()
response_time.observe(0.234)
```

Alertas automáticas cuando:
- Tasa de errores > 1%
- Tiempo de respuesta promedio > 2 segundos
- Uso de DB connections > 80%
- Redis memory > 90%
- Usuarios activos caen súbitamente 50%

---

## 9. Monetización y Roles

### 9.1 Estrategia de Monetización

DianaBot tiene múltiples flujos de ingresos diseñados para ser sostenibles sin ser intrusivos.

**Suscripciones VIP**

El modelo de suscripción es el pilar principal:

Tiers de Suscripción:
- VIP Mensual: $9.99/mes
- VIP Trimestral: $24.99 (17% descuento)
- VIP Anual: $89.99 (25% descuento)

Beneficios VIP claramente diferenciados:
- Acceso a niveles narrativos 4-6 (contenido exclusivo)
- Misiones VIP con recompensas premium
- Items exclusivos en tienda
- Doble besitos en misiones diarias
- Acceso prioritario a subastas
- Badge especial en perfil
- Canal VIP con contenido adicional

Funnel de Conversión:
1. Usuario free experimenta niveles 1-3 (contenido de alta calidad)
2. Al completar nivel 3, mensaje: "La historia continúa en nivel 4. ¡Hazte VIP!"
3. Trial period: 7 días gratis de VIP para usuarios enganchados
4. Recordatorios suaves durante trial
5. Al expirar trial, mensaje con descuento de "bienvenida de regreso" si se suscriben inmediatamente

**Tienda Virtual**

Venta de items digitales con dinero real o besitos:

Items con Dinero Real (micro-transacciones):
- Pack pequeño de besitos: 500 besitos por $2.99
- Pack mediano: 1,500 besitos por $7.99 (mejor valor)
- Pack grande: 4,000 besitos por $17.99 (mejor valor aún)
- Items cosméticos exclusivos: $0.99 - $4.99
- Bundles narrativos: "Pack Completo Temporada 1" por $14.99

Items con Besitos (economía interna):
- Items narrativos: 50-200 besitos
- Coleccionables: 30-100 besitos
- Power-ups: 40-150 besitos
- Items raros de subastas: 300-1000 besitos

**Modelo Freemium Balanceado**

El contenido gratuito debe ser suficientemente satisfactorio para retener usuarios, pero el contenido premium debe ser irresistible:

Ratio de Contenido:
- 40% completamente gratis (niveles 1-3, misiones básicas)
- 30% alcanzable con esfuerzo free (comprando con besitos ganados)
- 30% exclusivamente VIP (niveles 4-6, items ultra-raros)

Limitaciones Free sin Frustrar:
- Límite de inventario (20 slots vs 50 VIP)
- Límite de besitos ganables por día (200 vs 500 VIP)
- Acceso a trivias (5 por día vs ilimitado VIP)
- Sin acceso a fragmentos secretos premium

### 9.2 Procesamiento de Pagos

Integración con múltiples procesadores para maximizar conversión:

**Telegram Stars (Recomendado)**

Telegram tiene su sistema nativo de pagos que es ideal para bots:

```python
from telegram import LabeledPrice

async def send_invoice(update, context):
    """Envía invoice para suscripción VIP"""
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="DianaBot VIP - Mensual",
        description="Acceso completo a todos los niveles narrativos y beneficios exclusivos",
        payload=f"vip_subscription:monthly:{user_id}",
        provider_token=PROVIDER_TOKEN,
        currency="USD",
        prices=[
            LabeledPrice("Suscripción Mensual", 999)  # en centavos
        ],
        start_parameter="vip-monthly"
    )

async def handle_successful_payment(update, context):
    """Maneja pago exitoso"""
    payment = update.message.successful_payment
    
    # Activar suscripción
    activate_vip_subscription(
        user_id=update.effective_user.id,
        subscription_type='monthly',
        payment_reference=payment.telegram_payment_charge_id
    )
    
    # Enviar confirmación
    await update.message.reply_text(
        "¡Bienvenido a VIP! Tu suscripción está activa. "
        "Accede ahora a los niveles 4-6 y disfruta todos los beneficios."
    )
```

**Stripe (Alternativa)**

Para usuarios que prefieren pagar fuera de Telegram:

```python
import stripe

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def create_checkout_session(user_id, subscription_type):
    """Crea sesión de pago en Stripe"""
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_monthly_vip',  # ID del precio en Stripe
            'quantity': 1,
        }],
        mode='subscription',
        success_url=f'https://dianabot.com/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url='https://dianabot.com/payment/cancel',
        client_reference_id=str(user_id),
        metadata={
            'user_id': user_id,
            'subscription_type': subscription_type
        }
    )
    
    return session.url

# Webhook para confirmar pago
@app.post('/stripe/webhook')
async def stripe_webhook(request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    event = stripe.Webhook.construct_event(
        payload, sig_header, STRIPE_WEBHOOK_SECRET
    )
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = int(session['client_reference_id'])
        
        # Activar suscripción
        activate_vip_subscription(user_id, 'monthly', session['id'])
    
    return {'status': 'success'}
```

**Refunds y Cancelaciones**

Política clara de reembolsos:

```python
def handle_refund_request(user_id, reason):
    """Procesa solicitud de reembolso"""
    subscription = get_active_subscription(user_id)
    
    if not subscription:
        return {'success': False, 'message': 'No active subscription'}
    
    # Política: reembolso completo si cancela en primeros 48 horas
    hours_since_start = (datetime.now() - subscription.start_date).total_hours()
    
    if hours_since_start <= 48:
        # Reembolso completo
        process_refund(subscription.payment_reference, full=True)
        deactivate_subscription(subscription.subscription_id)
        
        return {
            'success': True,
            'message': 'Full refund processed',
            'amount': subscription.amount
        }
    else:
        # Cancelar pero no reembolsar
        cancel_subscription_at_period_end(subscription.subscription_id)
        
        return {
            'success': True,
            'message': 'Subscription will cancel at period end',
            'access_until': subscription.end_date
        }
```

### 9.3 Sistema de Roles y Permisos

Más allá de Free/VIP, el sistema soporta roles granulares para gestión:

**Jerarquía de Roles**

```python
class Role(Enum):
    OWNER = 1000        # Acceso total
    ADMIN = 800         # Gestión de contenido y usuarios
    MODERATOR = 600     # Moderación de usuarios
    CONTENT_CREATOR = 400  # Crear contenido pero no publicar
    VIP_USER = 200      # Acceso a contenido VIP
    FREE_USER = 100     # Acceso básico
    BANNED = 0          # Sin acceso

class Permission(Enum):
    # Contenido
    CREATE_CONTENT = 'create_content'
    EDIT_CONTENT = 'edit_content'
    DELETE_CONTENT = 'delete_content'
    PUBLISH_CONTENT = 'publish_content'
    
    # Usuarios
    VIEW_USERS = 'view_users'
    MANAGE_SUBSCRIPTIONS = 'manage_subscriptions'
    BAN_USERS = 'ban_users'
    
    # Configuración
    EDIT_CONFIGURATION = 'edit_configuration'
    VIEW_ANALYTICS = 'view_analytics'
    
    # Gamificación
    GRANT_BESITOS = 'grant_besitos'
    CREATE_ITEMS = 'create_items'

# Mapeo de roles a permisos
ROLE_PERMISSIONS = {
    Role.OWNER: [perm for perm in Permission],  # todos los permisos
    Role.ADMIN: [
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT,
        Permission.DELETE_CONTENT,
        Permission.PUBLISH_CONTENT,
        Permission.VIEW_USERS,
        Permission.MANAGE_SUBSCRIPTIONS,
        Permission.BAN_USERS,
        Permission.VIEW_ANALYTICS,
        Permission.GRANT_BESITOS,
        Permission.CREATE_ITEMS
    ],
    Role.MODERATOR: [
        Permission.VIEW_USERS,
        Permission.BAN_USERS,
        Permission.VIEW_ANALYTICS
    ],
    Role.CONTENT_CREATOR: [
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT
    ]
}
```

**Verificación de Permisos**

```python
def has_permission(user_id, permission):
    """Verifica si usuario tiene permiso específico"""
    user_role = get_user_role(user_id)
    return permission in ROLE_PERMISSIONS.get(user_role, [])

def require_permission(permission):
    """Decorator para proteger funciones con permisos"""
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user_id = update.effective_user.id
            
            if not has_permission(user_id, permission):
                await update.message.reply_text(
                    "No tienes permisos para realizar esta acción."
                )
                return
            
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

# Uso
@require_permission(Permission.PUBLISH_CONTENT)
async def publish_fragment(update, context):
    """Solo admins y owners pueden publicar"""
    # lógica de publicación
    pass
```

---

## 10. Documentación Técnica y Especificaciones

### 10.1 Estructura del Repositorio

```
dianabot/
├── bot/
│   ├── __init__.py
│   ├── main.py                 # Entry point del bot
│   ├── handlers/               # Handlers de Telegram
│   │   ├── __init__.py
│   │   ├── narrative.py        # Handlers de narrativa
│   │   ├── gamification.py     # Handlers de gamificación
│   │   ├── admin.py            # Handlers administrativos
│   │   └── payments.py         # Handlers de pagos
│   ├── commands/               # Comandos del bot
│   │   ├── start.py
│   │   ├── help.py
│   │   └── stats.py
│   └── keyboards/              # Teclados inline
│       ├── narrative_keyboards.py
│       └── shop_keyboards.py
├── core/
│   ├── __init__.py
│   ├── event_bus.py            # Sistema de eventos
│   ├── config_manager.py       # Gestión de configuración
│   └── user_state.py           # Gestión de estado de usuario
├── modules/
│   ├── narrative/
│   │   ├── __init__.py
│   │   ├── engine.py           # Motor de narrativa
│   │   ├── models.py           # Modelos de fragmentos, niveles
│   │   └── unlocks.py          # Sistema de desbloqueos
│   ├── gamification/
│   │   ├── __init__.py
│   │   ├── besitos.py          # Economía de besitos
│   │   ├── inventory.py        # Sistema de inventario
│   │   ├── missions.py         # Sistema de misiones
│   │   ├── achievements.py     # Sistema de logros
│   │   ├── auctions.py         # Sistema de subastas
│   │   └── trivias.py          # Sistema de trivias
│   └── admin/
│       ├── __init__.py
│       ├── subscriptions.py    # Gestión de VIP
│       ├── channels.py         # Gestión de canales
│       ├── publishing.py       # Sistema de publicación
│       └── moderation.py       # Herramientas de moderación
├── api/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── routers/
│   │   ├── config.py           # Endpoints de configuración
│   │   ├── analytics.py        # Endpoints de analíticas
│   │   └── webhooks.py         # Webhooks de pagos
│   └── middleware/
│       ├── auth.py             # Autenticación JWT
│       └── rate_limit.py       # Rate limiting
├── dashboard/
│   ├── templates/              # Templates HTML del panel admin
│   ├── static/                 # CSS, JS, imágenes
│   └── views.py                # Vistas del dashboard
├── database/
│   ├── models.py               # Modelos SQLAlchemy/Django ORM
│   ├── migrations/             # Migraciones de DB
│   └── seeds/                  # Datos iniciales
├── tasks/
│   ├── __init__.py
│   ├── celery_app.py           # Configuración de Celery
│   ├── scheduled.py            # Tareas programadas (cron)
│   └── async_tasks.py          # Tareas asíncronas
├── utils/
│   ├── __init__.py
│   ├── security.py             # Funciones de seguridad
│   ├── validators.py           # Validadores
│   └── helpers.py              # Helpers generales
├── config/
│   ├── settings.py             # Configuración general
│   ├── database.py             # Configuración de DB
│   └── redis.py                # Configuración de Redis
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
│   ├── architecture.md
│   ├── api_reference.md
│   └── deployment.md
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
├── requirements.txt
├── .env.example
└── README.md
```

### 10.2 Stack Tecnológico Final Recomendado

**Backend:**
- Python 3.11+
- python-telegram-bot 20.x
- FastAPI 0.104+
- SQLAlchemy 2.0+ (ORM)
- Pydantic 2.0+ (validación)
- Celery 5.3+ (tareas asíncronas)

**Bases de Datos:**
- PostgreSQL 15+ (datos relacionales)
- MongoDB 7+ (contenido flexible)
- Redis 7+ (caché y event bus)

**Infraestructura:**
- Docker & Docker Compose
- Nginx (reverse proxy y load balancer)
- Gunicorn (WSGI server para API)
- Prometheus + Grafana (monitoreo)
- Sentry (error tracking)

**Frontend (Dashboard Admin):**
- HTML5, CSS3, JavaScript
- Alpine.js o Vue.js (interactividad ligera)
- Tailwind CSS (estilos)
- Chart.js (gráficas)

**Servicios Externos:**
- Cloudflare (CDN y DDoS protection)
- AWS S3 o equivalent (almacenamiento de media)
- Stripe y/o Telegram Stars (pagos)

### 10.3 Ejemplo de Flujo Completo End-to-End

Veamos un ejemplo completo desde la perspectiva del usuario y del sistema:

**Escenario: Usuario Completa Experiencia Narrativa y Desbloquea Contenido**

Usuario: María, free user, acaba de completar fragmento 3 del nivel 1.

1. María hace click en decisión "Acercarte con confianza"

2. Bot recibe callback desde Telegram:
```python
callback_data = "decision:fragment_003:choice_confident:user_67890"
```

3. Handler de callback decodifica y verifica integridad:
```python
@callback_handler('decision:')
async def handle_decision(update, context):
    callback_data = verify_callback(update.callback_query.data)
    
    user_id = update.effective_user.id
    fragment_key = callback_data['fragment_key']
    decision = callback_data['choice']
    
    # Procesar decisión
    result = narrative_engine.process_decision(
        user_id, fragment_key, decision
    )
```

4. Motor de Narrativa ejecuta:
```python
def process_decision(user_id, fragment_key, decision):
    # Obtener fragmento y consecuencias
    fragment = get_fragment(fragment_key)
    consequences = fragment.get_consequences(decision)
    
    # Actualizar estado narrativo
    update_narrative_flags(user_id, consequences['flags'])
    
    # Registrar completación
    record_completion(user_id, fragment_key, decision)
    
    # Publicar evento
    event_bus.publish('narrative.fragment_completed', {
        'user_id': user_id,
        'fragment_key': fragment_key,
        'decision': decision,
        'consequences': consequences
    })
    
    # Retornar siguiente fragmento
    next_fragment = get_fragment(consequences['next_fragment'])
    return next_fragment
```

5. Módulo de Gamificación escucha evento y otorga recompensas:
```python
@event_handler('narrative.fragment_completed')
def handle_fragment_reward(event):
    user_id = event['user_id']
    fragment_key = event['fragment_key']
    
    # Obtener recompensas configuradas
    fragment = NarrativeFragment.objects.get(fragment_key=fragment_key)
    rewards = fragment.rewards
    
    # Otorgar besitos
    if 'besitos' in rewards:
        grant_besitos(user_id, rewards['besitos'], f'fragment:{fragment_key}')
    
    # Agregar items
    if 'items' in rewards:
        for item_key in rewards['items']:
            add_to_inventory(user_id, item_key)
            
            # Verificar si item desbloquea contenido
