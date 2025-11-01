# FASE 6: ANALYTICS AVANZADO Y DASHBOARD (Semanas 17-18)

## Especificación de la Fase

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
     - `get_engagement_metrics()`
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

## Referencias del Documento de Investigación

### Sección 2.6 - Sistema 6: Estadísticas y Analytics

#### Brechas Identificadas

**BRECHA CRÍTICA 1: Ausencia de Sistema de Analytics Unificado**
```
Actual: Estadísticas dispersas en módulos individuales
Requerido: modules/analytics/ centralizado
```

**Estructura del Módulo a Crear:**
```
modules/analytics/
├── __init__.py
├── collector.py           # Recolector de eventos
├── aggregator.py          # Agregador de métricas
├── dashboard.py           # Data para dashboard
├── reports.py             # Generador de reportes
├── insights.py            # Sistema de insights automáticos
└── export.py              # Exportación de datos
```

**Especificación de Componentes:**

**A. aggregator.py**
```python
class MetricsAggregator:
    def get_engagement_metrics(time_range):
        # MAU, DAU, retention
        # Engagement por módulo
        # Tiempo promedio de sesión
        pass
    
    def get_monetization_metrics(time_range):
        # Revenue total
        # Conversión free -> VIP
        # Valor de vida del usuario (LTV)
        # ARPU, ARPPU
        pass
    
    def get_narrative_metrics(time_range):
        # Fragmentos más visitados
        # Tasa de completitud de narrativas
        # Decisiones más populares
        pass
    
    def get_experience_metrics(time_range):
        # Experiencias iniciadas vs completadas
        # Tasa de abandono por experiencia
        # Tiempo promedio de completitud
        pass
```

**B. dashboard.py**
```python
class DashboardDataProvider:
    def get_overview_stats():
        # Stats principales para dashboard admin
        # Usuarios activos, revenue, engagement
        pass
    
    def get_funnel_data():
        # Funnel de conversión
        # Free -> Engaged -> Purchaser -> VIP
        pass
    
    def get_cohort_analysis(cohort_definition):
        # Análisis de cohortes
        # Retención por cohorte
        pass
```

**C. insights.py**
```python
class InsightEngine:
    def detect_drop_off_points():
        # Identificar dónde usuarios abandonan
        # En narrativa, experiencias, misiones
        pass
    
    def identify_high_value_users():
        # Usuarios con mayor potencial de conversión
        # Basado en engagement y comportamiento
        pass
    
    def suggest_content_optimizations():
        # Sugerencias de contenido a crear/modificar
        # Basado en gaps en engagement
        pass
```

**D. alerts.py**
```python
class AlertSystem:
    def check_anomalies():
        # Detectar caídas en engagement
        # Detectar picos de abandono
        # Detectar problemas técnicos
        pass
    
    def notify_admin(alert_type, alert_data):
        # Enviar notificación a admins via Telegram
        pass
    
    def get_alert_config():
        # Configuración de umbrales de alerta
        pass
```

**Modelo de Base de Datos:**
```sql
-- DailyMetrics (agregación diaria)
CREATE TABLE daily_metrics (
    id SERIAL PRIMARY KEY,
    metric_date DATE NOT NULL,
    metric_type VARCHAR(100),
    metric_value DECIMAL(15,2),
    metadata JSONB,
    UNIQUE(metric_date, metric_type)
);

-- UserSessionMetrics
CREATE TABLE user_session_metrics (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_start TIMESTAMP,
    session_end TIMESTAMP,
    actions_count INTEGER,
    modules_accessed JSONB,  -- Array de módulos visitados
    session_duration INTEGER  -- segundos
);
```

**BRECHA 3: Sistema de Alertas Proactivas**
```
Actual: No existe sistema de alertas
Requerido: Alertas automáticas para anomalías
```

**Componente a Crear:** `modules/analytics/alerts.py`
```python
class AlertSystem:
    def check_anomalies():
        # Detectar caídas en engagement
        # Detectar picos de abandono
        # Detectar problemas técnicos
        pass
    
    def notify_admin(alert_type, alert_data):
        # Enviar notificación a admins via Telegram
        pass
    
    def get_alert_config():
        # Configuración de umbrales de alerta
        pass
```

### Sección 3.3 - APIs de Integración entre Módulos

**API de Analytics:**
```python
# === API de Analytics ===
class AnalyticsAPI:
    def track_event(user_id, event_type, event_data) -> None:
        """Registra evento"""
        pass
    
    def get_user_metrics(user_id) -> UserMetrics:
        """Obtiene métricas de usuario"""
        pass
    
    def get_conversion_probability(user_id) -> float:
        """Calcula probabilidad de conversión"""
        pass
    
    def identify_user_archetype(user_id) -> Archetype:
        """Identifica arquetipo de usuario"""
        pass
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