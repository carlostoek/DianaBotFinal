# DianaBot: Hoja de Ruta de Implementación Gradual

## Principios de la Hoja de Ruta

✅ **Desarrollo Incremental**: Cada fase construye sobre la anterior
✅ **Sin Dependencias Futuras**: Solo se implementa lo que tiene sus fundamentos listos
✅ **Testeable en Cada Paso**: Cada fase produce un bot funcional y testeable
✅ **Referencias al Documento**: Cada sección referencia la investigación técnica para detalles

---

## FASE 0: Preparación del Entorno (Días 1-3)

### Objetivo
Configurar infraestructura base y repositorio

### Componentes a Implementar

#### 0.1 Estructura de Repositorio
- **Crear**: Estructura completa de carpetas según investigación
- **Referencia**: Sección 10.1 - Estructura del Repositorio
- **Archivos**:
  - `README.md`
  - `.gitignore`
  - `requirements.txt` (dependencias base)
  - `.env.example`
  - Estructura de carpetas: `bot/`, `core/`, `modules/`, `database/`, etc.

#### 0.2 Docker y Base de Datos
- **Crear**: `docker/docker-compose.yml`
- **Servicios**: PostgreSQL, Redis, MongoDB
- **Referencia**: Sección 2.2 - Base de Datos: Enfoque Híbrido
- **Archivos**:
  - `docker/Dockerfile`
  - `docker/docker-compose.yml`
  - `config/database.py`
  - `config/redis.py`

#### 0.3 Configuración Base
- **Crear**: Sistema de configuración con variables de entorno
- **Referencia**: Sección 2.1 - Framework del Bot
- **Archivos**:
  - `config/settings.py`
  - `.env` (no subir a git)

### Resultado de Fase 0
✓ Repositorio estructurado
✓ Docker compose levanta servicios
✓ Conexión a bases de datos funciona

---

## FASE 1: Bot Básico y Sistema de Usuarios (Días 4-7)

### Objetivo
Bot responde a comandos básicos y registra usuarios

### Componentes a Implementar

#### 1.1 Bot Telegram Básico
- **Crear**: Entry point del bot
- **Referencia**: Sección 2.1 - Framework del Bot
- **Archivos**:
  - `bot/main.py`
  - `bot/handlers/__init__.py`
- **Funcionalidad**:
  - Inicializar bot con python-telegram-bot
  - Handler para `/start`
  - Handler para `/help`
  - Logging básico

#### 1.2 Modelo de Usuario
- **Crear**: Tabla y modelo de usuarios
- **Referencia**: Sección 2.3 - Esquema PostgreSQL (tabla `users`)
- **Archivos**:
  - `database/models.py` (modelo User)
  - `database/migrations/001_create_users.sql`
- **Campos**: user_id, telegram_username, created_at, last_active, user_state

#### 1.3 Registro Automático de Usuarios
- **Crear**: Sistema que detecta nuevo usuario y lo registra
- **Referencia**: Sección 2.3 - Esquema PostgreSQL
- **Archivos**:
  - `bot/handlers/start.py`
  - `core/user_state.py` (funciones básicas)
- **Funcionalidad**:
  - Al recibir `/start`, verificar si usuario existe
  - Si no existe, crear registro en DB
  - Responder con mensaje de bienvenida personalizado

#### 1.4 Comandos Básicos
- **Crear**: Handlers para comandos esenciales
- **Referencia**: Sección 10.1 - Estructura del Repositorio
- **Archivos**:
  - `bot/commands/help.py`
  - `bot/commands/stats.py` (stats básicos del usuario)
- **Funcionalidad**:
  - `/help`: Mostrar ayuda
  - `/stats`: Mostrar stats básicos (fecha registro, última actividad)

### Resultado de Fase 1
✓ Bot responde a `/start`, `/help`, `/stats`
✓ Usuarios se registran automáticamente en DB
✓ Se puede consultar info básica de usuario

---

## FASE 2: Event Bus y Logging (Días 8-10)

### Objetivo
Implementar sistema de eventos para comunicación entre módulos

### Componentes a Implementar

#### 2.1 Event Bus Core
- **Crear**: Sistema pub/sub con Redis
- **Referencia**: Sección 7.1 - Event Bus - Sistema Nervioso Central
- **Archivos**:
  - `core/event_bus.py`
- **Funcionalidad**:
  - Clase EventBus con métodos `publish()` y `subscribe()`
  - Conexión a Redis Pub/Sub
  - Sistema de serialización de eventos (JSON)

#### 2.2 Event Logger
- **Crear**: Sistema que guarda eventos en DB para auditoría
- **Referencia**: Sección 7.1 - Event Bus
- **Archivos**:
  - `database/models.py` (añadir modelo EventLog)
  - `database/migrations/002_create_event_logs.sql`
- **Campos**: event_id, event_type, event_data, timestamp

#### 2.3 Eventos Básicos de Usuario
- **Modificar**: Handlers existentes para publicar eventos
- **Referencia**: Sección 7.1 - Eventos Principales del Sistema
- **Archivos**:
  - `bot/handlers/start.py` (publicar evento `user.registered`)
  - `core/user_state.py` (publicar evento `user.command_executed`)
- **Eventos**:
  - `user.registered`
  - `user.command_executed`
  - `user.activity`

#### 2.4 Subscriber de Prueba
- **Crear**: Handler que escucha eventos y los registra
- **Referencia**: Sección 7.1 - Event Bus
- **Archivos**:
  - `core/event_handlers.py`
- **Funcionalidad**:
  - Suscribirse a eventos `user.*`
  - Loggear eventos recibidos
  - Actualizar `last_active` en DB

### Resultado de Fase 2
✓ Event Bus funcional con Redis
✓ Eventos se publican y registran en DB
✓ Sistema de comunicación entre módulos establecido

---

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

---

## FASE 4: Inventario (Mochila) Básico (Días 15-18)

### Objetivo
Sistema de items sin mecánicas narrativas aún

### Componentes a Implementar

#### 4.1 Modelos de Items e Inventario
- **Crear**: Tablas de items y posesiones de usuario
- **Referencia**: Sección 2.3 - PostgreSQL (tablas `items`, `user_inventory`)
- **Archivos**:
  - `database/models.py` (modelos Item, UserInventory)
  - `database/migrations/004_create_items_inventory.sql`
- **Campos**: item_id, item_key, name, description, item_type, rarity, price_besitos

#### 4.2 Servicio de Inventario
- **Crear**: Lógica para gestionar inventario
- **Referencia**: Sección 4.3 - Inventario (Mochila) y Sistema de Items
- **Archivos**:
  - `modules/gamification/inventory.py`
- **Funciones**:
  - `add_item_to_inventory(user_id, item_key, quantity=1)`
  - `remove_item_from_inventory(user_id, item_key, quantity=1)`
  - `get_user_inventory(user_id)`
  - `has_item(user_id, item_key)`

#### 4.3 Seeders de Items Básicos
- **Crear**: Items de prueba para testing
- **Referencia**: Sección 4.3 - Categorías de Items
- **Archivos**:
  - `database/seeds/items_seed.py`
- **Items de Prueba**:
  - 5 items coleccionables
  - 3 items consumibles básicos
  - 2 items narrativos (sin función aún)

#### 4.4 Comandos de Inventario
- **Crear**: Visualización de inventario
- **Referencia**: Sección 4.3 - Gestión de Inventario
- **Archivos**:
  - `bot/commands/inventory.py`
- **Comandos**:
  - `/inventory`: Mostrar items con paginación
  - `/item <item_name>`: Ver detalles de item

#### 4.5 Eventos de Inventario
- **Crear**: Publicar eventos al modificar inventario
- **Referencia**: Sección 7.1 - Eventos de Gamificación
- **Modificar**: `modules/gamification/inventory.py`
- **Eventos**:
  - `gamification.item_acquired`
  - `gamification.item_used`

