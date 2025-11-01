# FASE 7: OPTIMIZACIÓN Y PULIDO (Semanas 19-20)

## Especificación de la Fase

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

## Referencias del Documento de Investigación

### Sección 6.1.1 - Puntos Críticos de Performance

**1. Validación de Requisitos Compuestos**
```
PROBLEMA: Validar requisitos puede requerir queries a múltiples tablas
IMPACTO: Latencia de 200-500ms por validación

SOLUCIONES:
- Caching de requisitos frecuentes en Redis
- Índices compuestos en tablas críticas
- Pre-cálculo de requisitos cumplidos
- Lazy loading de requisitos no críticos

IMPLEMENTACIÓN:
class RequirementCache:
    def get_cached_validation(user_id, target_id):
        cache_key = f"req_validation:{user_id}:{target_id}"
        cached = redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        result = compute_validation(user_id, target_id)
        redis.setex(cache_key, 300, json.dumps(result))  # 5 min TTL
        return result
```

**2. Operaciones del CoordinadorCentral**
```
PROBLEMA: Transacciones distribuidas pueden ser lentas
IMPACTO: Operaciones complejas toman 1-2 segundos

SOLUCIONES:
- Procesamiento asíncrono de operaciones no críticas
- Queue de operaciones con workers dedicados
- Optimización de queries con EXPLAIN ANALYZE
- Connection pooling optimizado

IMPLEMENTACIÓN:
# Operaciones críticas: síncronas
# Operaciones no críticas: asíncronas via Celery

@celery.task
def apply_purchase_unlocks_async(user_id, item_id):
    # Ejecutar en background
    pass

def COMPRAR_ITEM(user_id, item_id, payment_method):
    # Compra síncrona
    result = process_payment_sync(user_id, item_id)
    
    # Desbloqueos asíncronos
    apply_purchase_unlocks_async.delay(user_id, item_id)
    
    return result
```

**3. Tracking de Analytics**
```
PROBLEMA: Cada evento genera writes a base de datos
IMPACTO: Miles de inserts por minuto bajo carga

SOLUCIONES:
- Batch inserts cada 5-10 segundos
- Buffer en memoria con flush periódico
- Tabla particionada por fecha
- Índices optimizados para queries de lectura

IMPLEMENTACIÓN:
class EventCollectorBuffer:
    def __init__(self):
        self.buffer = []
        self.buffer_size = 1000
        self.flush_interval = 10  # segundos
    
    def track_event(self, event):
        self.buffer.append(event)
        if len(self.buffer) >= self.buffer_size:
            self.flush()
    
    def flush(self):
        if self.buffer:
            # Bulk insert
            db.bulk_insert_mappings(AnalyticsEvent, self.buffer)
            db.commit()
            self.buffer = []
```

### Sección 6.1.2 - Estrategias de Caching

**Redis Cache Strategy:**
```
┌──────────────────────────────────────────────────────────┐
│                   CACHING LAYERS                          │
└──────────────────────────────────────────────────────────┘

L1: User Session Cache (TTL: 30 min)
  - Estado VIP del usuario
  - Balance de besitos
  - Progreso narrativo actual
  - Experiencias activas

L2: Content Cache (TTL: 1 hora)
  - Fragmentos narrativos frecuentes
  - Catálogo de tienda
  - Configuración de recompensas
  - Templates de experiencias

L3: Computed Cache (TTL: 5 min)
  - Validaciones de requisitos
  - Arquetipos de usuario
  - Métricas agregadas
  - Ofertas personalizadas

INVALIDACIÓN:
- Manual: Al modificar contenido
- Automática: Por TTL
- Selective: Solo claves afectadas por cambio
```

**Implementación de Cache Manager:**
```python
class CacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def get_user_vip_status(self, user_id):
        cache_key = f"user:{user_id}:vip_status"
        cached = self.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        # Consultar DB
        status = db_query_vip_status(user_id)
        
        # Cachear por 30 minutos
        self.redis.setex(cache_key, 1800, json.dumps(status))
        return status
    
    def invalidate_user_cache(self, user_id):
        # Invalidar todas las claves del usuario
        pattern = f"user:{user_id}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
```

