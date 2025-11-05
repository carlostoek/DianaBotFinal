# Prompt de Investigación y Desarrollo: Evolución de DianaBot a su Arquitectura Objetivo

## 1. Contexto y Objetivo General

**Contexto del Sistema (Estado Actual - "As-Is"):**
El proyecto DianaBot posee una estructura de directorios bien definida y una extensa documentación que describe una arquitectura de sistema altamente integrada, modular y orientada a eventos. Sin embargo, un análisis del código fuente revela que la implementación actual es un esqueleto funcional. Los componentes de integración clave (como el `CoordinadorCentral` y el `EventBus`) y las definiciones de modelos de datos (`SQLAlchemy models`) están ausentes o vacíos. La lógica de negocio, en lugar de ser orquestada, reside directamente en los manejadores de eventos del bot (`handlers`).

**Arquitectura Objetivo (Estado Futuro - "To-Be"):**
La documentación describe un ecosistema sofisticado donde los módulos (`narrativa`, `gamificación`, `comercio`, etc.) se comunican de forma síncrona a través de un `CoordinadorCentral` para operaciones transaccionales, y de forma asíncrona mediante un `EventBus` para acciones desacopladas. El sistema debe operar sobre una infraestructura containerizada (`Docker`) con bases de datos relacionales (PostgreSQL), de documentos (MongoDB) y en memoria (Redis), definidas y gestionadas a través de un ORM (SQLAlchemy) y configuraciones explícitas.

**Objetivo Principal de la Investigación:**
El propósito de esta investigación es definir un plan de acción técnico, detallado y por fases para **desarrollar los componentes faltantes y refactorizar el código existente** con el fin de alinear completamente la implementación de DianaBot con su arquitectura conceptual documentada. El resultado final debe ser un sistema robusto, escalable, mantenible y que refleje fielmente el diseño arquitectónico propuesto.

---

## 2. Áreas Críticas de Investigación y Desarrollo

Se requiere un análisis profundo y la posterior implementación de las siguientes áreas, que constituyen la brecha principal entre el estado actual y el objetivo.

### 2.1. La Fundación: Infraestructura y Modelos de Datos

**Tarea:** Definir e implementar la capa de persistencia de datos y la infraestructura de servicios containerizada.

**Investigación Requerida:**
1.  **Ingeniería Inversa de Modelos de Datos:**
    -   Analizar exhaustivamente todos los archivos `.sql` en `database/migrations/` (desde `001` hasta `019`).
    -   A partir de las sentencias `CREATE TABLE`, derivar y construir los modelos `SQLAlchemy` correspondientes en el archivo `database/models.py`. Cada tabla debe tener su clase Python, con sus columnas, tipos de datos, relaciones (`relationship`), claves foráneas (`ForeignKey`) y back-references (`back_populates`).
    -   Prestar especial atención a las relaciones entre tablas (ej. `User` con `Subscription`, `ShopItem` con `LorePiece`, etc.) para implementarlas correctamente en el ORM.

2.  **Definición de Infraestructura como Código:**
    -   Diseñar y escribir el archivo `docker-compose.yml`.
    -   Debe definir los tres servicios de base de datos principales: `postgres`, `mongodb`, y `redis`.
    -   Configurar la red (`networks`) para que los servicios se comuniquen entre sí y con el servicio de la aplicación principal (`app`).
    -   Implementar volúmenes (`volumes`) para garantizar la persistencia de los datos de PostgreSQL y MongoDB entre reinicios del contenedor.
    -   Gestionar la configuración y las credenciales (usuarios, contraseñas, nombres de BD) de forma segura utilizando un archivo `.env` y la sección `environment` en `docker-compose.yml`.

3.  **Lógica de Conexión:**
    -   Implementar la lógica en `database/connection.py` para establecer y gestionar las sesiones de SQLAlchemy (`get_db`) y las conexiones a MongoDB (`get_mongo`) y Redis, leyendo la configuración desde las variables de entorno.

### 2.2. El Cerebro: `CoordinadorCentral` y `TransactionManager`

**Tarea:** Implementar el orquestador central para manejar flujos de negocio complejos de forma síncrona y transaccional.

**Investigación Requerida:**
1.  **Diseño e Implementación del `CoordinadorCentral`:**
    -   Basado en la documentación (`arquitectura_sistema_dianabot.md` y `fases_evolución/`), implementar la clase `CoordinadorCentral` en `core/coordinator.py`.
    -   Definir e implementar los métodos para las operaciones críticas documentadas: `TOMAR_DECISION`, `COMPRAR_ITEM`, `ACCEDER_NARRATIVA_VIP`, `REACCIONAR_CONTENIDO`.
    -   Cada método debe encapsular un flujo de negocio completo, llamando a los diferentes servicios de los módulos (`modules/`) en la secuencia correcta.

2.  **Gestión de Transacciones Distribuidas:**
    -   Implementar la clase `TransactionManager` en `core/transaction_manager.py`.
    -   Debe soportar un patrón `with transaction.atomic()` que asegure que todas las operaciones dentro de un flujo del coordinador se completen con éxito o se reviertan por completo (rollback) si alguna falla.
    -   Diseñar un mecanismo para que cada servicio (ej. `BesitosService`) pueda registrar una operación de compensación (rollback) cuando es ejecutado dentro de una transacción.

