# **PROMPT DE INVESTIGACIÓN PARA IMPLEMENTACIÓN DEL SISTEMA DIANABOT**

## **CONTEXTO DEL SISTEMA**

**Estado Actual:** Sistema modular con componentes básicos implementados (narrativa, gamificación, administración, comercio) pero con integración limitada entre módulos.

**Arquitectura Objetivo:** Ecosistema altamente integrado donde cada componente se interconecta profundamente con los demás, formando un "sistema nervioso" coordinado.

## **OBJETIVO DE INVESTIGACIÓN**

Investigar e implementar los componentes de integración profunda que transformen el sistema actual en el ecosistema interconectado descrito en la arquitectura conceptual.

## **COMPONENTES CRÍTICOS A INVESTIGAR E IMPLEMENTAR**

### **1. COORDINADOR CENTRAL (Sistema Nervioso)**

**Función:** Cerebro del ecosistema que coordina todos los módulos

**Investigación Requerida:**
- Diseñar arquitectura del CoordinadorCentral que maneje flujos como TOMAR_DECISION, ACCEDER_NARRATIVA_VIP, REACCIONAR_CONTENIDO, COMPRAR_ITEM
- Implementar sistema de validación de requisitos compuestos que verifique simultáneamente:
  - Requisitos narrativos (fragmentos visitados)
  - Requisitos de membresía (VIP/FREE)
  - Requisitos de nivel (puntos/gamificación)
  - Requisitos de posesión (items de tienda)
  - Requisitos de experiencia (experiencias previas completadas)
- Crear sistema de eventos unificados que propague cambios entre módulos

### **2. SISTEMA DE EXPERIENCIAS UNIFICADAS**

**Función:** Coordinador que integra múltiples sistemas en flujos cohesivos

**Investigación Requerida:**
- Diseñar modelo de Experiencia que combine elementos de narrativa, gamificación, comercio y administración
- Implementar sistema de propagación automática que sincronice:
  - Progreso narrativo con misiones de gamificación
  - Compras de items con desbloqueo de contenido
  - Membresías VIP con acceso a experiencias
- Crear validador de dependencias entre elementos de diferentes módulos

### **3. SISTEMA DE REQUISITOS COMPUESTOS**

**Función:** Validación unificada de múltiples condiciones

**Investigación Requerida:**
- Extender el sistema actual de flags narrativos para incluir:
  - Condiciones de gamificación (nivel mínimo, logros)
  - Condiciones de membresía (VIP activa)
  - Condiciones de comercio (posesión de items)
  - Condiciones de experiencia (experiencias completadas)
- Implementar evaluador de condiciones que verifique simultáneamente múltiples sistemas
- Crear sistema de retroalimentación que explique al usuario requisitos faltantes

### **4. SISTEMA DE RECOMPENSAS COMBINADAS**

**Función:** Distribución unificada de recompensas cruzadas

**Investigación Requerida:**
- Diseñar sistema que otorgue simultáneamente:
  - Recompensas narrativas (desbloqueo de contenido)
  - Recompensas de gamificación (puntos, logros)
  - Recompensas comerciales (items, descuentos)
  - Actualizaciones de rol (VIP/FREE)
- Implementar propagador de recompensas que actualice todos los módulos afectados
- Crear sistema de notificaciones unificadas para recompensas múltiples

### **5. SISTEMA DE FLUJO DE INFORMACIÓN**

**Función:** Comunicación bidireccional entre módulos

**Investigación Requerida:**
- Extender el Event Bus actual para manejar eventos complejos como:
  - `user.experience_completed` → Desbloquea narrativa + Otorga puntos + Actualiza estadísticas
  - `narrative.decision_made` → Actualiza gamificación + Verifica requisitos comerciales
  - `commerce.purchase_made` → Desbloquea contenido + Actualiza membresía + Notifica gamificación
- Implementar sistema de dependencias que propague cambios automáticamente
- Crear mecanismo de rollback para transacciones distribuidas

### **6. SISTEMA DE ARQUETIPOS Y PERSONALIZACIÓN**

**Función:** Personalización de experiencia basada en comportamiento

**Investigación Requerida:**
- Analizar datos existentes para identificar patrones de usuario
- Implementar sistema de clasificación de arquetipos (explorador, coleccionista, social, etc.)
- Diseñar contenido personalizado que se adapte al arquetipo detectado
- Crear sistema de recomendaciones cruzadas entre módulos

## **METODOLOGÍA DE INVESTIGACIÓN**

### **Fase 1: Análisis de Estado Actual**
- Mapear todas las integraciones existentes entre módulos
- Identificar puntos de acoplamiento actuales
- Documentar APIs y eventos disponibles

### **Fase 2: Diseño de Arquitectura de Integración**
- Diseñar interfaces comunes entre módulos
- Definir contratos de comunicación
- Especificar flujos de datos unificados

### **Fase 3: Implementación Gradual**
- Implementar CoordinadorCentral como capa de orquestación
- Extender sistemas existentes con hooks de integración
- Crear sistema de pruebas de integración

### **Fase 4: Optimización y Escalado**
- Implementar caché distribuido para validaciones frecuentes
- Diseñar sistema de colas para operaciones asíncronas
- Crear monitoreo de rendimiento de integraciones

## **CRITERIOS DE ÉXITO**

- **Integración Profunda:** Los módulos se comunican bidireccionalmente sin intervención manual
- **Experiencia Unificada:** Los usuarios perciben un solo sistema cohesivo
- **Propagación Automática:** Los cambios en un módulo se reflejan automáticamente en otros
- **Validación Compuesta:** El sistema verifica requisitos de múltiples módulos simultáneamente
- **Retroalimentación Positiva:** Las acciones en un módulo incentivan participación en otros

## **ENTREGABLES ESPERADOS**

1. **CoordinadorCentral** completamente funcional
2. **Sistema de Experiencias Unificadas** operativo
3. **Validación de Requisitos Compuestos** implementada
4. **Propagación Automática de Recompensas** funcionando
5. **Sistema de Arquetipos** personalizando contenido
6. **Dashboard de Integración** mostrando interconexiones

---

Este prompt guiará al LLM en la investigación sistemática para transformar el sistema actual en el ecosistema interconectado descrito en la arquitectura conceptual, enfocándose específicamente en los componentes de integración profunda que convierten módulos independientes en un sistema nervioso unificado.