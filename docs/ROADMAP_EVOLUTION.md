# DianaBot - Roadmap de Implementación
## Guía de Referencia Rápida al Documento de Investigación

---

## ESTRUCTURA DEL DOCUMENTO DE INVESTIGACIÓN

```
1. RESUMEN EJECUTIVO
2. ANÁLISIS MODULAR DETALLADO (6 sistemas)
3. ARQUITECTURA DE INTEGRACIÓN
4. EVOLUCIÓN DE DATA MODEL
5. PLAN DE IMPLEMENTACIÓN
6. CONSIDERACIONES TÉCNICAS
7. RIESGOS Y MITIGACIONES
8. CONCLUSIONES Y RECOMENDACIONES
```

---

## ROADMAP EJECUTIVO

### FASE 0: PRE-INICIO (Semana 0)
**Duración:** 1 semana  
**Objetivo:** Preparación del proyecto

#### Tareas
1. **Revisión y Aprobación**
   - Aprobar roadmap completo
   - Confirmar presupuesto
   - Asegurar equipo (ver **Sección 8.3 - Recomendación 4** para composición)

2. **Setup de Infraestructura**
   - Configurar ambientes (dev, staging, prod)
   - Setup CI/CD pipeline
   - Crear repositorio de documentación

3. **Planificación Detallada**
   - Crear backlog Sprint 1
   - Definir contratos de APIs (ver **Sección 3.3**)
   - Establecer métricas de éxito (ver **Sección 8.3 - Recomendación 5**)

#### Referencias Clave
- **Sección 8.5:** Próximos pasos inmediatos
- **Sección 5.3:** Composición de equipo requerido

---

## FASE 1: FUNDAMENTOS (Semanas 1-4)

### SPRINT 1: CoordinadorCentral Base (Semanas 1-2)

#### Objetivos
- Crear sistema de coordinación central operativo
- Implementar transacciones distribuidas
- Habilitar 2 operaciones básicas

#### Componentes a Implementar
1. **CoordinadorCentral**
   - **Referencia:** Sección 3.1 (Event Bus vs CoordinadorCentral)
   - **Especificación completa:** Código ejemplo en Sección 3.1
   - **Operaciones requeridas:** `TOMAR_DECISION`, `ACCEDER_NARRATIVA_VIP`

2. **TransactionManager**
   - **Referencia:** Sección 3.1 (componente adicional)
   - **Funcionalidad:** Gestión de transacciones distribuidas con rollback

3. **Extensión del Event Bus**
   - **Estado actual:** Sección 3.1 (Event Bus actual)
   - **Capacidades nuevas:** Orquestación, priorización de eventos

#### Nuevos Eventos Requeridos
- **Referencia completa:** Sección 3.2 (Nuevos Tipos de Eventos)
- **Eventos prioritarios Sprint 1:**
  - `coordinator.decision_taken`
  - `coordinator.access_denied`
  - `narrative.fragment_visited`
  - `narrative.decision_taken`

#### Entregables
- [ ] `core/coordinator.py` funcional
- [ ] `core/transaction_manager.py` implementado
- [ ] Tests unitarios >70% cobertura
- [ ] Documentación de APIs internas (ver **Sección 3.3**)

#### Dependencias
- Ninguna (puede iniciarse inmediatamente)

---

### SPRINT 2: Extensiones Data Model Fase 1 (Semanas 3-4)

#### Objetivos
- Extender modelos existentes sin romper funcionalidad
- Preparar base de datos para integraciones
- Migrar datos existentes

#### Modelos a Extender
1. **User Model**
   - **Referencia:** Sección 4.1 (Extensiones a Modelos Existentes)
   - **Campos nuevos:** archetipos, conversion_score, lifetime_value, etc.

2. **NarrativeFragment Model**
   - **Referencia:** Sección 4.1
   - **Campos nuevos:** experience_id, composite_requirements, extended_rewards, métricas

3. **Mission Model**
   - **Referencia:** Sección 4.1
   - **Campos nuevos:** experience_id, composite_requirements

4. **Item Model**
   - **Referencia:** Sección 4.1
   - **Campos nuevos:** is_purchasable, shop_item_id, unlocks_content

#### Estrategia de Migración
- **Referencia completa:** Sección 4.3 (Migraciones de Datos Requeridas)
- **Estrategia:** Fase 1 - Extensiones sin romper funcionalidad existente
- **Script ejemplo:** Ver Sección 4.3

#### Índices Críticos
- **Referencia:** Sección 6.1.3 (Optimización de Queries)
- **Índices a crear:** Todos los índices listados para User, NarrativeFragment, Mission

#### Entregables
- [ ] Migraciones creadas y probadas
- [ ] Datos legacy migrados sin pérdida
- [ ] Índices optimizados creados
- [ ] Tests de integridad de datos
- [ ] Documentación de cambios en schema

#### Dependencias
- Puede ejecutarse en paralelo con Sprint 1

#### Riesgos
- **Referencia:** Sección 7.1 - Riesgo 3 (Consistencia de Datos)
- **Mitigación:** PostgreSQL como Source of Truth

---

## FASE 2: REACCIONES Y ANALYTICS BÁSICO (Semanas 5-6)

### SPRINT 3: Sistema de Reacciones (Semana 5-6)

#### Objetivos
- Implementar sistema completo de reacciones
- Integrar con besitos para recompensas
- Habilitar tracking de engagement

#### Análisis de Brecha
- **Referencia:** Sección 2.2 - BRECHA CRÍTICA 1 (Ausencia de Sistema de Reacciones)

#### Componentes a Crear
1. **Módulo de Reacciones**
   - **Ubicación:** `modules/gamification/reactions.py`
   - **Especificación:** Sección 2.2 - BRECHA CRÍTICA 1
   - **Clase principal:** `ReactionProcessor`

2. **Modelos de Base de Datos**
   - **Referencia:** Sección 4.2 (Módulo de Reacciones)
   - **Modelos:** `ContentReaction`, `ReactionRewardConfig`

3. **Integración con CoordinadorCentral**
   - **Operación:** `REACCIONAR_CONTENIDO`
   - **Referencia:** Sección 3.1 (código completo de la operación)

#### Integraciones Requeridas
- Con `modules/narrative` para reacciones en fragmentos
- Con `modules/admin` para reacciones en posts de canales
- Con `besitos.py` para otorgar recompensas
- Con Event Bus para emitir eventos