### Sección 6.1.3 - Optimización de Queries

**Índices Críticos Requeridos:**
```sql
-- User queries
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_vip_status ON users(archetype_primary, conversion_score);

-- Narrative queries
CREATE INDEX idx_fragments_experience ON narrative_fragments(experience_id) 
    WHERE experience_id IS NOT NULL;
CREATE INDEX idx_fragments_vip ON narrative_fragments(is_vip_exclusive) 
    WHERE is_vip_exclusive = true;
CREATE INDEX idx_user_progress_composite ON user_narrative_progress(user_id, status, last_activity_at);

-- Experience queries
CREATE INDEX idx_experience_components_composite ON experience_components(experience_id, sequence_order);
CREATE INDEX idx_user_experience_status ON user_experience_progress(user_id, status, last_activity_at);

-- Commerce queries
CREATE INDEX idx_shop_items_available ON shop_items(is_available, type) 
    WHERE is_available = true;
CREATE INDEX idx_purchases_user_date ON user_purchases(user_id, purchase_date DESC);

-- Analytics queries
CREATE INDEX idx_analytics_user_time ON analytics_events(user_id, timestamp DESC);
CREATE INDEX idx_analytics_type_time ON analytics_events(event_type, timestamp DESC);

-- Partitioning para analytics_events
CREATE TABLE analytics_events_2025_10 PARTITION OF analytics_events
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
```

**Query Optimization Patterns:**
```python
# MALO: N+1 queries
def get_user_experiences(user_id):
    progress = UserExperienceProgress.query.filter_by(user_id=user_id).all()
    for p in progress:
        p.experience = Experience.query.get(p.experience_id)  # N queries
        p.components = ExperienceComponent.query.filter_by(
            experience_id=p.experience_id
        ).all()  # N queries más
    return progress

# BUENO: Single query with joins
def get_user_experiences(user_id):
    return db.session.query(UserExperienceProgress)\
        .options(
            joinedload(UserExperienceProgress.experience)
                .joinedload(Experience.components),
            joinedload(UserExperienceProgress.component_completions)
        )\
        .filter(UserExperienceProgress.user_id == user_id)\
        .all()
```

### Sección 6.2 - Seguridad y Validación

#### 6.2.1 - Validación de Transacciones

**Puntos Críticos de Seguridad:**

1. **Validación de Besitos**
```python
class BesitosSecurityValidator:
    def validate_grant(self, user_id, amount, reason):
        # Validar que reason es válido
        if reason not in VALID_BESITOS_REASONS:
            raise SecurityError("Invalid besitos grant reason")
        
        # Validar límites diarios
        today_total = self.get_today_grants(user_id)
        if today_total + amount > MAX_DAILY_GRANTS:
            raise SecurityError("Daily grant limit exceeded")
        
        # Validar que no es manipulación
        if self.detect_manipulation(user_id, amount, reason):
            self.flag_for_review(user_id)
            raise SecurityError("Suspicious activity detected")
        
        return True
    
    def validate_spend(self, user_id, amount, reason):
        # Validar balance suficiente
        balance = self.get_balance(user_id)
        if balance < amount:
            raise InsufficientFundsError()
        
        # Validar que gasto es legítimo
        if reason not in VALID_SPEND_REASONS:
            raise SecurityError("Invalid spend reason")
        
        return True
```

2. **Validación de Compras**
```python
class PurchaseSecurityValidator:
    def validate_purchase(self, user_id, item_id, payment_method):
        # Validar que item existe y está disponible
        item = ShopItem.query.get(item_id)
        if not item or not item.is_available:
            raise ItemNotAvailableError()
        
        # Validar que usuario no ha comprado ya (si es único)
        if item.type == 'unique' and self.user_owns_item(user_id, item_id):
            raise AlreadyOwnedError()
        
        # Validar requisitos de compra
        if not self.meets_purchase_requirements(user_id, item):
            raise RequirementsNotMetError()
        
        # Validar método de pago
        if payment_method == 'besitos':
            balance = self.get_besitos_balance(user_id)
            if balance < item.price_besitos:
                raise InsufficientFundsError()
        
        # Rate limiting: prevenir spam de compras
        if self.is_rate_limited(user_id):
            raise RateLimitError("Too many purchase attempts")
        
        return True
```