3.  **Refactorización de Handlers:**
    -   Analizar todos los archivos en `bot/handlers/`.
    -   Modificar cada handler para que, en lugar de contener lógica de negocio, simplemente extraiga los datos del `update` de Telegram y delegue la acción al método correspondiente del `CoordinadorCentral`.
    -   El handler solo debe recibir el resultado del coordinador y presentarlo al usuario.

### 2.3. El Sistema Nervioso: `EventBus` Asíncrono

**Tarea:** Implementar el sistema de comunicación asíncrona para desacoplar los módulos.

**Investigación Requerida:**
1.  **Implementación del `EventBus`:**
    -   Desarrollar la clase `EventBus` en `core/event_bus.py` utilizando `redis` Pub/Sub.
    -   Implementar los métodos `publish(event_type, event_data)` y `subscribe(event_type, handler_func)`.
    -   Definir una estructura estándar para los payloads de los eventos (ej. `{ 'timestamp': ..., 'source_module': ..., 'data': {...} }`).

2.  **Registro y Manejo de Eventos:**
    -   Implementar un registro central de manejadores de eventos en `core/event_handlers.py`.
    -   Este archivo debe importar los módulos que necesitan reaccionar a eventos y suscribir sus funciones al `EventBus`.
    -   Asegurar que el `EventBus` se inicie en un hilo separado en `bot/main.py` para escuchar eventos sin bloquear el bot.

3.  **Integración en Módulos:**
    -   Identificar los puntos en la lógica de los servicios (`modules/`) donde se deben emitir eventos. Por ejemplo, después de que `BesitosService` otorga puntos, debe publicar el evento `gamification.besitos_earned`.
    -   Identificar qué módulos deben reaccionar a qué eventos (ej. el módulo de `achievements` debe suscribirse a `gamification.besitos_earned` para verificar si se desbloquea un logro).

### 2.4. Completitud de los Módulos de Negocio

**Tarea:** Desarrollar la lógica de negocio faltante en los módulos, utilizando los modelos de datos y componentes de integración ya creados.

**Investigación Requerida:**
1.  **Módulo de Comercio (`modules/commerce/`):**
    -   Implementar la lógica en `shop.py`, `checkout.py`, y `unlocks.py` para interactuar con los modelos `ShopItem` y `UserPurchase`.
    -   Desarrollar el `ArchetypeEngine` para la personalización.

2.  **Módulo de Gamificación (`modules/gamification/`):**
    -   Completar la implementación de `missions.py`, `achievements.py`, y `auctions.py`, conectándolos a sus respectivos modelos de base de datos.

3.  **Módulo de Experiencias (`modules/experiences/`):**
    -   Este es el módulo más complejo y novedoso. Diseñar e implementar el `ExperienceEngine` y el `CompositeValidator` basándose en la extensa documentación de `fases_evolución/fase_4.md`. Debe ser capaz de gestionar flujos que combinan componentes de todos los demás módulos.

---

## 3. Metodología de Implementación Sugerida (Plan por Fases)

Se propone un enfoque incremental para abordar esta compleja tarea.

-   **Fase 1: Cimientos (Foundation).**
    1.  Implementar los modelos de datos en `database/models.py` a partir de las migraciones.
    2.  Implementar `docker-compose.yml` y la conexión a las bases de datos.
    3.  Poblar la base de datos con datos de prueba (`seeds`). En este punto, el sistema debería poder iniciarse y conectarse a las BBDD.

-   **Fase 2: Implementación del Núcleo de Integración.**
    1.  Desarrollar el `EventBus` en `core/event_bus.py`.
    2.  Desarrollar el `TransactionManager` y el `CoordinadorCentral` en `core/`.

-   **Fase 3: Refactorización y Conexión.**
    1.  Refactorizar un flujo simple (ej. `/balance`) para que el handler llame al `CoordinadorCentral` en lugar de al servicio directamente.
    2.  Integrar la publicación de un evento simple (ej. `user.command_executed`) y un suscriptor que lo registre (log).

-   **Fase 4: Desarrollo de la Lógica de Negocio.**
    1.  Completar la implementación de los servicios en los `modules/`, ahora que los modelos de BD y el núcleo de integración existen.

-   **Fase 5: Integración Completa y Pruebas.**
    1.  Refactorizar todos los handlers para usar exclusivamente el `CoordinadorCentral`.
    2.  Integrar la publicación y suscripción de todos los eventos documentados.
    3.  Desarrollar pruebas de integración (`pytest`) que verifiquen los flujos completos a través del coordinador y el bus de eventos.

---

## 4. Entregables Esperados

El resultado final de esta investigación y desarrollo debe ser un conjunto de cambios en el código que produzcan:

1.  Un archivo `database/models.py` completo y funcional.
2.  Un archivo `docker-compose.yml` que levante toda la infraestructura de servicios.
3.  Clases `CoordinadorCentral` y `EventBus` completamente implementadas y funcionales.
4.  Handlers en `bot/handlers/` refactorizados para usar el `CoordinadorCentral`.
5.  Módulos de negocio en `modules/` con su lógica de servicio completa.
6.  Un sistema que se comporte como se describe en la documentación conceptual, con flujos de datos y comunicación entre módulos claramente establecidos.
7.  Una versión actualizada del documento `docs/estructura.md` que ahora sí refleje fielmente la arquitectura implementada.