### Resultado de Fase 4
✓ Sistema de inventario funcional
✓ Items almacenados en DB
✓ Usuarios pueden ver su inventario
✓ Base para tienda e items narrativos

---

## FASE 5: Tienda Virtual Básica (Días 19-22)

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

---

## FASE 6: Motor de Narrativa Core (Días 23-30)

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
- **Archivos**:
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

---

## FASE 7: Sistema de Desbloqueos (Días 31-35)

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

---

## FASE 8: Misiones Básicas (Días 36-42)

### Objetivo
Sistema de misiones sin complejidad excesiva

### Componentes a Implementar

#### 8.1 Modelos de Misiones
- **Crear**: Tablas de misiones y progreso
- **Referencia**: Sección 2.3 - PostgreSQL (tablas `missions`, `user_missions`)
- **Archivos**:
  - `database/models.py` (modelos Mission, UserMission)
  - `database/migrations/006_create_missions_tables.sql`
- **Campos**: mission_id, mission_key, title, requirements, rewards, recurrence

#### 8.2 Servicio de Misiones
- **Crear**: Lógica de misiones
- **Referencia**: Sección 4.2 - Sistema de Misiones
- **Archivos**:
  - `modules/gamification/missions.py`
- **Funciones**:
  - `assign_mission(user_id, mission_key)`
  - `update_mission_progress(user_id, mission_id, progress)`
  - `complete_mission(user_id, mission_id)`
  - `get_active_missions(user_id)`
  - `get_available_missions(user_id)`

#### 8.3 Seeders de Misiones
- **Crear**: Misiones de prueba
- **Referencia**: Apéndice G - Ejemplo de Configuración de Misión
- **Archivos**:
  - `database/seeds/missions_seed.py`
- **Misiones**:
  - Misión diaria: "Completa 1 fragmento" (20 besitos)
  - Misión diaria: "Reclama tu regalo diario" (10 besitos)
  - Misión semanal: "Completa 5 fragmentos" (100 besitos)
  - Misión narrativa: "Alcanza nivel 2" (50 besitos + item)

#### 8.4 Tracking Automático de Misiones
- **Crear**: Handlers que detectan progreso en misiones
- **Referencia**: Sección 4.2 - Tracking de Progreso
- **Archivos**:
  - `core/event_handlers.py` (añadir handlers)
- **Funcionalidad**:
  - Escuchar eventos relevantes (fragment_completed, besitos_earned, etc.)
  - Actualizar progreso de misiones activas
  - Auto-completar cuando se alcanza target
  - Otorgar recompensas automáticamente

#### 8.5 Comandos de Misiones
- **Crear**: Interface para ver y gestionar misiones
- **Archivos**:
  - `bot/commands/missions.py`
- **Comandos**:
  - `/missions`: Ver misiones activas con progreso
  - `/mission <id>`: Ver detalles de misión específica

#### 8.6 Sistema de Asignación Diaria
- **Crear**: Job que asigna misiones diarias
- **Referencia**: Sección 4.2 - Asignación Inteligente de Misiones
- **Archivos**:
  - `tasks/scheduled.py`
  - `tasks/celery_app.py`
- **Funcionalidad**:
  - Cron job a las 9 AM (configurable)
  - Asignar misiones diarias a todos los usuarios activos
  - Resetear progreso de misiones expiradas

#### 8.7 Eventos de Misiones
- **Crear**: Tracking de eventos de misiones
- **Referencia**: Sección 7.1 - Eventos de Gamificación
- **Eventos**:
  - `gamification.mission_assigned`
  - `gamification.mission_progress_updated`
  - `gamification.mission_completed`

### Resultado de Fase 8
✓ Sistema de misiones funcional
✓ Tracking automático de progreso
✓ Misiones diarias y semanales funcionando
✓ Recompensas automáticas al completar
✓ Engagement diario incentivado

---

## FASE 9: Achievements (Logros) (Días 43-47)

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

---

## FASE 10: Narrativa Ramificada (Días 48-56)

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

---

## FASE 11: Sistema de Suscripciones VIP (Días 57-63)

### Objetivo
Gestión de usuarios VIP y contenido premium

### Componentes a Implementar

#### 11.1 Modelo de Suscripciones
- **Crear**: Tabla de suscripciones
- **Referencia**: Sección 2.3 - PostgreSQL (tabla `subscriptions`)
- **Archivos**:
  - `database/models.py` (modelo Subscription)
  - `database/migrations/008_create_subscriptions.sql`
- **Campos**: subscription_id, user_id, subscription_type, start_date, end_date, status

#### 11.2 Servicio de Suscripciones
- **Crear**: Lógica de gestión de VIP
- **Referencia**: Sección 5.1 - Gestión de Suscripciones VIP
- **Archivos**:
  - `modules/admin/subscriptions.py`
- **Funciones**:
  - `create_subscription(user_id, type, duration_days)`
  - `get_active_subscription(user_id)`
  - `is_vip(user_id)`
  - `cancel_subscription(subscription_id)`
  - `get_expiring_subscriptions(days_before)`

#### 11.3 Verificación de Acceso VIP
- **Crear**: Middleware de verificación
- **Referencia**: Sección 8.1 - Control de Acceso VIP
- **Archivos**:
  - `modules/admin/vip_access.py`
- **Funciones**:
  - `verify_vip_access(user_id, resource_type, resource_id)`
  - Verificación multicapa (DB + caché)

#### 11.4 Contenido VIP
- **Crear**: Fragmentos de nivel 4 (VIP)
- **Referencia**: Sección 11.1 - Fase 4: Módulo de Administración
- **Archivos**:
  - `database/seeds/narrative_seed.py` (añadir nivel 4)
- **Contenido**:
  - Nivel 4 marcado como VIP
  - 5 fragmentos exclusivos
  - Verificación de VIP antes de acceso

#### 11.5 Jobs de Gestión VIP
- **Crear**: Tareas programadas para suscripciones
- **Referencia**: Sección 5.1 - Recordatorios y Expiraciones
- **Archivos**:
  - `tasks/scheduled.py` (añadir jobs)
- **Jobs**:
  - Recordatorio 7 días antes de expirar
  - Recordatorio 24 horas antes
  - Expiración automática al vencer
  - Actualizar user_state a 'free'

#### 11.6 Comandos VIP
- **Crear**: Gestión de suscripción desde bot
- **Archivos**:
  - `bot/commands/vip.py`
- **Comandos**:
  - `/vip`: Ver status de suscripción
  - `/upgrade`: Info sobre beneficios VIP

#### 11.7 Notificaciones VIP
- **Crear**: Mensajes automáticos sobre suscripción
- **Referencia**: Sección 5.1 - Recordatorios y Expiraciones
- **Archivos**:
  - `modules/admin/notifications.py`
- **Funcionalidad**:
  - Notificar al activar VIP
  - Recordatorios antes de expirar
  - Mensaje al expirar con opción de renovar

### Resultado de Fase 11
✓ Sistema VIP funcional
✓ Contenido exclusivo para suscriptores
✓ Verificación automática de acceso
✓ Notificaciones de expiración
✓ Diferenciación clara entre free y VIP

---

## FASE 12: Canales de Telegram (Días 64-70)

### Objetivo
Gestión de canales free y VIP

### Componentes a Implementar

#### 12.1 Modelo de Canales
- **Crear**: Tabla de configuración de canales
- **Referencia**: Sección 2.3 - PostgreSQL (tabla `channels`)
- **Archivos**:
  - `database/models.py` (modelo Channel)
  - `database/migrations/009_create_channels.sql`
- **Campos**: channel_id, channel_type, channel_username, settings

#### 12.2 Servicio de Canales
- **Crear**: Gestión de canales
- **Referencia**: Sección 5.2 - Gestión de Contenido en Canales
- **Archivos**:
  - `modules/admin/channels.py`
- **Funciones**:
  - `configure_channel(channel_id, channel_type, settings)`
  - `get_channel_config(channel_id)`
  - `verify_channel_membership(user_id, channel_id)`