#### 6.2.2 - Prevención de Fraude

**Detección de Patrones Sospechosos:**
```python
class FraudDetectionEngine:
    def detect_suspicious_activity(self, user_id, action_type, action_data):
        signals = []
        
        # Señal 1: Actividad inusualmente alta
        activity_rate = self.get_recent_activity_rate(user_id)
        if activity_rate > NORMAL_ACTIVITY_THRESHOLD * 3:
            signals.append('high_activity_rate')
        
        # Señal 2: Patrones de bot
        if self.matches_bot_pattern(user_id):
            signals.append('bot_like_behavior')
        
        # Señal 3: Múltiples cuentas desde mismo dispositivo
        if self.detect_multi_accounting(user_id):
            signals.append('multi_accounting')
        
        # Señal 4: Explotación de mecánicas
        if self.detect_exploit_attempt(action_type, action_data):
            signals.append('exploit_attempt')
        
        if len(signals) >= 2:
            self.flag_user(user_id, signals)
            return FraudAlert(
                user_id=user_id,
                signals=signals,
                severity='high' if len(signals) >= 3 else 'medium'
            )
        
        return None
```

#### 6.2.3 - Rate Limiting

**Implementación de Rate Limits:**
```python
class RateLimiter:
    def check_rate_limit(self, user_id, action_type):
        limits = {
            'purchase': (5, 3600),  # 5 compras por hora
            'reaction': (50, 300),   # 50 reacciones por 5 min
            'decision': (20, 60),    # 20 decisiones por minuto
            'api_call': (100, 60)    # 100 llamadas API por minuto
        }
        
        max_count, window = limits.get(action_type, (100, 60))
        
        key = f"rate_limit:{user_id}:{action_type}"
        current = redis.get(key)
        
        if current and int(current) >= max_count:
            raise RateLimitExceededError(f"Rate limit exceeded for {action_type}")
        
        # Incrementar contador
        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        pipe.execute()
        
        return True
```

### Sección 6.3.1 - Estrategia de Testing

**Pirámide de Tests:**
```
                    ╱╲
                   ╱E2E╲        10% - Tests End-to-End
                  ╱────╲
                 ╱ INT  ╲       30% - Tests de Integración
                ╱────────╲
               ╱   UNIT   ╲     60% - Tests Unitarios
              ╱────────────╲
```

**Tests Unitarios Críticos:**
```python
# tests/test_coordinator.py

class TestCoordinadorCentral:
    def test_tomar_decision_valid_requirements(self):
        # Setup
        user = create_test_user(vip=True, besitos=100)
        fragment = create_test_fragment(requirements={'vip': True})
        decision = create_test_decision(fragment_id=fragment.id)
        
        # Execute
        result = coordinator.TOMAR_DECISION(
            user.id, fragment.id, decision.id
        )
        
        # Assert
        assert result['success'] == True
        assert result['rewards_granted'] is not None
        assert user.refresh_balance() >= 100  # Besitos otorgados
    
    def test_tomar_decision_missing_requirements(self):
        user = create_test_user(vip=False)
        fragment = create_test_fragment(requirements={'vip': True})
        
        result = coordinator.TOMAR_DECISION(user.id, fragment.id, 1)
        
        assert result['success'] == False
        assert 'vip' in result['missing_requirements']
    
    def test_transaction_rollback_on_error(self):
        user = create_test_user(besitos=100)
        
        # Simular error en medio de transacción
        with patch('modules.gamification.besitos.grant_besitos', 
                   side_effect=Exception("DB Error")):
            with pytest.raises(Exception):
                coordinator.COMPRAR_ITEM(user.id, item_id=1, payment_method='besitos')
        
        # Verificar que balance no cambió
        assert user.refresh_balance() == 100
```