#### Configuración Inicial
- **Recompensas por reacción:**
  - ❤️ (love): 10 besitos
  - 🔥 (fire): 15 besitos
  - ⭐ (star): 20 besitos
  - 👍 (like): 5 besitos

#### Entregables
- [ ] `modules/gamification/reactions.py` implementado
- [ ] Modelos de BD creados y migrados
- [ ] Handlers de Telegram configurados
- [ ] Integración con CoordinadorCentral completa
- [ ] Tests de integración

#### Dependencias
- Requiere CoordinadorCentral (Sprint 1)
- Requiere extensiones de User model (Sprint 2)

---

### SPRINT 3.5: Analytics Básico (Semana 6)

#### Objetivos
- Habilitar tracking automático de eventos
- Crear queries básicas de métricas
- Dashboard simple

#### Análisis de Brecha
- **Referencia:** Sección 2.6 - BRECHA CRÍTICA 1 (Analytics Unificado)

#### Componentes a Crear
1. **Event Collector**
   - **Ubicación:** `modules/analytics/collector.py`
   - **Referencia:** Sección 2.6 (especificación de componentes)

2. **Event Subscriber**
   - **Ubicación:** `modules/analytics/event_subscriber.py`
   - **Referencia:** Sección 2.6 - BRECHA 2 (integración con Event Bus)

3. **Modelos de Base de Datos**
   - **Referencia:** Sección 4.2 (Módulo de Analytics)
   - **Modelos:** `AnalyticsEvent`, `DailyMetrics`, `UserSessionMetrics`

#### Optimización de Performance
- **Referencia:** Sección 6.1.1 - Punto 3 (Tracking de Analytics)
- **Estrategia:** Batch inserts, buffer en memoria
- **Implementación:** EventCollectorBuffer (ver código en Sección 6.1.1)

#### Eventos a Trackear (Prioritarios)
- **Lista completa:** Sección 3.2
- **Prioritarios Sprint 3.5:**
  - Todos los eventos de narrativa
  - Todos los eventos de gamificación
  - `analytics.vip_content_accessed`

#### Entregables
- [ ] `modules/analytics/collector.py` implementado
- [ ] Suscripción automática a Event Bus
- [ ] Modelos de BD con particionamiento (ver Sección 6.1.3)
- [ ] Queries básicas de métricas funcionando
- [ ] Buffer de eventos implementado

#### Dependencias
- Requiere Event Bus extendido (Sprint 1)
- Requiere eventos nuevos implementados

---

## FASE 3: MÓDULO DE COMERCIO (Semanas 7-10)

### SPRINT 4: Tienda y Catálogo (Semanas 7-8)

#### Objetivos
- Crear sistema completo de tienda
- Habilitar navegación y búsqueda de productos
- UI de tienda en Telegram

#### Análisis de Brecha
- **Referencia:** Sección 2.3 - Estado Actual (NO EXISTE módulo)
- **Brecha:** BRECHA CRÍTICA 1 - Ausencia Total del Módulo de Comercio

#### Estructura del Módulo
- **Referencia completa:** Sección 2.3 - estructura de carpetas
```
modules/commerce/
├── shop.py
├── cart.py
├── checkout.py
├── payments.py
├── unlocks.py
├── upselling.py
└── subscriptions.py
```

#### Componentes Sprint 4
1. **shop.py**
   - **Especificación:** Sección 2.3 (ShopManager)
   - **Funciones:** `get_catalog()`, `get_item_details()`

2. **Modelos de Base de Datos**
   - **Referencia:** Sección 4.2 (Módulo de Comercio)
   - **Modelos Sprint 4:**
     - `ShopItem` (tabla completa)
     - `UserPurchase` (estructura base)

3. **UI de Telegram**
   - Menú de tienda con categorías
   - Vista de detalle de items
   - Filtros (tipo, precio, rareza)

#### Catálogo Inicial
- Crear 10-15 items de prueba
- Variar tipos: narrative_unlock, experience_unlock, power_up
- Variar raridades: common, rare, epic, legendary
- Precios: 100-5000 besitos

#### Entregables
- [ ] `modules/commerce/shop.py` implementado
- [ ] Modelos ShopItem y UserPurchase creados
- [ ] Catálogo inicial poblado
- [ ] UI de tienda funcional en Telegram
- [ ] Sistema de filtros y búsqueda

#### Dependencias
- Requiere User model extendido (Sprint 2)
- Requiere Item model extendido (Sprint 2)

---

### SPRINT 5: Sistema de Pagos (Semana 9)

#### Objetivos
- Integrar Telegram Payments
- Implementar compras con besitos
- Crear flujo de checkout completo

#### Componentes a Implementar
1. **payments.py**
   - **Especificación:** Sección 2.3 - BRECHA CRÍTICA 2
   - **Funcionalidades:**
     - Manejo de `PreCheckoutQuery`
     - Procesamiento de `SuccessfulPayment`
     - Sistema de refunds

2. **checkout.py**
   - **Especificación:** Sección 2.3 (CheckoutProcessor)
   - **Funciones:** `process_purchase()`, `process_vip_subscription()`

#### Validación de Seguridad
- **Referencia:** Sección 6.2.1 - Punto 2 (Validación de Compras)
- **Implementar:** `PurchaseSecurityValidator`
- **Validaciones:**
  - Item disponible
  - No duplicar compras únicas
  - Verificar requisitos
  - Rate limiting

#### Métodos de Pago
1. **Besitos (interno)**
   - Validar balance suficiente
   - Transacción atómica con CoordinadorCentral

2. **Telegram Payments (dinero real)**
   - Integración con provider
   - Manejo de webhooks
   - Confirmaciones

#### Entregables
- [ ] `modules/commerce/payments.py` implementado
- [ ] `modules/commerce/checkout.py` implementado
- [ ] Integración con Telegram Payments funcional
- [ ] Compras con besitos funcionando
- [ ] Sistema de validación de seguridad
- [ ] Tests de flujos de compra

#### Dependencias
- Requiere shop.py (Sprint 4)
- Requiere CoordinadorCentral (Sprint 1)
- Requiere sistema de besitos funcional

