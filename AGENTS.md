# Workflow del Agente - DianaBot

## Proceso de Implementación de Fases

### Workflow Consistente

1. **Ejecutar Fase Actual**: 
   - Implementar lo solicitado en la fase correspondiente
   - Seguir las especificaciones detalladas en `docs/fases/`

2. **Al Término de Cada Fase**:
   - Realizar un commit resumiendo lo implementado en esa fase
   - Marcar la fase como completada en `TODO.md` agregando una línea: "Fase X completada"
   - Pasar automáticamente a la siguiente fase sin solicitar confirmación

3. **Estructura de Fases**:
   - Las fases están divididas por archivos en `docs/fases/`
   - Cada archivo contiene el detalle específico de lo que se necesita implementar
   - El orden numérico de los archivos indica la secuencia de fases

### Archivos de Referencia

- **Fases**: `docs/fases/fase_*.md` - Especificaciones detalladas de cada fase
- **Progreso**: `TODO.md` - Tracking de fases completadas
- **Este Workflow**: `AGENTS.md` - Proceso consistente para el agente

### Comportamiento del Agente

- **Inicio de Sesión**: Verificar `TODO.md` para determinar la fase actual
- **Durante la Sesión**: Implementar completamente la fase actual
- **Finalización**: Commit, actualizar `TODO.md`, pasar a siguiente fase automáticamente
- **Recuperación**: Si se pierde conexión, retomar desde la fase indicada en `TODO.md`

Este workflow asegura consistencia y continuidad en el desarrollo del proyecto DianaBot.