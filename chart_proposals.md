# Propuestas de Visualización: 30 Gráficos de BI - GestObra

Este documento describe **30 gráficos y visualizaciones analíticas** que se pueden construir utilizando los datos operacionales de GestObra. Están organizados en áreas de negocio críticas para facilitar el control de obras, costos y la gestión de personal en campo.

---

## 📊 Área 1: Control Horario y Fichajes (Presencia)

### 1. Histórico Mensual de Horas Fichadas
*   **Tipo**: Gráfico de Líneas o Área.
*   **Objetivo**: Analizar la tendencia temporal del volumen total de horas laboradas.
*   **Dimensiones/Métricas**: Eje X: Mes/Año. Eje Y: Suma de `hours_worked` de `fact_time_clock`.

### 2.1. Distribución de Jornadas por X
*   **Tipo**: Gráfico de Pastel.
*   **Objetivo**: Identificar qué acumulan más horas en el mes actual.
*   **Dimensiones/Métricas**: Eje X: Suma de `hours_worked`. Eje Y: se puede escoger entre `person_name`, `specialty_name`, `project_name`.

### 3. Fichajes sin Salida Registrada (Alertas)
*   **Tipo**: Tarjeta de KPI + Lista de Alertas.
*   **Objetivo**: Mostrar en tiempo real cuántos registros de entrada carecen de hora de salida.
*   **Dimensiones/Métricas**: Conteo de filas de `time_clock_records` donde `exit_at` es NULL.

### 4. Puntualidad e Inicio de Jornada
*   **Tipo**: Gráfico de Dispersión (Scatter).
*   **Objetivo**: Evaluar la desviación de la hora de entrada real respecto al inicio de jornada oficial (`workday_start` de `teams`).
*   **Dimensiones/Métricas**: Eje X: Fecha. Eje Y: Diferencia en minutos entre `entry_at` y `workday_start`.

### 5. Tasa de Fichajes Corregidos Manualmente
*   **Tipo**: Gráfico de Torta (Pie).
*   **Objetivo**: Controlar la necesidad de corrección por olvidos de los operarios.
*   **Dimensiones/Métricas**: Fichajes normales vs Fichajes registrados en `time_clock_corrections`.

### 6. Ausentismo y Motivos de Baja
*   **Tipo**: Gráfico de Donut (Dona).
*   **Objetivo**: Visualizar las causas principales de inactividad de la plantilla.
*   **Dimensiones/Métricas**: Agrupado por `reason` de `person_absences`. Métrica: Días acumulados de ausencia.

### 7. Mapa de Calor de Fichajes (Días y Horas)
*   **Tipo**: Mapa de Calor (Heatmap).
*   **Objetivo**: Conocer los momentos de mayor afluencia de entradas y salidas de trabajadores.
*   **Dimensiones/Métricas**: Eje X: Día de la semana. Eje Y: Hora del día. Color: Volumen de registros.

---

## 📈 Área 2: Productividad, Obras y Desviaciones

### 8. Avance Físico de Obra vs Costo Acumulado
*   **Tipo**: Gráfico de Eje Y Doble (Línea + Barras).
*   **Objetivo**: Visualizar si el ritmo de gasto de personal acompaña al progreso real de la obra.
*   **Dimensiones/Métricas**: Eje X: Tiempo. Eje Y izquierdo: % de tareas completadas de `tasks`. Eje Y derecho: Costo total de `fact_project_imputation`.

### 9. Presupuesto de Mano de Obra vs Costo Real
*   **Tipo**: Gráfico de Barras Agrupadas.
*   **Objetivo**: Detectar desviaciones económicas de mano de obra en cada proyecto.
*   **Dimensiones/Métricas**: Eje X: Proyecto (`dim_project.name`). Eje Y: `budget` vs `calculated_labor_cost`.

### 10. Distribución del Costo de Obra por Categoría Profesional
*   **Tipo**: Gráfico de Torta (Pie).
*   **Objetivo**: Analizar en qué perfiles (Peón, Oficial, Encargado) se invierte el presupuesto.
*   **Dimensiones/Métricas**: Agrupado por `cargo_name` de `dim_person`. Métrica: Suma de `calculated_cost`.

### 11. Pareto de Horas Imputadas por Proyecto
*   **Tipo**: Gráfico de Barras con Línea Acumulativa (Pareto).
*   **Objetivo**: Identificar el 20% de las obras que consumen el 80% de los recursos de personal.
*   **Dimensiones/Métricas**: Eje X: Proyectos ordenados por costo de mayor a menor. Línea: Porcentaje acumulado de horas.

### 12. Eficiencia de Cierre de Tareas (Lead Time)
*   **Tipo**: Gráfico de Barras.
*   **Objetivo**: Medir el promedio de días que toma completar tareas desde su creación.
*   **Dimensiones/Métricas**: Eje X: Tipo de especialidad. Eje Y: Promedio de `completed_at - created_at` en días.

### 13. Tasa de Aprobación de Tareas
*   **Tipo**: Indicador de Aguja (Gauge Chart).
*   **Objetivo**: Monitorear el porcentaje de tareas completadas que ya han sido validadas por los encargados.
*   **Dimensiones/Métricas**: Tareas aprobadas vs Tareas en espera de aprobación de `teams.require_task_approval`.

### 14. Relación Horas Fichadas vs Imputadas
*   **Tipo**: Gráfico de Dispersión (Scatter Plot).
*   **Objetivo**: Evaluar la precisión de los operarios al registrar a qué obra dedican su jornada.
*   **Dimensiones/Métricas**: Cada punto es un operario. Eje X: Horas fichadas. Eje Y: Horas imputadas a proyectos.

