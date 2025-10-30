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

# Fase 10: Narrativa Ramificada

### Objetivo
Expandir narrativa con ramificaciones reales y consecuencias

### Componentes a Implementar

#### 10.1 Sistema de Flags Narrativos
- **Crear**: Tracking de decisiones importantes
- **Referencia**: Sección 3.2 - Persistencia del Estado Narrativo
- **Archivos**:
  - `database/models.py` (añadir campo narrative_flags a UserNarrativeProgress)
  - `modules/narrative/flags.py`
- **Funciones**:
  - `set_narrative_flag(user_id, flag_name, value)`
  - `get_narrative_flag(user_id, flag_name)`
  - `has_narrative_flags(user_id, flags_list)`

#### 10.2 Decisiones con Consecuencias
- **Modificar**: Motor narrativo para aplicar consecuencias
- **Referencia**: Sección 3.1 - Narrativa Ramificada
- **Modificar**: `modules/narrative/engine.py`
- **Funcionalidad**:
  - Aplicar flags según decisión tomada
  - Actualizar variables de relación con personajes
  - Determinar siguiente fragmento según contexto

#### 10.3 Condiciones Basadas en Flags
- **Modificar**: Desbloqueos considerando flags
- **Referencia**: Sección 3.3 - Desbloqueos Condicionales
- **Modificar**: `modules/narrative/unlocks.py`
- **Funcionalidad**:
  - Evaluar condiciones de tipo "narrative_flag"
  - Fragmentos accesibles solo con ciertas decisiones previas
  - Múltiples caminos según flags acumulados

#### 10.4 Contenido Narrativo Ramificado
- **Crear**: Niveles 2 y 3 con ramificaciones
- **Referencia**: Sección 3.1 - Estructura de Grafo Dirigido
- **Archivos**:
  - `database/seeds/narrative_seed.py` (expandir)
- **Contenido**:
  - Nivel 2: 5 fragmentos con 2 caminos paralelos
  - Nivel 3: 7 fragmentos con 3 endings diferentes
  - Decisiones que afectan diálogos futuros
  - Items que desbloquean opciones especiales

#### 10.5 Personalización de Contenido
- **Crear**: Sistema de interpolación de variables
- **Referencia**: Sección 3.2 - Motor de Narrativa
- **Archivos**:
  - `modules/narrative/templating.py`
- **Funcionalidad**:
  - Reemplazar variables en texto narrativo
  - Ejemplo: `{{trust_lucien > 5 ? 'querido amigo' : 'visitante'}}`
  - Diálogos personalizados según flags

#### 10.6 Visualización de Caminos
- **Modificar**: Comando de progreso muestra ramificaciones
- **Modificar**: `bot/commands/progress.py`
- **Funcionalidad**:
  - Mostrar decisiones tomadas
  - Indicar caminos alternativos disponibles
  - Sugerir replay para ver otros endings

### Resultado de Fase 10
✓ Narrativa con múltiples caminos
✓ Decisiones tienen consecuencias reales
✓ Contenido personalizado según decisiones
✓ Rejugabilidad implementada
✓ 3 niveles completos (15+ fragmentos)

## Referencias
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