#### 12.3 Invitaciones Automáticas
- **Crear**: Sistema de invitación a canales VIP
- **Referencia**: Sección 5.1 - Flujo de Suscripción VIP
- **Modificar**: `modules/admin/subscriptions.py`
- **Funcionalidad**:
  - Al activar VIP, generar link de invitación único
  - Enviar link por DM
  - Verificar que usuario se unió

#### 12.4 Expulsión Automática
- **Crear**: Job que remueve usuarios expirados
- **Referencia**: Sección 5.1 - Jobs de Gestión VIP
- **Archivos**:
  - `tasks/scheduled.py` (añadir job)
- **Funcionalidad**:
  - Detectar suscripciones expiradas
  - Remover de canal VIP
  - Mantener en canal free

#### 12.5 Handlers de Canales
- **Crear**: Respuestas a eventos en canales
- **Archivos**:
  - `bot/handlers/channels.py`
- **Funcionalidad**:
  - Detectar nuevos miembros
  - Mensaje de bienvenida personalizado
  - Detectar usuarios que salieron

### Resultado de Fase 12
✓ Canales free y VIP gestionados
✓ Invitaciones automáticas a VIP
✓ Expulsión automática al expirar
✓ Verificación de membresía funcional

---

## FASE 13: Publicación de Contenido (Días 71-77)

### Objetivo
Sistema de publicación programada en canales

### Componentes a Implementar

#### 13.1 Modelo de Posts
- **Crear**: Tabla de publicaciones
- **Referencia**: Sección 2.3 - PostgreSQL (tabla `channel_posts`)
- **Archivos**:
  - `database/models.py` (modelo ChannelPost)
  - `database/migrations/010_create_channel_posts.sql`
- **Campos**: post_id, channel_id, post_type, content, scheduled_for, published_at

#### 13.2 Servicio de Publicación
- **Crear**: Lógica de posts
- **Referencia**: Sección 5.2 - Programación de Contenido
- **Archivos**:
  - `modules/admin/publishing.py`
- **Funciones**:
  - `create_post(channel_id, content, scheduled_for=None)`
  - `publish_post(post_id)`
  - `get_scheduled_posts()`
  - `cancel_post(post_id)`

#### 13.3 Scheduler de Publicaciones
- **Crear**: Job que publica contenido programado
- **Referencia**: Sección 5.2 - Publicaciones Programadas
- **Archivos**:
  - `tasks/scheduled.py` (añadir job)
- **Funcionalidad**:
  - Ejecutar cada minuto
  - Buscar posts con `scheduled_for <= now`
  - Publicar en canal correspondiente
  - Marcar como publicado

#### 13.4 Tipos de Posts
- **Crear**: Templates para diferentes tipos
- **Referencia**: Sección 5.2 - Tipos de Publicaciones
- **Archivos**:
  - `modules/admin/post_templates.py`
- **Tipos**:
  - Post narrativo (fragmento + botón)
  - Post de misión (anuncio + botón aceptar)
  - Post de anuncio (solo texto/media)
  - Post de evento (con countdown)

#### 13.5 Posts Recurrentes
- **Crear**: Sistema de posts que se repiten
- **Referencia**: Sección 5.2 - Publicaciones Recurrentes
- **Modificar**: `modules/admin/publishing.py`
- **Funcionalidad**:
  - Campo `recurrence` en posts
  - Después de publicar, reprogramar según recurrencia
  - Ejemplos: daily, weekly, monthly

#### 13.6 Protección de Contenido
- **Crear**: Configuración de protección
- **Referencia**: Sección 5.2 - Protección de Contenido
- **Modificar**: `modules/admin/publishing.py`
- **Funcionalidad**:
  - Flag `protect_content` en posts
  - Prevenir forward y screenshots en posts VIP

### Resultado de Fase 13
✓ Sistema de publicación programada
✓ Posts se publican automáticamente
✓ Recurrencia implementada
✓ Contenido VIP protegido
✓ Múltiples tipos de posts soportados

---

## FASE 14: Reacciones Gamificadas (Días 78-82)

### Objetivo
Vincular reacciones en canales con recompensas

### Componentes a Implementar

#### 14.1 Configuración de Reacciones
- **Crear**: Sistema de rewards por reacción
- **Referencia**: Sección 5.3 - Sistema de Reacciones Vinculadas
- **Archivos**:
  - `database/models.py` (añadir campo reaction_rewards a ChannelPost)
  - `modules/admin/reactions.py`
- **Estructura**: Mapeo de emoji → recompensa + límite

#### 14.2 Handler de Reacciones
- **Crear**: Detector de reacciones en posts
- **Referencia**: Sección 5.3 - Configuración de Reacciones Gamificadas
- **Archivos**:
  - `bot/handlers/reactions.py`
- **Funcionalidad**:
  - Recibir `MessageReactionUpdated`
  - Identificar post y reacción
  - Verificar configuración de rewards
  - Verificar límites por usuario
  - Otorgar recompensas

#### 14.3 Tracking de Reacciones
- **Crear**: Registro de reacciones por usuario/post
- **Archivos**:
  - `database/models.py` (modelo UserReaction)
  - `database/migrations/011_create_reactions_tracking.sql`
- **Funcionalidad**:
  - Prevenir duplicados
  - Respetar límites configurados
  - Auditar reacciones para analíticas

#### 14.4 Integración con Misiones
- **Crear**: Misiones que requieren reacciones
- **Referencia**: Apéndice G - Ejemplo de Configuración de Misión
- **Modificar**: `modules/gamification/missions.py`
- **Funcionalidad**:
  - Tipo de tarea: "react_to_posts"
  - Tracking automático vía eventos
  - Contar solo reacciones válidas

#### 14.5 Eventos de Reacciones
- **Crear**: Publicar eventos de reacción
- **Referencia**: Sección 7.1 - Eventos Administrativos
- **Eventos**:
  - `admin.reaction_added`
  - Incluye: user_id, post_id, emoji, rewards_granted

### Resultado de Fase 14
✓ Reacciones otorgan recompensas
✓ Límites respetados
✓ Integrado con misiones
✓ Engagement en canales incentivado

---

## FASE 15: Trivias Básicas (Días 83-88)

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

---

## FASE 16: Configuration Manager (Días 89-98)

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

---

## FASE 17: API REST (FastAPI) (Días 99-106)

### Objetivo
API para panel administrativo

### Componentes a Implementar

#### 17.1 Setup de FastAPI
- **Crear**: Aplicación FastAPI
- **Referencia**: Sección 10.2 - Stack Tecnológico
- **Archivos**:
  - `api/main.py`
  - `api/__init__.py`
  - `requirements.txt` (añadir FastAPI, uvicorn)

#### 17.2 Sistema de Autenticación
- **Crear**: JWT auth para admins
- **Referencia**: Sección 9.3 - Sistema de Roles y Permisos
- **Archivos**:
  - `api/middleware/auth.py`
  - `database/models.py` (modelo AdminUser)
  - `database/migrations/014_create_admin_users.sql`
- **Funcionalidad**:
  - Login con username/password
  - Generar JWT token
  - Middleware de verificación
  - Roles y permisos

#### 17.3 Routers de Configuración
- **Crear**: Endpoints de config
- **Referencia**: Sección 6.4 - API de Configuración Centralizada
- **Archivos**:
  - `api/routers/config.py`
- **Endpoints**:
  - `POST /api/config/templates`
  - `GET /api/config/templates/{id}`
  - `POST /api/config/instances`
  - `PUT /api/config/instances/{id}`
  - `DELETE /api/config/instances/{id}`
  - `POST /api/config/validate`
  - `POST /api/config/propagate/{id}`

#### 17.4 Routers de Usuarios
- **Crear**: Endpoints de gestión de usuarios
- **Archivos**:
  - `api/routers/users.py`
