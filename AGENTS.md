# Workflow del Agente - DianaBot

You are a task implementation specialist this workflow.

Actualmente estamos trabajando en la evolución de un sistema bot de Telegram en donde ya hay una base que hay que mejorar con estas frases que estamos implementando

## Your Role
You are responsible for implementing a single, specific task from a specification's tasks.md file. You must:
1. Focus ONLY on the assigned task - do not implement other tasks
2. Follow existing code patterns and conventions meticulously
3. Leverage existing code and components whenever possible
4. Write clean, maintainable, tested code
5. Mark the task as complete in TODO_EVOLUTION.md 


## Proceso de Implementación de Fases

### Workflow Consistente

1. **Ejecutar Fase Actual**: - Antes de escribir cualquier línea de código analizar lo solicitado en la fase y planifica creando un TODO con tareas atómicas que no toquen más de tres archivos y no lleven más de 30 minutos en su implementación
   - Implementar lo solicitado en la fase correspondiente tarea por tarea 
   - Seguir las especificaciones detalladas en `docs/fases_evolución/`

2. **Al Término de Cada Fase**:
   - Realizar un commit resumiendo lo implementado en esa fase
   - Hacer push a remoto
   - Marcar la fase como completada en `TODO_EVOLUTION.md` agregando una línea: "Fase X completada"
   - Realíza tests con datos reales utiliza mocks únicamente con servicios que no dependan de nosotros
   - Si hay problemas con los test no simplifiques el test verifica cuál es el error y solucionarlo para poder ejecutar tu test
   - Al término de la face te enviaré  una revisión en donde posiblemente se encuentren algunos detalles que tendrás que corregir
3. **Estructura de Fases**:
   - Las fases están divididas por archivos en `docs/fases_evolución/`
   - Cada archivo contiene el detalle específico de lo que se necesita implementar Y en la parte inferior los apartados completos del documento de investigación a los que hace referencia cada fase para que los puedas consultar directamente ahí sin tener que leer todo el documento de investigación
   - El orden numérico de los archivos indica la secuencia de fasesj

### Archivos de Referencia

- **fases_evolución**: `docs/fases_evolución/fase_*.md` - Especificaciones detalladas de cada fase
- **Progreso**: `TODO_EVOLUTION.md` - Tracking de fases completadas
- **Este Workflow**: `AGENTS.md` - Proceso consistente para el agente

### Comportamiento del Agente

- **Inicio de Sesión**: Verificar `TODO_EVOLUTION.md` para determinar la fase actual
- **Durante la Sesión**: Implementar completamente la fase actual
- **Finalización**: Commit, actualizar `TODO_EVOLUTION.md`, pasar a siguiente fase automáticamente
- **Recuperación**: Si se pierde conexión, retomar desde la fase indicada en `TODO_EVOLUTION.md`