#### Riesgos
- **Referencia:** Sección 7.1 - Riesgo 2 (Performance de Transacciones)
- **Mitigación:** Procesamiento asíncrono de operaciones no críticas

---

### SPRINT 6: Desbloqueos y Arquetipos (Semana 10)

#### Objetivos
- Implementar desbloqueos automáticos post-compra
- Crear sistema de arquetipos de usuario
- Habilitar ofertas personalizadas

#### Componentes a Implementar
1. **unlocks.py**
   - **Especificación:** Sección 2.3 (PurchaseUnlockEngine)
   - **Funciones:** `apply_unlocks()`, `check_purchase_requirements()`

2. **archetypes.py**
   - **Especificación:** Sección 2.3 - BRECHA CRÍTICA 3
   - **Clase:** `ArchetypeEngine`
   - **Arquetipos:** NARRATIVE_LOVER, COLLECTOR, COMPETITIVE, SOCIAL, COMPLETIONIST

3. **upselling.py**
   - **Especificación:** Sección 2.3 (UpsellEngine)
   - **Funciones:** `get_contextual_offers()`, `trigger_conversion_flow()`

4. **Modelos de Base de Datos**
   - **Referencia:** Sección 4.2 (Módulo de Comercio)
   - **Modelos Sprint 6:**
     - `UserArchetype`
     - `PersonalizedOffer`

#### Lógica de Desbloqueos
- Desbloquear fragmentos narrativos
- Activar experiencias exclusivas
- Otorgar acceso a canales especiales
- Desbloquear misiones premium

#### Detección de Arquetipos
- **Basado en:**
  - Patrones de consumo de contenido
  - Frecuencia de interacciones
  - Tipos de compras realizadas
  - Decisiones narrativas tomadas

#### Integración con CoordinadorCentral
- **Operación:** `COMPRAR_ITEM` completa
- **Referencia:** Sección 3.1 (código completo)
- **Flujo:** Compra → Inventory → Unlocks → Archetipos → Upsell

#### Entregables
- [ ] `modules/commerce/unlocks.py` implementado
- [ ] `modules/commerce/archetypes.py` implementado
- [ ] `modules/commerce/upselling.py` implementado
- [ ] Modelos UserArchetype y PersonalizedOffer
- [ ] Integración completa con COMPRAR_ITEM
- [ ] Tests de desbloqueos automáticos

#### Dependencias
- Requiere checkout.py (Sprint 5)
- Requiere analytics básico (Sprint 3.5) para detección de arquetipos
- Requiere extensiones de NarrativeFragment (Sprint 2)

#### Riesgos
- **Referencia:** Sección 7.2 - Riesgo 6 (Balance Económico)
- **Mitigación:** Simulación económica (ver código en Sección 7.2)

---

## FASE 4: MÓDULO DE EXPERIENCIAS UNIFICADAS (Semanas 11-14)

### SPRINT 7: Core de Experiencias (Semanas 11-12)

#### Objetivos
- Crear sistema completo de experiencias
- Implementar motor de progreso
- Habilitar validación de requisitos compuestos

#### Análisis de Brecha
- **Referencia:** Sección 2.5 - Estado Actual (NO EXISTE)
- **Importancia:** BRECHA CRÍTICA - Módulo central a la arquitectura

#### Concepto de Experiencia
- **Referencia:** Sección 2.5 - Concepto de Experiencia
- Un flujo unificado que integra múltiples elementos de diferentes sistemas

#### Estructura del Módulo
- **Referencia completa:** Sección 2.5
```
modules/experiences/
├── engine.py
├── builder.py
├── propagation.py
├── validator.py
├── coordinator.py
└── templates.py
```

#### Modelos de Base de Datos
- **Referencia completa:** Sección 4.2 (Módulo de Experiencias)
- **Modelos Sprint 7:**
  - `Experience`
  - `ExperienceComponent`
  - `UserExperienceProgress`
  - `UserComponentCompletion`
  - `ExperienceRequirement`
  - `ExperienceReward`

#### Componentes Sprint 7
1. **engine.py**
   - **Especificación:** Sección 2.5 (ExperienceEngine)
   - **Funciones clave:**
     - `start_experience()`
     - `progress_experience()`
     - `complete_experience()`
     - `get_experience_status()`

2. **validator.py**
   - **Especificación:** Sección 2.5 (CompositeValidator)
   - **Funcionalidad:** Validar requisitos de múltiples sistemas
   - **Tipos de requisitos:** level, vip_membership, item, achievement, experience_completed

#### Sistema de Requisitos Compuestos
- **Referencia teórica:** Sección 2.1 - BRECHA CRÍTICA 1 (Sistema de Requisitos Compuestos)
- **Implementación:** `validator.py` valida contra todos los módulos
- **Integración:** Usa APIs internas (ver Sección 3.3)

#### Entregables
- [ ] Todos los modelos de experiencias creados y migrados
- [ ] `modules/experiences/engine.py` implementado
- [ ] `modules/experiences/validator.py` implementado
- [ ] Sistema de requisitos compuestos funcional
- [ ] Tests unitarios de motor de experiencias

#### Dependencias
- Requiere TODOS los módulos previos operativos
- Requiere APIs internas definidas (Sección 3.3)
- Requiere CoordinadorCentral completo

---

### SPRINT 8: Builder y Propagación (Semana 13)

#### Objetivos
- Crear herramientas para construir experiencias
- Implementar propagación automática de componentes
- Templates predefinidos para experiencias comunes

#### Componentes a Implementar
1. **builder.py**
   - **Especificación:** Sección 2.5 (ExperienceBuilder)
   - **Funciones:**
     - `create_experience()`
     - `add_component()`
     - `from_template()`

2. **propagation.py**
   - **Especificación:** Sección 2.5 (PropagationEngine)
   - **Funcionalidad:** Crear automáticamente componentes en otros sistemas
   - **Ejemplo:** Crear fragmentos narrativos + misiones + items vinculados

3. **templates.py**
   - **Especificación:** Sección 2.5 (ExperienceTemplates)
   - **Templates:** NARRATIVE_JOURNEY, MISSION_CHAIN, HYBRID

#### Sistema de Propagación Automática
**Flujo:**
1. Admin crea experiencia con template
2. System genera componentes automáticamente:
   - Fragmentos narrativos → tabla `narrative_fragments`
   - Misiones → tabla `missions`
   - Items de recompensa → tabla `items`