- **Endpoints**:
  - `GET /api/users`
  - `GET /api/users/{id}`
  - `PUT /api/users/{id}/subscription`
  - `POST /api/users/{id}/grant-besitos`
  - `GET /api/users/{id}/stats`

#### 17.5 Routers de Contenido
- **Crear**: Endpoints de gestión de contenido
- **Archivos**:
  - `api/routers/content.py`
- **Endpoints**:
  - Narrativa: CRUD de fragmentos
  - Gamificación: CRUD de items, misiones, achievements
  - Canales: CRUD de posts programados

#### 17.6 Routers de Analíticas
- **Crear**: Endpoints de métricas
- **Referencia**: Sección 12 - Métricas de Éxito y KPIs
- **Archivos**:
  - `api/routers/analytics.py`
- **Endpoints**:
  - `GET /api/metrics/summary`
  - `GET /api/metrics/engagement`
  - `GET /api/metrics/monetization`
  - `GET /api/metrics/narrative`

#### 17.7 Rate Limiting
- **Crear**: Limitación de requests
- **Referencia**: Sección 8.1 - Seguridad
- **Archivos**:
  - `api/middleware/rate_limit.py`
- **Funcionalidad**:
  - Límites por endpoint
  - Tracking en Redis
  - Headers de rate limit

#### 17.8 Documentación Automática
- **Configurar**: OpenAPI/Swagger
- **Funcionalidad**:
  - FastAPI genera automáticamente
  - Disponible en `/docs`
  - Modelos Pydantic para request/response

### Resultado de Fase 17
✓ API REST funcional
✓ Autenticación JWT
✓ Endpoints de configuración
✓ Endpoints de gestión
✓ Documentación automática
✓ Rate limiting

---

## FASE 18: Dashboard Web Básico (Días 107-119)

### Objetivo
Panel administrativo web

### Componentes a Implementar

#### 18.1 Setup de Frontend
- **Crear**: Estructura HTML/CSS/JS
- **Referencia**: Sección 10.2 - Frontend (Dashboard Admin)
- **Archivos**:
  - `dashboard/templates/base.html`
  - `dashboard/static/css/style.css`
  - `dashboard/static/js/app.js`
- **Tech Stack**: HTML5, Alpine.js, Tailwind CSS

#### 18.2 Vista de Login
- **Crear**: Página de autenticación
- **Archivos**:
  - `dashboard/templates/login.html`
  - `dashboard/views.py`
- **Funcionalidad**:
  - Form de login
  - Llamar API de auth
  - Guardar JWT en localStorage
  - Redirect a dashboard

#### 18.3 Dashboard Principal
- **Crear**: Vista de métricas principales
- **Referencia**: Sección 6.5 - Panel de Administración Unificado
- **Archivos**:
  - `dashboard/templates/dashboard.html`
- **Contenido**:
  - KPIs en tiempo real
  - Usuarios activos
  - Suscripciones VIP
  - Besitos en circulación
  - Alertas del sistema

#### 18.4 Vista de Usuarios
- **Crear**: Gestión de usuarios
- **Archivos**:
  - `dashboard/templates/users.html`
- **Funcionalidad**:
  - Lista de usuarios con filtros
  - Búsqueda
  - Ver detalles de usuario
  - Editar suscripción
  - Otorgar besitos manualmente

#### 18.5 Vista de Configuración Simple
- **Crear**: Interface básica de config
- **Referencia**: Sección 6.2 - Flujos de Configuración Unificada
- **Archivos**:
  - `dashboard/templates/config.html`
- **Funcionalidad**:
  - Lista de configuraciones
  - Crear nueva (forms básicos)
  - Editar existente
  - Ver historial de versiones

#### 18.6 Vista de Contenido
- **Crear**: Gestión de narrativa y gamificación
- **Archivos**:
  - `dashboard/templates/content.html`
- **Funcionalidad**:
  - CRUD de fragmentos narrativos
  - CRUD de items
  - CRUD de misiones
  - CRUD de achievements

#### 18.7 Vista de Publicaciones
- **Crear**: Gestión de posts en canales
- **Archivos**:
  - `dashboard/templates/posts.html`
- **Funcionalidad**:
  - Calendario de publicaciones
  - Crear nuevo post
  - Editar posts programados
  - Ver posts publicados

#### 18.8 Vista de Analíticas
- **Crear**: Dashboards de métricas
- **Referencia**: Sección 12.3 - Dashboard de KPIs
- **Archivos**:
  - `dashboard/templates/analytics.html`
  - `dashboard/static/js/charts.js`
- **Contenido**:
  - Gráficas de engagement
  - Gráficas de monetización
  - Gráficas de progreso narrativo
  - Usar Chart.js

### Resultado de Fase
` (modelos Auction, Bid)
  - `database/migrations/015_create_auctions_bids.sql`
- **Campos**: auction_id, item_id, start_price, current_bid, winner_id, status, end_time

#### 19.2 Servicio de Subastas
- **Crear**: Lógica de subastas
- **Referencia**: Sección 4.4 - Mecánica de Subasta
- **Archivos**:
  - `modules/gamification/auctions.py`
- **Funciones**:
  - `create_auction(item_key, start_price, duration_minutes)`
  - `place_bid(user_id, auction_id, amount)`
  - `get_active_auctions()`
  - `close_auction(auction_id)`
  - `get_auction_status(auction_id)`

#### 19.3 Locks Distribuidos
- **Crear**: Prevención de condiciones de carrera
- **Referencia**: Sección 4.4 - Prevención de Manipulación
- **Archivos**:
  - `utils/locks.py
  
  #### 19.3 Locks Distribuidos
- **Crear**: Prevención de condiciones de carrera
- **Referencia**: Sección 4.4 - Prevención de Manipulación
- **Archivos**:
  - `utils/locks.py`
- **Funcionalidad**:
  - Usar Redis para locks
  - Lock al procesar puja
  - Timeout automático

#### 19.4 Timer Dinámico
- **Crear**: Sistema de extensión de tiempo
- **Referencia**: Sección 4.4 - Mecánica de Subasta
- **Modificar**: `modules/gamification/auctions.py`
- **Funcionalidad**:
  - Si puja en últimos 60 segundos, extender 60s más
  - Prevenir "sniping"
  - Actualizar timer en tiempo real

#### 19.5 Handlers de Subastas
- **Crear**: Interface de subastas
- **Archivos**:
  - `bot/handlers/auctions.py`
  - `bot/keyboards/auction_keyboards.py`
- **Funcionalidad**:
  - Ver subastas activas
  - Pujar en subasta
  - Ver historial de pujas
  - Notificar cuando alguien supera tu puja

#### 19.6 Comando de Subastas
- **Crear**: Entry point
- **Archivos**:
  - `bot/commands/auctions.py`
- **Comandos**:
  - `/auctions`: Ver subastas activas
  - `/auction <id>`: Ver detalles de subasta específica

#### 19.7 Job de Cierre de Subastas
- **Crear**: Finalización automática
- **Referencia**: Sección 4.4 - Mecánica de Subasta
- **Archivos**:
  - `tasks/scheduled.py` (añadir job)
- **Funcionalidad**:
  - Ejecutar cada minuto
  - Cerrar subastas expiradas
  - Transferir item al ganador
  - Retornar besitos a perdedores
  - Notificar resultado

#### 19.8 Anuncios de Subastas
- **Crear**: Posts automáticos en canales
- **Referencia**: Sección 5.2 - Tipos de Publicaciones
- **Funcionalidad**:
  - Anunciar 24h antes
  - Post al iniciar subasta
  - Actualizaciones de puja importante
  - Anunciar ganador

#### 19.9 Eventos de Subastas
- **Crear**: Tracking de actividad
- **Referencia**: Sección 7.1 - Eventos de Gamificación
- **Eventos**:
  - `gamification.auction_started`
  - `gamification.bid_placed`
  - `gamification.auction_won`