### 15. Control de Hitos de Obra
*   **Tipo**: Diagrama de Gantt / Cronograma de Hitos.
*   **Objetivo**: Visualizar las fechas de hitos clave previstos vs reales.
*   **Dimensiones/Métricas**: Eje X: Tiempo. Filas: Proyectos. Hitos: Estados de `milestones`.

---

## 💬 Área 3: Eficiencia de Canales de Reporte (WhatsApp)

### 16. Volumen Diario de Mensajes al Bot
*   **Tipo**: Gráfico de Área.
*   **Objetivo**: Medir la adopción y el uso del bot de WhatsApp a lo largo del tiempo.
*   **Dimensiones/Métricas**: Eje X: Fecha. Eje Y: Conteo de registros en `whatsapp_action_log`.

### 17. Tipo de Reporte de Campo (WhatsApp)
*   **Tipo**: Gráfico de Torta o Donut.
*   **Objetivo**: Conocer el formato preferido por los operarios para reportar (texto, audio o fotos).
*   **Dimensiones/Métricas**: Mensajes de texto vs `voice_inputs` vs `whatsapp_media_inputs` (`media_kind`).

### 18. Duración Media de Partes de Voz
*   **Tipo**: Histograma.
*   **Objetivo**: Evaluar si los partes de voz son concisos o extensos.
*   **Dimensiones/Métricas**: Eje X: Rangos de duración en segundos (de `media_duration_ms`). Eje Y: Frecuencia de partes de voz.

### 19. Tasa de Transcripciones Exitosas de Audio
*   **Tipo**: Gráfico de Barras Apiladas.
*   **Objetivo**: Analizar la efectividad del motor de IA al transcribir audios de obra.
*   **Dimensiones/Métricas**: Conteo por `transcript_status` (success, failed, processing) de `voice_inputs`.

### 20. Errores del Webhook del Bot de WhatsApp
*   **Tipo**: Gráfico de Líneas.
*   **Objetivo**: Detectar caídas del servicio o fallos técnicos en la comunicación con WhatsApp.
*   **Dimensiones/Métricas**: Conteo diario de `last_error` en la tabla `whatsapp_inbound_messages`.

### 21. Ranking de Operarios por Uso del Bot
*   **Tipo**: Gráfico de Barras Horizontales.
*   **Objetivo**: Identificar operarios que no están reportando activamente por el bot.
*   **Dimensiones/Métricas**: Eje X: Cantidad de reportes enviados. Eje Y: Nombre del operario.

### 22. Fotos y Evidencias de Obra por Proyecto
*   **Tipo**: Gráfico de Barras.
*   **Objetivo**: Monitorear en qué proyectos se están registrando más evidencias visuales.
*   **Dimensiones/Métricas**: Eje X: Proyecto. Eje Y: Cantidad de imágenes subidas (`media_kind = 'IMAGE'`).

---

## 🚜 Área 4: Recursos, Materiales y Logística

### 23. Tasa de Uso de Vehículos de la Empresa
*   **Tipo**: Gráfico de Barras.
*   **Objetivo**: Medir qué vehículos están activos y cuáles están subutilizados.
*   **Dimensiones/Métricas**: Eje X: Vehículo (`vehicles.license_plate`). Eje Y: % de días asignados en `project_schedule_resource`.

### 24. Costo Diario Acumulado de Flota (Vehículos)
*   **Tipo**: Gráfico de Área Apilada.
*   **Objetivo**: Analizar el costo total imputado por el uso de vehículos en obras.
*   **Dimensiones/Métricas**: Eje X: Fecha. Eje Y: Suma de `daily_rate` de los vehículos activos.

### 25. Herramientas Asignadas sin Devolución
*   **Tipo**: Tabla de Inventario BI.
*   **Objetivo**: Listar herramientas de alto valor asignadas a operarios que no han sido devueltas.
*   **Dimensiones/Métricas**: Herramientas (`tools`) activas cruzadas con el último operario asignado en tareas.

### 26. Consumo de Accesorios por Proyecto
*   **Tipo**: Gráfico de Torta (Pie).
*   **Objetivo**: Identificar los materiales de consumo más demandados en las obras.
*   **Dimensiones/Métricas**: Agrupado por `accessories.name`. Métrica: Suma de `quantity` de `vehicle_accessories`.

### 27. Uso de Maquinaria y Recursos Críticos por Obra
*   **Tipo**: Diagrama de Cuerdas (Chord Diagram) o Sankey.
*   **Objetivo**: Visualizar el flujo de asignación de recursos materiales entre proyectos.
*   **Dimensiones/Métricas**: Origen: Recursos (tipo máquina). Destino: Proyectos. Ancho: Horas imputadas.

### 28. Capacidad Operativa vs Asignación
*   **Tipo**: Gráfico de Área Comparativo.
*   **Objetivo**: Comparar la capacidad máxima diaria en minutos vs la programada en tareas.
*   **Dimensiones/Métricas**: Eje X: Fecha. Eje Y: `daily_capacity_minutes` (capacidad) vs `shift_minutes` (planificado).

### 29. Especialidades más Requeridas en Tareas
*   **Tipo**: Gráfico de Barras.
*   **Objetivo**: Conocer qué especialidades técnicas se planifican más en los proyectos.
*   **Dimensiones/Métricas**: Eje X: Especialidad (`specialties.name`). Eje Y: Conteo de tareas asignadas.

### 30. Tareas Críticas Retrasadas por Obra
*   **Tipo**: Tarjeta de KPI Dinámica.
*   **Objetivo**: Mostrar el número total de tareas marcadas con prioridad 'Alta' o 'Crítica' que han superado su fecha de entrega.
*   **Dimensiones/Métricas**: Conteo de `tasks` donde `priority = 'CRITICAL'` y `completed_at` es mayor que la fecha límite.