**Tests End-to-End:**
```python
# tests/e2e/test_user_journey.py

class TestUserJourney:
    def test_new_user_to_vip_conversion(self, telegram_bot_client):
        # Simular journey completo de usuario
        
        # 1. Usuario nuevo inicia bot
        response = telegram_bot_client.send_message('/start')
        assert 'Bienvenido' in response.text
        
        # 2. Usuario consume contenido narrativo
        response = telegram_bot_client.send_message('Ver historia')
        assert response.has_narrative_content
        
        # 3. Usuario gana besitos por reacciones
        telegram_bot_client.react_to_message(message_id=123, reaction='❤️')
        balance = get_user_balance(telegram_bot_client.user_id)
        assert balance > 0
        
        # 4. Usuario intenta acceder contenido VIP
        response = telegram_bot_client.send_message('Ver contenido exclusivo')
        assert 'VIP requerido' in response.text
        assert response.has_upgrade_offer
        
        # 5. Usuario se suscribe a VIP
        telegram_bot_client.click_button('Suscribirse a VIP')
        # Simular pago exitoso
        telegram_bot_client.complete_payment(amount=9.99)
        
        # 6. Verificar acceso VIP
        response = telegram_bot_client.send_message('Ver contenido exclusivo')
        assert response.has_vip_content
        assert 'VIP requerido' not in response.text
```

### Sección 6.3.2 - Logging y Monitoreo

**Estrategia de Logging:**
```python
import logging
import structlog

# Configuración de structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

class CoordinadorCentral:
    def TOMAR_DECISION(self, user_id, fragment_id, decision_id):
        logger.info(
            "decision_started",
            user_id=user_id,
            fragment_id=fragment_id,
            decision_id=decision_id
        )
        
        try:
            result = self._execute_decision(user_id, fragment_id, decision_id)
            
            logger.info(
                "decision_completed",
                user_id=user_id,
                fragment_id=fragment_id,
                success=True,
                rewards=result['rewards_granted']
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "decision_failed",
                user_id=user_id,
                fragment_id=fragment_id,
                error=str(e),
                exc_info=True
            )
            raise
```

**Métricas de Monitoreo:**
```python
from prometheus_client import Counter, Histogram, Gauge

# Contadores
decisions_total = Counter('decisions_total', 'Total decisions taken', ['status'])
purchases_total = Counter('purchases_total', 'Total purchases', ['method', 'status'])
experiences_started = Counter('experiences_started_total', 'Experiences started')

# Histogramas (latencia)
decision_duration = Histogram('decision_duration_seconds', 'Decision processing time')
purchase_duration = Histogram('purchase_duration_seconds', 'Purchase processing time')

# Gauges (estado actual)
active_users = Gauge('active_users', 'Currently active users')
vip_users = Gauge('vip_users_total', 'Total VIP users')

# Uso en código
@decision_duration.time()
def TOMAR_DECISION(self, user_id, fragment_id, decision_id):
    try:
        result = self._execute_decision(user_id, fragment_id, decision_id)
        decisions_total.labels(status='success').inc()
        return result
    except Exception as e:
        decisions_total.labels(status='error').inc()
        raise
```

### Sección 7.1 - Riesgo 2 (Performance de Transacciones)

**Mitigaciones:**
```python
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

@breaker
def call_external_service():
    # Llamada que puede fallar
    pass
```

### Sección 7.1 - Riesgo 4 (Escalabilidad del Sistema de Experiencias)

**Descripción:** Con cientos de experiencias y miles de usuarios, el tracking de progreso puede volverse un cuello de botella.

**Mitigaciones:**
1. **Desnormalización Estratégica:**
   ```sql
   -- En lugar de calcular cada vez
   SELECT COUNT(*) FROM user_component_completions 
   WHERE user_progress_id = ?
   
   -- Almacenar en user_experience_progress
   UPDATE user_experience_progress 
   SET components_completed = components_completed + 1
   WHERE id = ?
   ```

2. **Particionamiento de Tablas:**
   ```sql
   CREATE TABLE user_experience_progress_2025 PARTITION OF user_experience_progress
       FOR VALUES FROM (1) TO (1000000);
   ```

3. **Lazy Loading:** Cargar solo datos necesarios