### Resultado de Fase 19
✓ Sistema de subastas en tiempo real
✓ Pujas con locks distribuidos
✓ Timer dinámico anti-sniping
✓ Cierre automático
✓ Notificaciones a participantes
✓ Integrado con inventario y besitos

---

## FASE 20: Integración de Pagos (Días 127-136)

### Objetivo
Monetización real con procesadores de pago

### Componentes a Implementar

#### 20.1 Configuración de Telegram Stars
- **Crear**: Integración con Telegram Payments
- **Referencia**: Sección 9.2 - Procesamiento de Pagos (Telegram Stars)
- **Archivos**:
  - `modules/admin/payments.py`
  - `bot/handlers/payments.py`
- **Funcionalidad**:
  - Configurar provider token
  - Crear invoices

#### 20.2 Flujo de Suscripción VIP
- **Crear**: Proceso de compra
- **Referencia**: Sección 9.2 - Procesamiento de Pagos
- **Archivos**:
  - `bot/commands/subscribe.py`
- **Funcionalidad**:
  - Comando `/subscribe` muestra opciones (monthly, yearly)
  - Genera invoice
  - Maneja pre-checkout query
  - Procesa pago exitoso
  - Activa suscripción

#### 20.3 Handler de Pagos Exitosos
- **Crear**: Procesamiento post-pago
- **Referencia**: Sección 9.2 - Handler de Pagos
- **Modificar**: `bot/handlers/payments.py`
- **Funcionalidad**:
  - Recibir `successful_payment`
  - Activar suscripción VIP
  - Invitar a canal VIP
  - Enviar confirmación
  - Registrar transacción

#### 20.4 Configuración de Stripe (Alternativa)
- **Crear**: Integración con Stripe
- **Referencia**: Sección 9.2 - Procesamiento de Pagos (Stripe)
- **Archivos**:
  - `modules/admin/stripe_integration.py`
  - `api/routers/webhooks.py`
- **Funcionalidad**:
  - Crear checkout sessions
  - Webhook para confirmar pagos
  - Sincronizar con suscripciones

#### 20.5 Compra de Besitos
- **Crear**: Microtransacciones de besitos
- **Referencia**: Sección 9.1 - Tienda Virtual
- **Archivos**:
  - `bot/commands/buy_besitos.py`
- **Packs**:
  - 500 besitos - $2.99
  - 1500 besitos - $7.99
  - 4000 besitos - $17.99

#### 20.6 Sistema de Refunds
- **Crear**: Gestión de reembolsos
- **Referencia**: Sección 9.2 - Refunds y Cancelaciones
- **Archivos**:
  - `modules/admin/refunds.py`
- **Funcionalidad**:
  - Procesar solicitudes de refund
  - Política de 48 horas
  - Revertir suscripción si refund
  - Notificar usuario

#### 20.7 Registro de Transacciones
- **Crear**: Tabla de pagos
- **Archivos**:
  - `database/models.py` (modelo Payment)
  - `database/migrations/016_create_payments.sql`
- **Campos**: payment_id, user_id, amount, currency, payment_method, status, reference

#### 20.8 Dashboard de Ingresos
- **Crear**: Vista de monetización en dashboard
- **Referencia**: Sección 12.1 - Métricas de Producto
- **Archivos**:
  - `dashboard/templates/revenue.html`
- **Contenido**:
  - MRR (Monthly Recurring Revenue)
  - Total transacciones
  - Conversión rate
  - ARPU / ARPPU
  - Gráficas temporales

### Resultado de Fase 20
✓ Pagos reales implementados
✓ Suscripciones VIP comprables
✓ Microtransacciones de besitos
✓ Sistema de refunds
✓ Tracking completo de ingresos
✓ Dashboard de monetización

---

## FASE 21: Fragmentos Secretos y Metajuego (Días 137-143)

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

---

## FASE 22: Editor Visual de Narrativa (Días 144-154)

### Objetivo
Herramienta administrativa avanzada para crear narrativa

### Componentes a Implementar

#### 22.1 Backend de Editor
- **Crear**: API endpoints para editor
- **Referencia**: Sección 6.5 - Editor Visual de Flujos
- **Archivos**:
  - `api/routers/narrative_editor.py`
- **Endpoints**:
  - `GET /api/editor/fragments`: Lista de fragmentos
  - `GET /api/editor/graph/{level_id}`: Grafo de nivel
  - `POST /api/editor/fragments`: Crear fragmento
  - `PUT /api/editor/fragments/{id}`: Actualizar
  - `POST /api/editor/connections`: Crear conexión
  - `DELETE /api/editor/connections/{id}`: Eliminar

#### 22.2 Representación de Grafo
- **Crear**: Lógica de grafo dirigido
- **Referencia**: Sección 3.1 - Estructura de Grafo Dirigido
- **Archivos**:
  - `modules/narrative/graph.py`
- **Funciones**:
  - `build_narrative_graph(level_id)`
  - `detect_orphaned_fragments(graph)`
  - `detect_circular_dependencies(graph)`
  - `find_all_paths(start, end)`

#### 22.3 Vista de Editor Visual
- **Crear**: Interface drag-and-drop
- **Referencia**: Sección 6.5 - Editor Visual
- **Archivos**:
  - `dashboard/templates/editor.html`
  - `dashboard/static/js/narrative_editor.js`
- **Tecnología**: Librería de grafos (ej: vis.js, cytoscape.js)
- **Funcionalidad**:
  - Visualizar fragmentos como nodos
  - Visualizar decisiones como aristas
  - Drag-and-drop para mover
  - Click para editar
  - Crear conexiones arrastrando

#### 22.4 Modal de Edición de Fragmento
- **Crear**: Form completo de fragmento
- **Archivos**:
  - `dashboard/templates/components/fragment_modal.html`
- **Campos**:
  - Título, descripción
  - Contenido narrativo (editor de texto rico)
  - Decisiones (lista dinámica)
  - Condiciones de desbloqueo
  - Recompensas
  - Media (upload de imágenes)

#### 22.5 Validación Visual
- **Crear**: Indicadores de problemas
- **Referencia**: Sección 6.7 - Sistema de Validación
- **Funcionalidad**:
  - Nodos rojos = fragmentos huérfanos
  - Nodos amarillos = falta contenido
  - Aristas rojas = referencias inválidas
  - Panel de errores y warnings

#### 22.6 Simulador de Recorrido
- **Crear**: Previsualización de experiencia
- **Referencia**: Sección 6.7 - Simulador de Experiencias
- **Archivos**:
  - `dashboard/templates/simulator.html`
- **Funcionalidad**:
  - Elegir fragmento inicial
  - Navegar decisiones
  - Ver qué vería el usuario
  - Probar condiciones de desbloqueo

#### 22.7 Export/Import de Narrativa
- **Crear**: Portabilidad de contenido
- **Archivos**:
  - `api/routers/narrative_import_export.py`
- **Funcionalidad**:
  - Exportar nivel completo a JSON
  - Importar desde JSON
  - Validar antes de importar
  - Backup de narrativa

### Resultado de Fase 22
✓ Editor visual de narrativa
✓ Creación drag-and-drop
✓ Visualización de grafo
✓ Validación visual
✓ Simulador integrado
✓ Creación de contenido acelerada

---

## FASE 23: Asistentes de Configuración (Días 155-162)

### Objetivo
Wizards que guían creación de contenido complejo

### Componentes a Implementar

#### 23.1 Asistente de Experiencia Narrativa
- **Crear**: Wizard multi-paso
- **Referencia**: Sección 6.2 - Flujo: Crear Experiencia Narrativa-Gamificada
- **Archivos**:
  - `dashboard/templates/wizards/experience_wizard.html`
  - `dashboard/static/js/wizards/experience.js`
- **Pasos**:
  1. Info básica (título, descripción, nivel)
  2. Requisitos de acceso
  3. Fragmentos narrativos (editor simplificado)
  4. Recompensas unificadas
  5. Programación de publicación
  6. Validación y preview
  7. Confirmación