3. Vincula todo a la experiencia central

#### UI de Administración
- Panel para crear experiencias
- Editor visual de componentes
- Preview de flujo de experiencia
- Configuración de requisitos y recompensas

#### Experiencias Iniciales
Crear 3-5 experiencias de ejemplo:
1. **"El Primer Beso"** (NARRATIVE_JOURNEY)
   - 5 fragmentos narrativos
   - 3 decisiones clave
   - 1 logro al completar

2. **"Cazador de Secretos"** (MISSION_CHAIN)
   - 3 misiones secuenciales
   - Requiere comprar 1 item
   - Desbloquea contenido especial

3. **"Camino VIP"** (HYBRID)
   - Mezcla narrativa + misiones
   - Requiere membresía VIP
   - Recompensas exclusivas

#### Entregables
- [ ] `modules/experiences/builder.py` implementado
- [ ] `modules/experiences/propagation.py` implementado
- [ ] `modules/experiences/templates.py` implementado
- [ ] UI de administración funcional
- [ ] 3-5 experiencias de ejemplo creadas
- [ ] Documentación de creación de experiencias

#### Dependencias
- Requiere engine.py (Sprint 7)
- Requiere todos los módulos de contenido (narrativa, gamificación, comercio)

---

### SPRINT 9: Integración Profunda (Semana 14)

#### Objetivos
- Integrar experiencias con todos los módulos
- Crear flujos de usuario end-to-end
- Validar funcionamiento completo del sistema

#### Integraciones Requeridas
**Referencia completa:** Sección 2.5 - Integraciones Requeridas

1. **Con Narrativa**
   - Fragmentos como componentes de experiencias
   - Progreso narrativo actualiza experiencia
   - Desbloqueos narrativos como recompensas

2. **Con Gamificación**
   - Misiones como componentes
   - Logros otorgados al completar
   - Besitos como recompensas

3. **Con Comercio**
   - Items como requisitos
   - Experiencias exclusivas para compradores
   - Descuentos al completar

4. **Con Administración**
   - Experiencias VIP exclusivas
   - Contenido publicado en canales
   - Acceso a canales como recompensa

#### Actualización del CoordinadorCentral
- Extender operaciones existentes para considerar experiencias
- Agregar lógica de progreso de experiencias en:
  - `TOMAR_DECISION`
  - `COMPRAR_ITEM`
  - `REACCIONAR_CONTENIDO`

#### Flujos End-to-End a Validar
1. Usuario inicia experiencia → completa todos los componentes → recibe recompensas
2. Usuario intenta iniciar experiencia sin requisitos → ve qué le falta → completa requisitos → inicia
3. Usuario abandona experiencia a mitad → puede retomar después
4. Usuario completa experiencia → desbloquea siguiente experiencia

#### Tests de Integración
- **Referencia:** Sección 6.3.1 (Tests de Integración)
- **Ejemplo:** `test_complete_experience_flow` (ver código en Sección 6.3.1)

#### Entregables
- [ ] Todas las integraciones implementadas
- [ ] CoordinadorCentral actualizado
- [ ] Flujos end-to-end funcionando
- [ ] Tests de integración completos (>30 test cases)
- [ ] Documentación de flujos de usuario

#### Dependencias
- Requiere builder y propagation (Sprint 8)
- Requiere TODOS los módulos previos estables

#### Riesgos
- **Referencia:** Sección 7.2 - Riesgo 7 (Baja Adopción de Experiencias)
- **Mitigación:** MVP con experiencias bien diseñadas y promoción in-app

---

## FASE 5: INTEGRACIONES PROFUNDAS (Semanas 15-16)

### SPRINT 10: Operaciones Avanzadas del Coordinador (Semana 15)

#### Objetivos
- Completar todas las operaciones del CoordinadorCentral
- Sistema de rollback robusto
- Optimización de performance

#### Operaciones a Completar
**Referencia:** Sección 3.1 (CoordinadorCentral)

1. **`REACCIONAR_CONTENIDO`** (completar)
   - **Especificación completa:** Código en Sección 3.1
   - **Integraciones:** reacciones → besitos → logros → misiones → analytics

2. **`COMPRAR_ITEM`** (extender)
   - **Ya implementado en Sprint 6**
   - **Extender con:** Experiencias, actualizaciones de arquetipos completas

3. **Operaciones adicionales** (si requeridas)
   - Definir según necesidades identificadas en testing

#### Sistema de Rollback Robusto
- **Referencia:** Sección 3.1 (TransactionManager)
- **Mejorar:**
  - Logging detallado de cada paso
  - Retry automático en fallos transitorios
  - Alertas a admins en rollbacks

#### Priorización de Eventos
- Eventos críticos (compras, VIP) → alta prioridad
- Eventos de tracking → baja prioridad
- Queue management para evitar overflow

#### Optimización de Performance
- **Referencia:** Sección 6.1.1 (Puntos Críticos de Performance)
- **Implementar:**
  - Caching de validaciones (ver Sección 6.1.1 - Punto 1)
  - Procesamiento asíncrono (ver Sección 6.1.1 - Punto 2)
  - Circuit breaker pattern (ver Sección 7.1 - Riesgo 2)

#### Entregables
- [ ] 4 operaciones principales completas y optimizadas
- [ ] Sistema de rollback robusto con logging
- [ ] Circuit breakers implementados
- [ ] Performance P95 < 1 segundo
- [ ] Documentación de operaciones

#### Dependencias
- Requiere todos los módulos implementados
- Requiere experiencias integradas (Sprint 9)

---

### SPRINT 11: Flujos de Conversión y Retroalimentación (Semana 16)

#### Objetivos
- Implementar flujos de conversión free→VIP
- Sistema de ofertas contextuales completo
- Retroalimentación positiva entre sistemas

#### Análisis Conceptual
- **Referencia:** Sección del documento de arquitectura (arquitectura_sistema_dianabot.md)
  - "Sistema de Retroalimentación" - Retroalimentación Positiva
  - "Mecanismos de Conversión"

#### Componentes a Implementar/Extender
1. **Flujos de Conversión**
   - **Modelo de BD:** `ConversionFunnel` (ver Sección 4.2 - Analytics)
   - **Tracking de etapas:** entered, current, completed
   - **Triggers:** Acceso denegado a VIP, oferta contextual, etc.

