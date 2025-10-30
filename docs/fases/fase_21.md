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

# Fase 21: Fragmentos Secretos y Metajuego

### Objetivo
Contenido oculto y mecánicas de descubrimiento

### Componentes a Implementar

#### 21.1 Marcado de Fragmentos Secretos
- **Modificar**: Modelo de fragmentos
- **Referencia**: Sección 3.4 - Fragmentos Ocultos y Metajuego
- **Archivos**:
  - `database/models.py` (añadir campo is_secret a NarrativeFragment)
- **Funcionalidad**:
  - Fragmentos no aparecen en progreso normal
  - Solo visibles al desbloquear

#### 21.2 Sistema de Pistas
- **Crear**: Mecánica de códigos y pistas
- **Referencia**: Sección 3.4 - Fragmentos Ocultos
- **Archivos**:
  - `modules/narrative/secrets.py`
- **Funciones**:
  - `submit_secret_code(user_id, code)`
  - `verify_secret_code(code)`
  - `unlock_secret_fragment(user_id, fragment_key)`
  - `get_discovered_secrets(user_id)`

#### 21.3 Combinación de Items
- **Crear**: Desbloqueo por poseer items específicos
- **Referencia**: Sección 3.4 - Fragmentos Ocultos
- **Modificar**: `modules/narrative/unlocks.py`
- **Funcionalidad**:
  - Verificar si usuario tiene combinación de items
  - Auto-desbloquear fragmento secreto
  - Notificar descubrimiento

#### 21.4 Pistas en Canales
- **Crear**: Posts con códigos encriptados
- **Referencia**: Sección 3.4 - Fragmentos Ocultos
- **Archivos**:
  - `modules/admin/secrets_posting.py`
- **Funcionalidad**:
  - Publicar pistas periódicas
  - Códigos cifrados simples
  - Acertijos narrativos

#### 21.5 Comando de Secretos
- **Crear**: Interface para secretos
- **Archivos**:
  - `bot/commands/secrets.py`
- **Comandos**:
  - `/secret <code>`: Ingresar código secreto
  - `/secrets`: Ver secretos descubiertos
  - `/hint`: Pista sobre próximo secreto

#### 21.6 Contador de Secretos
- **Crear**: Achievement por descubrir todos
- **Referencia**: Sección 4.6 - Sistema de Logros
- **Funcionalidad**:
  - Achievement "Maestro de Secretos"
  - Tracking de secretos descubiertos vs totales
  - Recompensa épica al completar todos

#### 21.7 Fragmentos Secretos de Contenido
- **Crear**: 5 fragmentos secretos narrativos
- **Referencia**: Sección 3.4 - Fragmentos Ocultos
- **Archivos**:
  - `database/seeds/narrative_seed.py` (secretos)
- **Contenido**:
  - Backstories de personajes
  - Endings alternativos
  - Lore profundo
  - Revelaciones importantes

### Resultado de Fase 21
✓ Sistema de secretos funcional
✓ Fragmentos ocultos descubribles
✓ Pistas y códigos funcionando
✓ Metajuego de exploración
✓ 5+ secretos implementados
✓ Engagement a largo plazo

## Referencias
### 3.4 Fragmentos Ocultos y Metajuego

Algunos fragmentos son "secretos" y no aparecen en el flujo normal. Los usuarios los descubren mediante:

Pistas en otros canales: Un mensaje en el canal VIP contiene un código encriptado. Resolverlo revela el `fragment_key` de un fragmento secreto.

Combinaciones de items: Poseer simultáneamente "ancient_map" y "decoder_ring" desbloquea automáticamente un fragmento oculto sobre el pasado de Lucien.

Exploración de paths alternativos: Si el usuario toma decisiones contraintuitivas en varios fragmentos, desbloquea un "bad ending" alternativo.

El motor verifica periódicamente si el estado del usuario satisface condiciones de fragmentos ocultos y los hace aparecer dinámicamente en el mapa de narrativa del usuario.

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