#### 23.2 Asistente de Misión
- **Crear**: Wizard de misiones
- **Referencia**: Apéndice G - Ejemplo de Configuración de Misión
- **Archivos**:
  - `dashboard/templates/wizards/mission_wizard.html`
- **Pasos**:
  1. Tipo de misión (daily, weekly, narrative)
  2. Requisitos (qué debe hacer usuario)
  3. Recompensas
  4. Recurrencia y asignación
  5. Validación

#### 23.3 Asistente de Evento
- **Crear**: Wizard para eventos especiales
- **Archivos**:
  - `dashboard/templates/wizards/event_wizard.html`
- **Pasos**:
  1. Info del evento (nombre, duración)
  2. Contenido (narrativa temporal)
  3. Misiones exclusivas del evento
  4. Items exclusivos
  5. Publicaciones en canales
  6. Programación

#### 23.4 Validación en Tiempo Real
- **Crear**: Validadores asíncronos
- **Referencia**: Sección 6.3 - Asistentes Inteligentes
- **Archivos**:
  - `api/routers/validation.py`
- **Endpoints**:
  - `POST /api/validate/besitos`: Validar monto de besitos
  - `POST /api/validate/item-ref`: Verificar item existe
  - `POST /api/validate/coherence`: Verificar coherencia general

#### 23.5 Sugerencias Contextuales
- **Crear**: Sistema de sugerencias
- **Referencia**: Sección 6.3 - Asistentes Inteligentes
- **Funcionalidad**:
  - Sugerir recompensas según dificultad
  - Sugerir precios de items según rareza
  - Alertar sobre posibles inconsistencias
  - Recomendar mejores prácticas

#### 23.6 Templates Predefinidos
- **Crear**: Plantillas reutilizables
- **Referencia**: Sección 6.3 - Plantillas Predefinidas
- **Archivos**:
  - `core/config_templates/` (expandir)
- **Templates**:
  - "Experiencia Narrativa Simple"
  - "Evento de Fin de Semana"
  - "Cadena de Misiones"
  - "Subasta de Item Legendario"

### Resultado de Fase 23
✓ Asistentes de creación funcionales
✓ Wizards paso a paso
✓ Validación en tiempo real
✓ Sugerencias inteligentes
✓ Templates predefinidos
✓ Creación de contenido simplificada

---

## FASE 24: Optimizaciones y Performance (Días 163-171)

### Objetivo
Mejorar rendimiento y escalabilidad

### Componentes a Implementar

#### 24.1 Índices de Base de Datos
- **Crear**: Índices optimizados
- **Referencia**: Sección 8.2 - Escalabilidad de Base de Datos
- **Archivos**:
  - `database/migrations/017_create_indexes.sql`
- **Índices**:
  - Todos los índices mencionados en investigación
  - Índices compuestos para queries frecuentes
  - Índices parciales para filtros comunes

#### 24.2 Caching Estratégico
- **Crear**: Sistema de caché multicapa
- **Referencia**: Sección 8.2 - Escalabilidad de Caché
- **Archivos**:
  - `core/cache.py`
- **Funcionalidad**:
  - Cache warming para usuarios activos
  - TTLs diferenciados por tipo de dato
  - Invalidación inteligente de caché
  - Cache-aside pattern

#### 24.3 Connection Pooling
- **Configurar**: Pools de conexiones
- **Referencia**: Sección 8.2 - Escalabilidad de Base de Datos
- **Archivos**:
  - `config/database.py` (actualizar)
- **Funcionalidad**:
  - pgBouncer para PostgreSQL
  - Pool de conexiones Redis
  - Pool de conexiones MongoDB
  - Configuración óptima de tamaños

#### 24.4 Query Optimization
- **Optimizar**: Queries lentas
- **Referencia**: Sección 8.2 - Escalabilidad de Base de Datos
- **Funcionalidad**:
  - Identificar queries lentas (logs)
  - Reescribir con JOINs eficientes
  - Eager loading vs lazy loading
  - Pagination para listas grandes

#### 24.5 Background Tasks
- **Optimizar**: Celery workers
- **Referencia**: Sección 8.2 - Escalabilidad de Procesamiento
- **Archivos**:
  - `tasks/celery_app.py` (configurar)
- **Configuración**:
  - Worker pools separados por tipo
  - Concurrency óptima
  - Rate limiting de tasks
  - Retry policies

#### 24.6 Response Compression
- **Crear**: Compresión de responses
- **Archivos**:
  - `api/middleware/compression.py`
- **Funcionalidad**:
  - Gzip para responses grandes
  - Minificación de JSON
  - Compresión de imágenes

#### 24.7 Load Testing
- **Crear**: Suite de load tests
- **Referencia**: Sección 11.2 - Testing Estratégico
- **Archivos**:
  - `tests/load/locustfile.py`
- **Scenarios**:
  - 100 usuarios simultáneos
  - 500 usuarios simultáneos
  - 1000 usuarios simultáneos
  - Identificar breaking points

#### 24.8 Monitoring de Performance
- **Crear**: Métricas de performance
- **Referencia**: Sección 12.2 - Métricas Técnicas
- **Archivos**:
  - `core/monitoring.py`
- **Métricas**:
  - Response times por endpoint
  - Database query times
  - Cache hit rates
  - Memory usage
  - CPU usage

### Resultado de Fase 24
✓ Sistema optimizado
✓ Response times < 500ms
✓ Cache hit rate > 80%
✓ Queries optimizadas
✓ Load testing completado
✓ Monitoring de performance

---

## FASE 25: Testing Exhaustivo (Días 172-185)

### Objetivo
Cobertura de tests completa

### Componentes a Implementar

#### 25.1 Tests Unitarios Completos
- **Crear**: Tests para cada módulo
- **Referencia**: Sección 11.2 - Testing Estratégico
- **Archivos**:
  - `tests/unit/test_besitos.py`
  - `tests/unit/test_inventory.py`
  - `tests/unit/test_narrative.py`
  - `tests/unit/test_missions.py`
  - `tests/unit/test_achievements.py`
  - etc.
- **Cobertura**: Mínimo 70%

#### 25.2 Tests de Integración
- **Crear**: Tests de flujos completos
- **Referencia**: Sección 11.2 - Tests de Integración
- **Archivos**:
  - `tests/integration/test_narrative_flow.py`
  - `tests/integration/test_purchase_flow.py`
  - `tests/integration/test_mission_completion.py`
  - `tests/integration/test_vip_subscription.py`
- **Escenarios**: Todos los flujos críticos

#### 25.3 Tests End-to-End
- **Crear**: Tests simulando usuarios reales
- **Archivos**:
  - `tests/e2e/test_user_journey.py`
- **Journeys**:
  - Usuario nuevo completa onboarding
  - Usuario completa primer nivel
  - Usuario compra item y lo usa
  - Usuario se suscribe a VIP

#### 25.4 Tests de Event Bus
- **Crear**: Verificación de eventos
- **Archivos**:
  - `tests/integration/test_event_bus.py`
- **Funcionalidad**:
  - Eventos se publican correctamente
  - Handlers reciben eventos
  - No hay eventos perdidos
  - Idempotencia funciona

#### 25.5 Tests de Seguridad
- **Crear**: Tests de vulnerabilidades
- **Referencia**: Sección 8.1 - Seguridad
- **Archivos**:
  - `tests/security/test_auth.py`
  - `tests/security/test_sql_injection.py`
  - `tests/security/test_rate_limiting.py`
- **Verificaciones**:
  - No SQL injection
  - No XSS
  - Auth funciona correctamente
  - Rate limiting efectivo

#### 25.6 Tests de Economía
- **Crear**: Verificación de balance económico
- **Archivos**:
  - `tests/unit/test_economy.py`
- **Escenarios**:
  - No se pueden crear besitos de la nada
  - Transacciones son atómicas
  - Balance nunca negativo
  - Auditoría completa

#### 25.7 CI/CD Pipeline
- **Crear**: Automatización de tests
- **Archivos**:
  - `.github/workflows/test.yml`