2. **Sistema de Ofertas Inteligente**
   - Extender `upselling.py` (creado en Sprint 6)
   - **Contextos:**
     - Post decisión narrativa importante
     - Al completar misión
     - Después de reaccionar
     - Al ver contenido VIP bloqueado

3. **Retroalimentación Positiva**
   - Más narrativa → más puntos → más compras → más contenido
   - Más participación → más VIP → más narrativa → más engagement

#### Integración con Arquetipos
- **Referencia:** Sección 2.3 (Sistema de Arquetipos)
- Personalizar ofertas según arquetipo del usuario:
  - NARRATIVE_LOVER → Ofrecer desbloqueos narrativos
  - COLLECTOR → Ofrecer items raros
  - COMPETITIVE → Ofrecer ventajas
  - etc.

#### Modelo de Administración de Suscripciones
- **Referencia:** Sección 2.4 - BRECHA 4 (Lifecycle de Suscripción)
- **Componente:** `subscription_lifecycle.py`
- **Funciones:**
  - `handle_subscription_expiring()`
  - `handle_subscription_expired()`
  - `handle_subscription_renewed()`

#### Métricas de Conversión
- Funnel de conversión Free → Engaged → Purchaser → VIP
- Tasa de conversión por arquetipo
- Efectividad de ofertas contextuales
- ROI de cada tipo de oferta

#### Entregables
- [ ] Flujos de conversión automatizados
- [ ] Sistema de ofertas contextuales funcionando
- [ ] `modules/admin/subscription_lifecycle.py` implementado
- [ ] Tracking de conversión funnel
- [ ] Dashboard de métricas de conversión
- [ ] Tests de flujos de conversión

#### Dependencias
- Requiere arquetipos (Sprint 6)
- Requiere experiencias (Sprint 9)
- Requiere CoordinadorCentral optimizado (Sprint 10)

#### Riesgos
- **Referencia:** Sección 7.2 - Riesgo 5 (Complejidad Abruma a Usuarios)
- **Mitigación:** Onboarding gradual, UI simplificada

---

## FASE 6: ANALYTICS AVANZADO Y DASHBOARD (Semanas 17-18)

### SPRINT 12: Analytics Completo (Semana 17)

#### Objetivos
- Sistema completo de analytics operacional
- Insights automáticos
- Sistema de alertas proactivas

#### Análisis de Brecha
- **Referencia:** Sección 2.6 (Sistema de Estadísticas y Analytics)
- **Componentes faltantes:** aggregator, insights, alerts

#### Componentes a Implementar
1. **aggregator.py**
   - **Especificación:** Sección 2.6 (MetricsAggregator)
   - **Funciones:**
     - `get_engagement__metrics()`
     - `get_monetization_metrics()`
     - `get_narrative_metrics()`
     - `get_experience_metrics()`

2. **insights.py**
   - **Especificación:** Sección 2.6 (InsightEngine)
   - **Funciones:**
     - `detect_drop_off_points()`
     - `identify_high_value_users()`
     - `suggest_content_optimizations()`

3. **alerts.py**
   - **Especificación:** Sección 2.6 - BRECHA 3 (Sistema de Alertas)
   - **Funciones:**
     - `check_anomalies()`
     - `notify_admin()`
     - `get_alert_config()`

4. **reports.py**
   - **Especificación:** Sección 2.6 (estructura del módulo)
   - **Funcionalidad:** Generación de reportes exportables

5. **export.py**
   - **Funcionalidad:** Exportación en múltiples formatos (PDF, Excel, CSV)

#### Métricas Avanzadas a Implementar

**Engagement:**
- MAU (Monthly Active Users)
- DAU (Daily Active Users)
- Retention (D1, D7, D30)
- Session duration promedio
- Engagement por módulo

**Monetización:**
- Revenue total
- ARPU (Average Revenue Per User)
- ARPPU (Average Revenue Per Paying User)
- Conversión free→VIP
- LTV (Lifetime Value)

**Narrativa:**
- Fragmentos más visitados
- Tasa de completitud
- Decisiones más populares
- Puntos de abandono

**Experiencias:**
- Tasa de inicio
- Tasa de completitud
- Tiempo promedio de completitud
- Experiencias más populares

#### Sistema de Insights Automáticos

**Detección de patrones:**
- Usuarios en riesgo de churn
- High-value users potenciales
- Contenido con bajo engagement
- Oportunidades de optimización

**Recomendaciones automáticas:**
- Crear contenido del tipo X
- Ajustar precio del item Y
- Mejorar fragmento Z (bajo engagement)

#### Sistema de Alertas

**Tipos de alertas:**
- Caída en engagement (>20%)
- Spike de errores técnicos
- Caída en conversión
- Usuarios de alto valor en riesgo
- Anomalías en economía de besitos

**Canales de notificación:**
- Telegram (mensaje a admins)
- Email
- Dashboard con badge

#### Entregables
- [ ] `modules/analytics/aggregator.py` implementado
- [ ] `modules/analytics/insights.py` implementado
- [ ] `modules/analytics/alerts.py` implementado
- [ ] `modules/analytics/reports.py` implementado
- [ ] `modules/analytics/export.py` implementado
- [ ] Sistema de alertas configurado y probado
- [ ] Documentación de métricas

#### Dependencias
- Requiere analytics básico (Sprint 3.5)
- Requiere todos los módulos generando eventos
- Depende de modelos de analytics (creados en Sprint 3.5)

---

### SPRINT 13: Dashboard Administrativo (Semana 18)

#### Objetivos
- Dashboard web completo y funcional
- Visualizaciones interactivas
- Sistema de reportes para admins

#### Componentes a Implementar

1. **dashboard.py**
   - **Especificación:** Sección 2.6 (DashboardDataProvider)
   - **Funciones:**
     - `get_overview_stats()`
     - `get_funnel_data()`
     - `get_cohort_analysis()`

2. **API Endpoints para Dashboard**
   - **Referencia:** Sección 3.3 (AnalyticsAPI)
   - Endpoints REST para frontend

3. **Frontend Web**
   - Framework: React/Vue (recomendado) o template engine
   - Biblioteca de gráficos: Chart.js, Recharts, o D3.js
   - Dashboard responsive

