# Prompt de Investigación y Especificación Técnica: Evolución de DianaBot a su Arquitectura Objetivo

## 1. Contexto y Objetivo de la Investigación

**Contexto del Sistema (Estado Actual - "As-Is"):**
El proyecto DianaBot posee una estructura de directorios bien definida y una extensa documentación que describe una arquitectura de sistema altamente integrada. Sin embargo, el código fuente actual es un esqueleto funcional donde los componentes de integración clave (`CoordinadorCentral`, `EventBus`) y las definiciones de datos (`SQLAlchemy models`, `docker-compose.yml`) están ausentes o vacíos. La lógica de negocio reside en los manejadores de eventos (`handlers`), en lugar de ser orquestada centralmente.

**Arquitectura Objetivo (Estado Futuro - "To-Be"):**
La documentación describe un ecosistema sofisticado con módulos que se comunican síncrona y asíncronamente a través de un `CoordinadorCentral` y un `EventBus`, operando sobre una infraestructura containerizada y bases de datos bien definidas.

**Objetivo Principal de la Investigación:**
**Investigar, analizar y especificar** un plan de acción técnico y detallado para cerrar la brecha entre el estado actual del código y la arquitectura objetivo. El resultado de esta investigación **no será una implementación**, sino un **documento de diseño técnico y un plan de evolución** que sirva como guía para un equipo de desarrollo. Se deben definir las estructuras de datos, las interfaces de los componentes, los flujos de comunicación y las especificaciones de refactorización necesarias.

---

## 2. Áreas Críticas de Investigación y Especificación

Se requiere un análisis profundo y la posterior **especificación** de las siguientes áreas.

### 2.1. La Fundación: Infraestructura y Modelos de Datos

**Tarea:** Definir la capa de persistencia de datos y la infraestructura de servicios containerizada.

**Investigación y Especificación Requerida:**
1.  **Definición de Modelos de Datos:**
    -   Analizar los archivos `.sql` en `database/migrations/`.
    -   **Especificar el código completo** para el archivo `database/models.py`, definiendo cada clase de `SQLAlchemy` con sus columnas, tipos, relaciones (`relationship`, `ForeignKey`, `back_populates`), e índices.

2.  **Especificación de Infraestructura como Código:**
    -   **Diseñar y especificar el contenido completo** del archivo `docker-compose.yml`.
    -   Detallar los servicios `postgres`, `mongodb`, y `redis`, incluyendo su configuración de red, volúmenes para persistencia y la gestión de credenciales a través de un archivo `.env`.

3.  **Especificación de la Lógica de Conexión:**
    -   **Detallar la implementación** requerida en `database/connection.py` para gestionar las sesiones de las bases de datos.

### 2.2. El Cerebro: Diseño del `CoordinadorCentral` y `TransactionManager`

**Tarea:** Diseñar el orquestador central para manejar flujos de negocio complejos.

**Investigación y Especificación Requerida:**
1.  **Diseño de la Interfaz y Lógica del `CoordinadorCentral`:**
    -   **Diseñar la arquitectura de la clase** `CoordinadorCentral` en `core/coordinator.py`.
    -   **Especificar la firma de cada método público** (`TOMAR_DECISION`, `COMPRAR_ITEM`, etc.) y documentar sus parámetros y tipo de retorno.
    -   **Escribir pseudocódigo o diagramas de secuencia** para cada método, detallando el flujo de llamadas a los diferentes servicios de los módulos (`modules/`).

2.  **Diseño del `TransactionManager`:**
    -   **Especificar la implementación** de la clase `TransactionManager` en `core/transaction_manager.py`.
    -   Detallar cómo funcionará el patrón `with transaction.atomic()` y cómo los servicios registrarán operaciones de compensación (rollback).