- **Pipeline**:
  - Ejecutar tests en cada push
  - Verificar cobertura
  - Linting y formateo
  - Build de Docker images

### Resultado de Fase 25
✓ Cobertura de tests > 70%
✓ Tests automáticos en CI/CD
✓ Flujos críticos testeados
✓ Seguridad verificada
✓ Economía validada
✓ Confianza en el código

---

## FASE 26: Documentación Completa (Días 186-192)

### Objetivo
Documentación técnica y operativa

### Componentes a Implementar

#### 26.1 README Completo
- **Crear**: Documentación principal
- **Referencia**: Sección 10 - Documentación Técnica
- **Archivo**: `README.md`
- **Contenido**:
  - Descripción del proyecto
  - Arquitectura general
  - Setup de desarrollo
  - Deployment
  - Contribución

#### 26.2 Documentación de API
- **Crear**: Guía de API
- **Archivo**: `docs/api_reference.md`
- **Contenido**:
  - Autenticación
  - Endpoints disponibles
  - Request/Response examples
  - Error codes
  - Rate limits

#### 26.3 Guía de Arquitectura
- **Crear**: Documentación técnica
- **Archivo**: `docs/architecture.md`
- **Contenido**:
  - Diagrama de componentes
  - Flujo de datos
  - Event Bus
  - Base de datos
  - Escalabilidad

#### 26.4 Guía de Deployment
- **Crear**: Manual de despliegue
- **Archivo**: `docs/deployment.md`
- **Contenido**:
  - Requisitos de infraestructura
  - Configuración de servidores
  - Variables de entorno
  - Backup y restore
  - Monitoring

#### 26.5 Runbooks Operacionales
- **Crear**: Guías de operación
- **Archivos**:
  - `docs/runbooks/emergency_response.md`
  - `docs/runbooks/database_maintenance.md`
  - `docs/runbooks/scaling.md`
- **Contenido**:
  - Procedimientos comunes
  - Troubleshooting
  - Respuesta a incidentes

#### 26.6 Guía de Usuario Admin
- **Crear**: Manual de dashboard
- **Archivo**: `docs/admin_guide.md`
- **Contenido**:
  - Cómo crear contenido
  - Cómo usar asistentes
  - Gestión de usuarios
  - Interpretación de métricas
  - Mejores prácticas

#### 26.7 Docstrings y Comentarios
- **Completar**: Documentación en código
- **Funcionalidad**:
  - Todas las funciones con docstrings
  - Comentarios en lógica compleja
  - Type hints en Python
  - JSDoc en JavaScript

### Resultado de Fase 26
✓ Documentación completa
✓ API documentada
✓ Arquitectura clara
✓ Guías operacionales
✓ Manual de administrador
✓ Código autodocumentado

---

## FASE 27: Preparación de Producción (Días 193-199)

### Objetivo
Preparar sistema para lanzamiento

### Componentes a Implementar

#### 27.1 Configuración de Producción
- **Crear**: Configs de producción
- **Archivos**:
  - `config/production.py`
  - `.env.production.example`
- **Configuración**:
  - Variables de entorno
  - Secrets management
  - Logging levels
  - Debug mode OFF

#### 27.2 SSL/TLS
- **Configurar**: Certificados
- **Archivos**:
  - `docker/nginx.conf` (actualizar)
- **Funcionalidad**:
  - Certificado SSL válido
  - HTTPS obligatorio
  - Headers de seguridad

#### 27.3 Backups Automáticos
- **Configurar**: Sistema de backups
- **Referencia**: Sección 13.1 - Riesgos Técnicos
- **Archivos**:
  - `scripts/backup.sh`
  - Cron jobs configurados
- **Funcionalidad**:
  - Backup diario de PostgreSQL
  - Backup diario de MongoDB
  - Backup semanal completo
  - Retención de 30 días
  - Tests de restore

#### 27.4 Monitoring en Producción
- **Configurar**: Prometheus + Grafana
- **Referencia**: Sección 8.2 - Monitoreo y Alertas
- **Archivos**:
  - `docker/docker-compose.prod.yml`
  - `monitoring/prometheus.yml`
  - `monitoring/grafana_dashboards/`
- **Dashboards**:
  - System metrics
  - Application metrics
  - Business metrics
  - Error rates

#### 27.5 Alertas
- **Configurar**: Sistema de alertas
- **Funcionalidad**:
  - Alerta si error rate > 1%
  - Alerta si response time > 2s
  - Alerta si downtime > 1min
  - Alerta si disco > 85%
  - Notificaciones vía email/Telegram

#### 27.6 Log Aggregation
- **Configurar**: Logs centralizados
- **Archivos**:
  - `docker/docker-compose.prod.yml` (añadir ELK stack opcional)
- **Funcionalidad**:
  - Todos los logs en un lugar
  - Búsqueda y filtrado
  - Retención de 90 días

#### 27.7 Secrets Management
- **Configurar**: Gestión de secrets
- **Referencia**: Sección 8.1 - Seguridad
- **Opciones**:
  - AWS Secrets Manager
  - HashiCorp Vault
  - O variables de entorno seguras
- **Secrets**:
  - Bot token
  - Database passwords
  - API keys
  - Payment provider tokens

#### 27.8 Disaster Recovery Plan
- **Documentar**: Plan de recuperación
- **Referencia**: Sección 13.1 - Riesgos Técnicos
- **Archivo**: `docs/disaster_recovery.md`
- **Contenido**:
  - Procedimiento de restore de DB
  - Failover de servicios
  - RTO y RPO definidos
  - Contactos de emergencia
  - Checklist de verificación post-restore

### Resultado de Fase 27
✓ Configuración de producción completa
✓ SSL/TLS configurado
✓ Backups automáticos funcionando
✓ Monitoring y alertas activos
✓ Secrets gestionados de forma segura
✓ Plan de disaster recovery documentado
✓ Sistema listo para producción

---

## FASE 28: Launch y Post-Launch (Días 200-210)

### Objetivo
Lanzamiento controlado y estabilización

### Componentes a Implementar

#### 28.1 Checklist Pre-Launch
- **Verificar**: Todos los ítems
- **Referencia**: Apéndice D - Checklist Pre-Launch
- **Proceso**:
  - Revisar cada ítem del checklist
  - Resolver blockers críticos
  - Documentar conocidos no-críticos
  - Aprobar go/no-go

#### 28.2 Beta Cerrada
- **Ejecutar**: Lanzamiento beta
- **Referencia**: Sección 11.1 - Plan de Implementación
- **Proceso**:
  - Invitar 20-50 usuarios beta
  - Monitorear métricas intensivamente
  - Recolectar feedback activamente
  - Iterar rápido en bugs críticos
  - Duración: 7 días

#### 28.3 Soft Launch
- **Ejecutar**: Lanzamiento limitado
- **Proceso**:
  - Abrir a 100-200 usuarios
  - Anunciar en comunidades relevantes
  - Limitar registros diarios
  - Monitorear estabilidad
  - Duración: 7-10 días

#### 28.4 Monitoreo Intensivo
- **Ejecutar**: Vigilancia 24/7
- **Referencia**: Sección 12.2 - Métricas Técnicas
- **Funcionalidad**:
  - Dashboard de métricas en pantalla
  - Revisión de logs cada 2-4 horas
  - Respuesta rápida a alertas
  - Comunicación constante de equipo

#### 28.5 Hotfixes Rápidos
- **Proceso**: Pipeline acelerado
- **Funcionalidad**:
  - Branch de hotfix
  - Testing mínimo pero crítico
  - Deploy rápido a producción
  - Comunicación a usuarios si aplica

#### 28.6 Recolección de Feedback
- **Crear**: Canales de feedback
- **Implementar**:
  - Comando `/feedback` en bot
  - Form en dashboard
  - Canal de Discord/Telegram para usuarios
  - Encuestas periódicas