#### Secciones del Dashboard

**1. Overview (Vista Principal)**
- KPIs principales en tiempo real:
  - Usuarios activos (hoy, semana, mes)
  - Revenue (día, semana, mes)
  - Conversión free→VIP
  - Engagement score promedio
- Gráficos de tendencias
- Alertas activas

**2. Usuarios**
- Lista de usuarios con filtros
- Segmentación por arquetipo
- Usuarios de alto valor
- Usuarios en riesgo de churn
- Detalle individual de usuario

**3. Contenido**
- Estadísticas de narrativa
- Performance de experiencias
- Items de tienda más vendidos
- Contenido con bajo engagement

**4. Monetización**
- Revenue breakdown
- Funnel de conversión
- Análisis de cohort
- Métricas de LTV

**5. Sistema**
- Health checks
- Performance metrics
- Error logs
- Uso de recursos

#### Visualizaciones Clave

- Gráfico de línea: Usuarios activos en el tiempo
- Funnel chart: Conversión free→VIP
- Heatmap: Engagement por hora del día
- Bar chart: Revenue por tipo de producto
- Pie chart: Distribución de arquetipos
- Cohort table: Retención por cohorte

#### Sistema de Reportes

**Reportes predefinidos:**
1. Reporte semanal ejecutivo
2. Reporte mensual de revenue
3. Reporte de performance de contenido
4. Reporte de experiencias

**Funcionalidad:**
- Programar reportes automáticos
- Exportar en PDF/Excel
- Enviar por email
- Compartir vía link

#### Entregables
- [ ] `modules/analytics/dashboard.py` implementado
- [ ] API endpoints para dashboard
- [ ] Frontend web funcional
- [ ] Todas las visualizaciones implementadas
- [ ] Sistema de reportes automatizado
- [ ] Documentación de uso del dashboard

#### Dependencias
- Requiere aggregator e insights (Sprint 12)
- Requiere API funcionando (probablemente ya existe)

#### Riesgos
- **Referencia:** Sección 6.1 (Performance)
- **Mitigación:** Caching agresivo de métricas agregadas, pre-cálculo nocturno

---

## FASE 7: OPTIMIZACIÓN Y PULIDO (Semanas 19-20)

### SPRINT 14: Optimización de Performance (Semana 19)

#### Objetivos
- Sistema optimizado para escala
- Tiempos de respuesta óptimos
- Uso eficiente de recursos

#### Optimizaciones Requeridas

**1. Base de Datos**
- **Referencia:** Sección 6.1.3 (Optimización de Queries)
- **Acciones:**
  - Analizar queries lentos con EXPLAIN ANALYZE
  - Crear índices adicionales si necesarios
  - Optimizar N+1 queries (ejemplos en Sección 6.1.3)
  - Implementar query patterns optimizados

**2. Caching Estratégico**
- **Referencia:** Sección 6.1.2 (Estrategias de Caching)
- **Implementar:**
  - CacheManager completo (ver código en Sección 6.1.2)
  - L1: User Session Cache (30 min TTL)
  - L2: Content Cache (1 hora TTL)
  - L3: Computed Cache (5 min TTL)
  - Sistema de invalidación selectiva

**3. Operaciones del CoordinadorCentral**
- **Referencia:** Sección 6.1.1 - Punto 2 (Performance de Transacciones)
- **Acciones:**
  - Mover operaciones no críticas a async
  - Optimizar validaciones con cache
  - Implementar connection pooling optimizado
  - Configurar timeouts apropiados

**4. Tracking de Analytics**
- **Referencia:** Sección 6.1.1 - Punto 3 (Tracking de Analytics)
- **Ya implementado en Sprint 3.5**, pero verificar:
  - Buffer funcionando correctamente
  - Batch inserts eficientes
  - Particionamiento de tablas activo

#### Load Testing

**Herramientas:**
- Locust o Apache JMeter
- Simular 1000+ usuarios concurrentes

**Escenarios de testing:**
1. Usuarios navegando narrativa
2. Usuarios realizando compras simultáneas
3. Spike de reacciones en contenido popular
4. Carga del dashboard por admins

**Métricas objetivo:**
- P50 latency: < 200ms
- P95 latency: < 1 segundo
- P99 latency: < 2 segundos
- Tasa de error: < 0.1%

#### Optimización de Event Bus

- Verificar que Redis puede manejar la carga
- Considerar Redis Cluster si necesario
- Optimizar serialización de eventos

#### Entregables
- [ ] Todos los queries optimizados
- [ ] CacheManager completo implementado
- [ ] Load testing completado con métricas objetivo cumplidas
- [ ] Connection pooling optimizado
- [ ] Documentación de optimizaciones

#### Dependencias
- Requiere sistema completo funcionando
- Todos los módulos deben estar estables

#### Riesgos
- **Referencia:** Sección 7.1 - Riesgo 2 (Performance de Transacciones)
- **Referencia:** Sección 7.1 - Riesgo 4 (Escalabilidad de Experiencias)

---

### SPRINT 15: Testing Final y Documentación (Semana 20)

#### Objetivos
- Cobertura de tests >80%
- Documentación completa
- Sistema production-ready

#### Testing Completo

**1. Tests Unitarios**
- **Referencia:** Sección 6.3.1 (Estrategia de Testing)
- **Target:** 60% de cobertura (base de la pirámide)
- **Áreas críticas:**
  - CoordinadorCentral
  - Validators
  - Lógica de negocio en cada módulo

**2. Tests de Integración**
- **Referencia:** Sección 6.3.1 (Tests de Integración)
- **Target:** 30% de cobertura
- **Ejemplos de tests:** Ver código en Sección 6.3.1
- **Áreas clave:**
  - Flujos de experiencias completos
  - Flujos de compra end-to-end
  - Integraciones entre módulos

**3. Tests End-to-End**
- **Referencia:** Sección 6.3.1 (Tests End-to-End)
- **Target:** 10% de cobertura
- **Ejemplo:** `test_new_user_to_vip_conversion` (ver Sección 6.3.1)
- **Escenarios críticos:**
  - Journey completo de usuario nuevo
  - Conversión free→VIP
  - Completar experiencia compleja

**4. Tests de Regresión**
- Verificar que funcionalidad existente no se rompió
- Automatizar tests de regresión en CI/CD

