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

# Fase 15: Trivias Básicas

### Objetivo
Sistema de preguntas con recompensas

### Componentes a Implementar

#### 15.1 Colección de Trivias en MongoDB
- **Crear**: Estructura de preguntas
- **Referencia**: Sección 2.3 - MongoDB (colección `trivia_questions`)
- **Archivos**:
  - `database/mongo_schemas.py` (schema de trivia)
- **Estructura**: question, options[], correct_option, rewards, time_limit

#### 15.2 Servicio de Trivias
- **Crear**: Lógica de trivias
- **Referencia**: Sección 4.5 - Sistema de Trivias
- **Archivos**:
  - `modules/gamification/trivias.py`
- **Funciones**:
  - `get_random_trivia(category=None, difficulty=None)`
  - `submit_answer(user_id, trivia_id, answer, response_time)`
  - `get_trivia_stats(user_id)`

#### 15.3 Seeders de Trivias
- **Crear**: Preguntas de prueba
- **Referencia**: Sección 4.5 - Categorías de Preguntas
- **Archivos**:
  - `database/seeds/trivias_seed.py`
- **Contenido**:
  - 20 trivias sobre lore narrativo
  - Diferentes dificultades
  - Rewards variables

#### 15.4 Handlers de Trivias
- **Crear**: Interface de trivia
- **Archivos**:
  - `bot/handlers/trivias.py`
  - `bot/keyboards/trivia_keyboards.py`
- **Funcionalidad**:
  - Mostrar pregunta con opciones
  - Timer visual
  - Procesar respuesta
  - Mostrar resultado y reward

#### 15.5 Comando de Trivia
- **Crear**: Iniciar trivia
- **Archivos**:
  - `bot/commands/trivia.py`
- **Comando**:
  - `/trivia`: Trivia aleatoria
  - `/trivia <category>`: Trivia de categoría específica

#### 15.6 Trivias en Canales
- **Crear**: Publicar trivias programadas
- **Referencia**: Sección 5.2 - Tipos de Publicaciones
- **Modificar**: `modules/admin/post_templates.py`
- **Funcionalidad**:
  - Post tipo "trivia"
  - Botones de opciones inline
  - Auto-cierre después de tiempo límite
  - Anunciar ganadores

#### 15.7 Rate Limiting de Trivias
- **Crear**: Límites para prevenir farming
- **Referencia**: Sección 4.1 - Prevención de Inflación
- **Archivos**:
  - `utils/rate_limiter.py`
- **Funcionalidad**:
  - Máximo 10 trivias por día para free users
  - Ilimitado para VIP
  - Tracking en Redis

#### 15.8 Eventos de Trivias
- **Crear**: Publicar eventos de respuestas
- **Referencia**: Sección 7.1 - Eventos de Gamificación
- **Eventos**:
  - `gamification.trivia_answered`
  - Incluye: correct, response_time, rewards

### Resultado de Fase 15
✓ Sistema de trivias funcional
✓ Recompensas por respuestas correctas
✓ Rate limiting implementado
✓ Trivias en canales
✓ Estadísticas de trivias

## Referencias
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

### 2.3 Esquema de Bases de Datos

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

**Prevención de Inflación**

Para prevenir que besitos pierdan valor con el tiempo, implementamos:

Límites de farming: Cada fuente de besitos tiene caps diarios o semanales. No puedes ganar infinitos besitos repitiendo trivias.

Besitos que expiran: Los besitos "bonus" obtenidos de eventos especiales expiran en 30 días si no se usan. Esto incentiva gasto activo.

Items de alto valor: La tienda siempre ofrece items premium caros (500-1000 besitos) para que usuarios avanzados tengan objetivos de ahorro.

Impuestos en subastas: Las subastas cobran una pequeña comisión del 10% que se elimina del sistema, actuando como sumidero.

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