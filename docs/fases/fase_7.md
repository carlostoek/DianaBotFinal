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

# Fase 7: Sistema de Desbloqueos

### Objetivo
Condicionar acceso a fragmentos según requisitos

### Componentes a Implementar

#### 7.1 Motor de Desbloqueos
- **Crear**: Sistema que evalúa condiciones
- **Referencia**: Sección 3.3 - Desbloqueos Condicionales Complejos
- **Archivos**:
  - `modules/narrative/unlocks.py`
- **Funciones**:
  - `evaluate_conditions(user_id, conditions)`
  - `check_unlock_status(user_id, fragment_key)`
  - `get_missing_requirements(user_id, conditions)`
- **Tipos de Condiciones**:
  - Besitos mínimos
  - Items en inventario
  - Fragmentos completados
  - Combinaciones con AND/OR

#### 7.2 Actualizar Motor Narrativo
- **Modificar**: Verificar desbloqueos antes de mostrar fragmento
- **Referencia**: Sección 3.3 - Desbloqueos Condicionales
- **Modificar**: `modules/narrative/engine.py`
- **Funcionalidad**:
  - Antes de mostrar fragmento, verificar condiciones
  - Si no cumple, mostrar requisitos faltantes
  - Ofrecer links a tienda si necesita items/besitos

#### 7.3 Fragmentos con Requisitos
- **Crear**: Nuevos fragmentos que requieren condiciones
- **Archivos**:
  - `database/seeds/narrative_seed.py` (añadir fragmentos)
- **Contenido**:
  - 2 fragmentos que requieren 50 besitos
  - 1 fragmento que requiere item específico
  - 1 fragmento que requiere haber completado otros 2

#### 7.4 Visualización de Progreso
- **Crear**: Comando que muestra mapa de narrativa
- **Referencia**: Sección 3.1 - Sistema de Narrativa Ramificada
- **Archivos**:
  - `bot/commands/progress.py`
- **Comando**:
  - `/progress`: Mostrar fragmentos completados, disponibles y bloqueados
  - Indicar requisitos para fragmentos bloqueados

### Resultado de Fase 7
✓ Fragmentos bloqueados por condiciones
✓ Sistema de desbloqueos flexible
✓ Usuarios entienden qué necesitan para avanzar
✓ Economía tiene propósito (desbloquear contenido)

## Referencias
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