#### Documentación Completa

**1. Documentación Técnica**
- **Arquitectura general:** Diagramas actualizados
- **Módulos individuales:** Documentación de cada módulo
- **APIs internas:** Referencia completa (ver Sección 3.3)
- **Modelos de datos:** ERD actualizado
- **Flujos de coordinación:** Secuencia de operaciones

**2. Documentación de Operaciones (Runbooks)**
- **Referencia:** Sección 7.1 - Riesgo 10 (Documentación)
- **Runbooks para:**
  - Deployment procedure
  - Rollback procedure
  - Troubleshooting común
  - Gestión de alertas
  - Backup y restore
  - Scaling procedures

**3. Documentación de Usuario Admin**
- Guía de uso del dashboard
- Cómo crear experiencias
- Cómo configurar tienda
- Cómo interpretar métricas
- FAQs

**4. Architecture Decision Records (ADRs)**
- **Referencia:** Sección 7.1 - Riesgo 10
- **Documentar decisiones importantes:**
  - ADR 001: PostgreSQL como Source of Truth
  - ADR 002: Arquitectura de CoordinadorCentral
  - ADR 003: Sistema de Experiencias Unificadas
  - ADR 004: Estrategia de Caching
  - etc.

#### Security Audit

**Revisión de seguridad:**
- **Referencia:** Sección 6.2 (Seguridad y Validación)
- **Áreas a auditar:**
  - Validación de transacciones de besitos (ver Sección 6.2.1 - Punto 1)
  - Validación de compras (ver Sección 6.2.1 - Punto 2)
  - Validación de acceso VIP (ver Sección 6.2.1 - Punto 3)
  - Rate limiting (ver Sección 6.2.3)
  - Prevención de fraude (ver Sección 6.2.2)

**Herramientas:**
- OWASP ZAP para scanning
- Bandit para análisis de código Python
- Manual code review de áreas críticas

#### Preparación para Producción

**Checklist:**
- [ ] Todos los secrets en variables de ambiente
- [ ] Logging configurado apropiadamente (ver Sección 6.3.2)
- [ ] Monitoring configurado (Prometheus/Grafana) (ver Sección 6.3.2)
- [ ] Alertas configuradas
- [ ] Backups automáticos configurados
- [ ] Plan de rollback probado
- [ ] Feature flags configurados
- [ ] Rate limiting activo

#### Entregables
- [ ] Cobertura de tests >80%
- [ ] Documentación técnica completa
- [ ] Runbooks operacionales
- [ ] Security audit completado
- [ ] Sistema production-ready
- [ ] Checklist de pre-lanzamiento completado

#### Dependencias
- Requiere TODO el sistema implementado y optimizado

---

## FASE 8: LANZAMIENTO GRADUAL (Semanas 21-23)

### Estrategia de Lanzamiento

**Referencia:** Sección 7.3 - Riesgo 9 (Bugs en Producción)

#### Semana 21: Beta Privada

**Objetivo:** Validar con usuarios de confianza

**Acciones:**
1. **Seleccionar beta testers**
   - 20-50 usuarios de confianza
   - Mezcla de usuarios activos y nuevos
   - Incluir diferentes arquetipos

2. **Feature Flags**
   - **Referencia:** Sección 7.3 - Riesgo 9 (código de FeatureFlags)
   - Habilitar nuevas features solo para beta testers
   - Monitorear métricas específicas

3. **Recolección de Feedback**
   - Encuestas post-uso
   - Entrevistas 1-on-1
   - Analytics de comportamiento

**Métricas a monitorear:**
- Tasa de error
- Tiempos de respuesta
- Engagement con nuevas features
- Feedback cualitativo

**Criterio de éxito:**
- Tasa de error < 1%
- NPS > 30
- >70% de testers usan nuevas features

---

#### Semana 22: Rollout Gradual

**Objetivo:** Lanzamiento gradual a todos los usuarios

**Plan de rollout:**
- **Referencia:** Sección 7.3 - Riesgo 9 (Feature Flags con Rollout Gradual)

**Día 1-2:** 10% de usuarios
- Monitorear intensivamente
- Estar listos para rollback

**Día 3-4:** 25% de usuarios
- Si métricas son buenas, continuar

**Día 5-6:** 50% de usuarios
- Monitorear capacidad del sistema

**Día 7:** 100% de usuarios
- Si todo va bien, activar completamente

**Monitoring Post-Deployment**
- **Referencia:** Sección 7.3 - Riesgo 9 (código de post_deployment_monitoring)
- **Métricas críticas:**
  - Error rate
  - Response time
  - User complaints
- **Alertas automáticas**
- **Rollback automático** si error rate > 2x baseline

---

#### Semana 23: Estabilización

**Objetivo:** Estabilizar sistema y optimizar basado en datos reales

**Acciones:**
1. **Análisis de Métricas Reales**
   - Comparar contra métricas objetivo (ver Sección 8.3 - Recomendación 5)
   - Identificar áreas de mejora

2. **Corrección de Bugs Menores**
   - Bugs no críticos encontrados en producción
   - Optimizaciones de UX

3. **Ajustes de Balance**
   - **Referencia:** Sección 7.2 - Riesgo 6 (Balance Económico)
   - Ajustar recompensas de besitos si necesario
   - Ajustar precios de tienda si necesario

4. **Optimizaciones de Performance**
   - Basadas en bottlenecks reales detectados

**Métricas de Éxito del Lanzamiento:**
```
Métrica                          Target    Real    Estado
─────────────────────────────────────────────────────────
Conversión Free→VIP              > 5%      ___     ___
Retención día 30                 > 40%     ___     ___
ARPU                             > $2      ___     ___
Engagement con Experiencias      > 30%     ___     ___
NPS                              > 40      ___     ___
Tasa de Error                    < 0.5%    ___     ___
P95 Latency                      < 1s      ___     ___
```

---

## CONTINGENCIAS Y PLANES B

### Si hay Delays Significativos

**Referencia:** Sección 7.3 - Riesgo 8 (Delays)

#### Opción 1: MVP Reducido
**Lanzar solo:**
- Fase 1-3: CoordinadorCentral + Comercio
- Posponer: Experiencias y Analytics Avanzado

**Beneficio:** Time-to-market más rápido
**Riesgo:** Menos diferenciación