3.  **Plan de Refactorización de Handlers:**
    -   **Crear un plan de refactorización** para los archivos en `bot/handlers/`.
    -   Proveer ejemplos concretos de "antes" y "después" para un handler típico (ej. `narrative_decision_handler`), mostrando cómo la lógica de negocio se mueve desde el handler hacia el `CoordinadorCentral`.

### 2.3. El Sistema Nervioso: Diseño del `EventBus` Asíncrono

**Tarea:** Diseñar el sistema de comunicación asíncrona.

**Investigación y Especificación Requerida:**
1.  **Especificación del `EventBus`:**
    -   **Detallar la implementación** de la clase `EventBus` en `core/event_bus.py` usando `redis` Pub/Sub.
    -   Definir la estructura y el contenido del payload estándar para los eventos.

2.  **Diseño del Registro de Eventos:**
    -   **Especificar cómo funcionará** el registro de manejadores en `core/event_handlers.py`.
    -   Crear una tabla o mapa que relacione cada `event_type` con los módulos y funciones que deben suscribirse a él.

3.  **Mapeo de Puntos de Publicación de Eventos:**
    -   **Identificar y listar** los puntos exactos en la lógica de los servicios (`modules/`) donde se deben emitir eventos, especificando el tipo de evento y los datos a incluir.

### 2.4. Especificación de los Módulos de Negocio

**Tarea:** Definir la lógica de negocio faltante en los módulos.

**Investigación y Especificación Requerida:**
1.  **Módulo de Comercio (`modules/commerce/`):**
    -   **Definir las interfaces y la lógica interna** para `ShopManager`, `CheckoutProcessor`, y `ArchetypeEngine`, detallando cómo interactuarán con los modelos de datos.

2.  **Módulos de Gamificación y Experiencias:**
    -   **Especificar las funcionalidades** a completar en `missions.py`, `achievements.py`, etc.
    -   **Diseñar la arquitectura completa** del `ExperienceEngine` (`modules/experiences/`), detallando cómo gestionará los flujos unificados y validará los requisitos compuestos.

---

## 3. Metodología de Investigación Sugerida

Se propone un enfoque incremental para la investigación y especificación.

-   **Fase 1: Análisis de la Fundación.** Definir las especificaciones para los modelos de datos y la infraestructura de Docker.
-   **Fase 2: Diseño del Núcleo de Integración.** Diseñar la arquitectura y las interfaces para el `CoordinadorCentral` y el `EventBus`.
-   **Fase 3: Plan de Refactorización.** Analizar los componentes existentes y crear un plan detallado para su adaptación a la nueva arquitectura.
-   **Fase 4: Especificación de la Lógica de Negocio.** Detallar la funcionalidad requerida para cada uno de los módulos de negocio.
-   **Fase 5: Plan de Integración y Pruebas.** Diseñar un plan de pruebas de integración para validar que la arquitectura especificada, una vez implementada, funcionará como un todo cohesivo.

---

## 4. Entregables Esperados de la Investigación

El resultado final de esta investigación será un **Documento de Diseño Técnico y Plan de Evolución** exhaustivo, que contendrá las siguientes secciones:

1.  **Especificación de Modelos de Datos:** El código completo y documentado para `database/models.py`.
2.  **Especificación de Infraestructura:** El contenido completo y comentado para el archivo `docker-compose.yml`.
3.  **Documentos de Diseño de Componentes Core:**
    -   Diseño técnico para `CoordinadorCentral` y `TransactionManager` con pseudocódigo y/o diagramas de secuencia.
    -   Diseño técnico para `EventBus` y un mapa de eventos del sistema.
4.  **Plan de Refactorización:** Un documento que guíe la migración de la lógica de los handlers al `CoordinadorCentral`, con ejemplos claros.
5.  **Especificaciones Funcionales de Módulos:** Documentos que detallen la lógica, funciones y responsabilidades de cada servicio dentro de los `modules/`.
6.  **Plan de Pruebas de Integración:** Una lista de escenarios de prueba clave para validar la arquitectura una vez implementada.