#### 28.7 Análisis de Métricas
- **Ejecutar**: Review diario
- **Referencia**: Sección 12 - Métricas de Éxito y KPIs
- **Métricas Clave**:
  - DAU y retención D1/D7
  - Fragmentos completados
  - Besitos ganados/gastados
  - Conversión a VIP
  - Errores y crashes
  - Response times

#### 28.8 Iteración Basada en Datos
- **Proceso**: Mejora continua
- **Ciclo**:
  1. Identificar problema en métricas
  2. Formular hipótesis
  3. Implementar solución
  4. Medir impacto
  5. Iterar

#### 28.9 Launch Público
- **Ejecutar**: Lanzamiento completo
- **Proceso**:
  - Remover límites de registro
  - Anuncio oficial en redes sociales
  - Press release (si aplica)
  - Promoción en comunidades
  - Monitorear estabilidad con carga real

#### 28.10 Post-Launch Support
- **Establecer**: Soporte continuo
- **Funcionalidad**:
  - Horarios de soporte definidos
  - Sistema de tickets
  - FAQs actualizadas
  - Comunicación proactiva de issues conocidos

### Resultado de Fase 28
✓ Beta exitosa con usuarios reales
✓ Soft launch estable
✓ Métricas monitoreadas
✓ Feedback recolectado
✓ Hotfixes aplicados
✓ Launch público completado
✓ Sistema funcionando en producción

---

## Post-Launch: Mantenimiento y Evolución

### Actividades Continuas

#### Mantenimiento Regular
- **Semanal**:
  - Review de métricas
  - Análisis de feedback
  - Planning de mejoras
  - Actualización de contenido narrativo
  
- **Mensual**:
  - Review de performance
  - Análisis de churn
  - Optimizaciones de DB
  - Actualización de dependencias

#### Creación de Contenido
- **Continuo**:
  - Nuevos fragmentos narrativos
  - Nuevas misiones
  - Nuevos items
  - Eventos temporales

#### Mejoras Incrementales
- **Basado en Feedback**:
  - Features solicitadas por usuarios
  - Mejoras de UX
  - Optimizaciones
  - Corrección de bugs menores

#### Expansión Futura
- **Referencia**: Sección 14 - Roadmap Post-Launch
- **Fases 2 y 3**:
  - Funcionalidades sociales avanzadas
  - Contenido expandido (niveles 7-9)
  - Personalización
  - Multiplataforma

---

## Resumen de Dependencias entre Fases

```
FASE 0: Preparación
    ↓
FASE 1: Bot Básico + Usuarios ← base para todo
    ↓
FASE 2: Event Bus ← necesario para comunicación entre módulos
    ↓
FASE 3: Besitos ← economía base
    ↓
FASE 4: Inventario ← requiere usuarios y besitos
    ↓
FASE 5: Tienda ← requiere inventario y besitos
    ↓
FASE 6: Narrativa Core ← independiente pero integra con besitos
    ↓
FASE 7: Desbloqueos ← requiere narrativa + besitos + inventario
    ↓
FASE 8: Misiones ← requiere event bus + besitos
    ↓
FASE 9: Achievements ← requiere event bus + besitos
    ↓
FASE 10: Narrativa Ramificada ← expande fase 6
    ↓
FASE 11: VIP ← independiente
    ↓
FASE 12: Canales ← requiere VIP
    ↓
FASE 13: Publicación ← requiere canales
    ↓
FASE 14: Reacciones ← requiere publicación + besitos
    ↓
FASE 15: Trivias ← requiere besitos + event bus
    ↓
FASE 16: Config Manager ← requiere todos los módulos funcionales
    ↓
FASE 17: API REST ← requiere config manager
    ↓
FASE 18: Dashboard ← requiere API
    ↓
FASE 19: Subastas ← requiere inventario + besitos
    ↓
FASE 20: Pagos ← requiere VIP
    ↓
FASE 21: Secretos ← requiere narrativa completa
    ↓
FASE 22: Editor Visual ← requiere API + dashboard
    ↓
FASE 23: Asistentes ← requiere config manager + dashboard
    ↓
FASE 24-28: Optimización, Testing, Docs, Producción, Launch
```

---

## Puntos Críticos de Validación

### Después de Fase 6 (Narrativa Core)
**Validar**: ¿La narrativa engancha?
- Testear con 10-15 usuarios
- Medir completion rate de primer nivel
- Si < 50% completan, iterar en contenido antes de continuar

### Después de Fase 11 (VIP)
**Validar**: ¿La diferenciación VIP es clara?
- Testear con usuarios beta
- Verificar que entienden beneficios VIP
- Ajustar messaging si hay confusión

### Después de Fase 16 (Config Manager)
**Validar**: ¿El sistema unificado funciona?
- Crear experiencia completa usando config manager
- Verificar propagación correcta
- Asegurar que ahorra tiempo vs configuración manual

### Después de Fase 20 (Pagos)
**Validar**: ¿Los pagos funcionan correctamente?
- Testing exhaustivo de flujos de pago
- Verificar con transacciones reales pequeñas
- Probar refunds
- Solo proceder a launch después de validar pagos

---

## Estimación Total

### Tiempo Total: ~210 días (7 meses)

**Desglose**:
- Fases 0-10 (Fundamentos + Narrativa): ~56 días (2 meses)
- Fases 11-15 (VIP + Canales + Gamificación Avanzada): ~56 días (2 meses)
- Fases 16-23 (Config + Admin + Tools): ~70 días (2.3 meses)
- Fases 24-28 (Optimización + Launch): ~28 días (1 mes)

**Equipo Recomendado**:
- 2 Developers Full-stack (backend + bot + frontend)
- 1 Content Creator (narrativa)
- 1 Designer (UI/UX del dashboard)
- 1 QA/Testing (part-time en fases finales)

**Con Equipo de 2 Developers**:
- Estimación más realista: 9-10 meses
- Priorizar MVP en primeros 4-5 meses
- Iterar resto basado en feedback

---

## Recomendaciones Finales para la Ejecución

### 1. Comenzar con MVP
No es necesario implementar todas las fases para lanzar. Un MVP viable incluye:
- Fases 0-7: Bot básico, besitos, inventario, narrativa con desbloqueos
- Fase 11: VIP básico
- Fase 20: Pagos
- **Lanzar en ~3 meses con este scope**

### 2. Iterar Basado en Uso Real
Después del MVP, priorizar fases según feedback:
- Si usuarios piden más contenido → Fases 10, 21
- Si admins necesitan herramientas → Fases 16-18, 22-23
- Si escalabilidad es problema → Fase 24

### 3. Testing en Paralelo
No esperar a Fase 25 para testear:
- Escribir tests desde Fase 1
- Cobertura incremental
- CI/CD desde temprano

### 4. Documentar Mientras se Desarrolla
No dejar documentación para el final:
- Docstrings en tiempo real
- README actualizado continuamente
- Diagramas cuando la arquitectura cambia

### 5. Monitorear desde Día 1
Implementar logging y métricas básicas desde Fase 1:
- Añadir Prometheus desde el inicio
- Dashboards básicos temprano
- Expandir métricas gradualmente

---

## Referencias Rápidas al Documento de Investigación

Para cada fase, consultar las siguientes secciones del documento de investigación:

- **Arquitectura General**: Sección 1
- **Tecnologías**: Sección 2
- **Narrativa**: Sección 3
- **Gamificación**: Sección 4
- **Administración**: Sección 5
- **Configuración Unificada**: Sección 6
- **Integración**: Sección 7
- **Seguridad y Escalabilidad**: Sección 8
- **Monetización**: Sección 9
- **Documentación Técnica**: Sección 10
- **Plan de Implementación**: Sección 11
- **Métricas**: Sección 12
- **Riesgos**: Sección 13
- **Roadmap Post-Launch**: Sección 14
- **Apéndices**: Ejemplos de código, plantillas, schemas

---

**Fin de la Hoja de Ruta de Implementación Gradual** 