#### Opción 2: Agregar Recursos
- Contratar developers adicionales
- Trabajar más sprints en paralelo

**Beneficio:** Mantener timeline
**Riesgo:** Costo adicional, complejidad de coordinación

#### Opción 3: Extender Timeline
- Agregar 4-6 semanas adicionales
- Mantener alcance completo

**Beneficio:** Calidad no se compromete
**Riesgo:** Retraso en monetización

---

### Si Métricas Post-Lanzamiento No Cumplen Targets

**Referencia:** Sección 8.3 - Recomendación 5 (Métricas de Éxito)

#### Si Conversión < 5%
**Posibles causas:**
- Precio muy alto
- Valor percibido muy bajo
- Flujo de conversión confuso

**Acciones:**
- A/B test de precios
- Mejorar ofertas contextuales
- Simplificar flujo de upgrade

#### Si Retención < 40%
**Posibles causas:**
- Contenido insuficiente
- Experiencias no atractivas
- Bugs frustrantes

**Acciones:**
- Crear más contenido urgente
- Revisar experiencias con bajo engagement
- Priorizar bug fixes

#### Si Engagement con Experiencias < 30%
**Posibles causas:**
- Experiencias muy complejas
- No se entiende el concepto
- Recompensas no atractivas

**Acciones:**
- **Referencia:** Sección 7.2 - Riesgo 7 (Baja Adopción)
- Simplificar experiencias existentes
- Mejor promoción in-app
- Aumentar recompensas

**Criterio de Cancelación:**
- **Referencia:** Sección 7.2 - Riesgo 7
- Si < 20% de usuarios inician experiencias después de 2 meses, re-evaluar

---

## RECURSOS ADICIONALES

### Secciones de Referencia Rápida por Tema

**Arquitectura e Integración:**
- CoordinadorCentral: Sección 3.1
- APIs Internas: Sección 3.3
- Nuevos Eventos: Sección 3.2

**Data Model:**
- Extensiones a modelos existentes: Sección 4.1
- Nuevos modelos: Sección 4.2
- Estrategia de migración: Sección 4.3

**Performance:**
- Puntos críticos: Sección 6.1.1
- Caching: Sección 6.1.2
- Optimización de queries: Sección 6.1.3
- Escalabilidad: Sección 6.1.4

**Seguridad:**
- Validación de transacciones: Sección 6.2.1
- Prevención de fraude: Sección 6.2.2
- Rate limiting: Sección 6.2.3

**Testing:**
- Estrategia general: Sección 6.3.1
- Logging y monitoring: Sección 6.3.2

**Riesgos:**
- Riesgos técnicos: Sección 7.1
- Riesgos de producto: Sección 7.2
- Riesgos de implementación: Sección 7.3

**Decisiones Estratégicas:**
- Recomendaciones: Sección 8.3
- Alternativas: Sección 8.4
- Próximos pasos: Sección 8.5

---

## MATRIZ DE REFERENCIAS POR SPRINT

| Sprint | Secciones Clave a Consultar |
|--------|----------------------------|
| **Sprint 1** | 3.1 (CoordinadorCentral), 3.2 (Eventos) |
| **Sprint 2** | 4.1 (Extensiones), 4.3 (Migraciones), 6.1.3 (Índices) |
| **Sprint 3** | 2.2 (Reacciones), 4.2 (Modelos Reacciones), 3.1 (REACCIONAR_CONTENIDO) |
| **Sprint 3.5** | 2.6 (Analytics), 4.2 (Modelos Analytics), 6.1.1 (Performance) |
| **Sprint 4** | 2.3 (Comercio completo), 4.2 (Modelos Comercio) |
| **Sprint 5** | 2.3 (Payments, Checkout), 6.2.1 (Seguridad Compras) |
| **Sprint 6** | 2.3 (Unlocks, Arquetipos, Upselling), 7.2 Riesgo 6 |
| **Sprint 7** | 2.5 (Experiencias completo), 4.2 (Modelos Experiencias) |
| **Sprint 8** | 2.5 (Builder, Propagation, Templates) |
| **Sprint 9** | 2.5 (Integraciones), 6.3.1 (Tests) |
| **Sprint 10** | 3.1 (Operaciones Completas), 6.1.1 (Performance), 7.1 Riesgo 2 |
| **Sprint 11** | Arquitectura conceptual, 2.4 (Lifecycle), 7.2 Riesgo 5 |
| **Sprint 12** | 2.6 (Analytics Completo) |
| **Sprint 13** | 2.6 (Dashboard), 3.3 (APIs) |
| **Sprint 14** | 6.1 (Performance completo), 7.1 Riesgos 2 y 4 |
| **Sprint 15** | 6.3 (Testing completo), 6.2 (Seguridad), 7.1 Riesgo 10 |
| **Lanzamiento** | 7.3 Riesgo 9, 8.3 (Métricas), 8.5 (Próximos pasos) |

---

## CHECKLIST EJECUTIVO DE PROGRESO

### Fundamentos
- [ ] CoordinadorCentral base operativo (Sprint 1)
- [ ] Data model extendido (Sprint 2)
- [ ] Sistema de reacciones funcional (Sprint 3)
- [ ] Analytics básico tracking (Sprint 3.5)

### Monetización
- [ ] Tienda y catálogo funcional (Sprint 4)
- [ ] Sistema de pagos completo (Sprint 5)
- [ ] Desbloqueos y arquetipos (Sprint 6)

### Engagement Profundo
- [ ] Core de experiencias operativo (Sprint 7)
- [ ] Builder y propagación (Sprint 8)
- [ ] Integración profunda completa (Sprint 9)

### Optimización
- [ ] CoordinadorCentral optimizado (Sprint 10)
- [ ] Flujos de conversión (Sprint 11)
- [ ] Analytics avanzado (Sprint 12)
- [ ] Dashboard administrativo (Sprint 13)

### Production Ready
- [ ] Performance optimizado (Sprint 14)
- [ ] Testing y documentación completos (Sprint 15)
- [ ] Lanzamiento gradual exitoso (Semanas 21-23)

---

**Este roadmap debe consultarse junto con el documento de investigación completo. Cada sprint referencia las secciones específicas donde se encuentra la información detallada, especificaciones técnicas y ejemplos de código.**
