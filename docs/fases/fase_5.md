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

# Fase 5: Tienda Virtual Básica

### Objetivo
Permitir compra de items con besitos

### Componentes a Implementar

#### 5.1 Servicio de Tienda
- **Crear**: Lógica de compra/venta
- **Referencia**: Sección 4.3 - Inventario (tienda virtual)
- **Archivos**:
  - `modules/gamification/shop.py`
- **Funciones**:
  - `get_shop_items(filters=None)`
  - `purchase_item(user_id, item_key)`
  - `can_afford(user_id, item_key)`

#### 5.2 Keyboard de Tienda
- **Crear**: Interface inline para navegar tienda
- **Referencia**: Sección 2.4 - Botones Inline y Callbacks
- **Archivos**:
  - `bot/keyboards/shop_keyboards.py`
- **Funcionalidad**:
  - Mostrar items con botones de compra
  - Paginación de items
  - Confirmación de compra

#### 5.3 Handlers de Compra
- **Crear**: Procesamiento de compras
- **Referencia**: Sección 4.1 - Economía de Besitos (sumideros)
- **Archivos**:
  - `bot/handlers/shop.py`
- **Callbacks**:
  - `shop:view:<page>`
  - `shop:buy:<item_key>`
  - `shop:confirm:<item_key>`
- **Validaciones**:
  - Fondos suficientes
  - Item existe y está disponible
  - Transacción atómica (restar besitos + agregar item)

#### 5.4 Comando de Tienda
- **Crear**: Entry point a la tienda
- **Referencia**: Sección 4.3 - Gestión de Inventario
- **Archivos**:
  - `bot/commands/shop.py`
- **Comando**:
  - `/shop`: Abrir tienda con items disponibles

#### 5.5 Eventos de Tienda
- **Crear**: Tracking de compras
- **Referencia**: Sección 7.2 - Ejemplos de Flujos Integrados
- **Eventos**:
  - `gamification.item_purchased`
  - Incluye: user_id, item_key, price_paid

### Resultado de Fase 5
✓ Tienda funcional con items comprables
✓ Economía de besitos tiene sumidero
✓ Transacciones de compra auditadas
✓ Base para monetización futura

## Referencias
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

### 2.4 Integración con API de Telegram

**Botones Inline y Callbacks**

Los botones inline son el mecanismo principal de interacción para decisiones narrativas y compras. Cada botón incluye un `callback_data` que codifica la acción. Por ejemplo: `"decision:fragment_005:choice_b:user_12345"`. El handler de callback decodifica esto, verifica que el usuario tenga acceso al fragmento, procesa la decisión, actualiza el estado y responde con el siguiente fragmento.

Para prevenir que usuarios maliciosos manipulen callbacks, incluimos un hash HMAC en cada callback_data que valida la integridad del mensaje.

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