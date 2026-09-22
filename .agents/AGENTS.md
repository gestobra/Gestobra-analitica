# Reglas del Asistente para GestObra BI

Este archivo contiene las directrices, reglas y estándares obligatorios para el desarrollo y mantenimiento del módulo de Business Intelligence (BI) de GestObra.

---

## Directrices y Estándares del Proyecto

1. **Idioma de Comunicación y Documentación**:
   - La comunicación con el usuario y toda la documentación técnica (guías, README, agentes, propuestas) debe ser estrictamente en **Español**.
   - Los nombres de variables en el código Python y JavaScript deben mantener la consistencia con el esquema existente.

2. **Acceso y Seguridad de Datos**:
   - Las credenciales de acceso a PostgreSQL se leen exclusivamente del archivo `.env` en la raíz del proyecto.
   - **NUNCA** incluir credenciales en el código fuente, logs o confirmaciones de git.
   - Todas las consultas a la base de datos de producción deben ser de **solo lectura** (`SELECT`). Queda terminantemente prohibida cualquier modificación de esquema o mutación de datos en producción.
   - Para consultas de exploración, limitar siempre los resultados (`LIMIT 100`) para evitar bloqueos en la base de datos de producción.

3. **Arquitectura BI y Componentes Visuales**:
   - **Capa ETL/ELT**: Los scripts en Python (`src/etl_pipeline.py`) deben ser idempotentes, robustos frente a valores nulos o ausentes, y capaces de ejecutarse tanto en modo batch (archivos CSV) como en servidor dinámico (`src/server.py`).
   - **Gráficos e Interfaz (`output/dashboard.html`)**:
     - Todos los gráficos deben poseer un ID único en el elemento `<canvas>` y en su tarjeta contenedora (`card-{chartId}`).
     - Cada gráfico debe incluir un botón interactivo `🔍 Ver Consulta` que invoque el visor modal de consultas (`#query-modal`) mostrando la sentencia SQL PostgreSQL, la línea Pandas en Python, las tablas utilizadas y su descripción funcional.
     - Todos los filtros dinámicos (Cliente, Proyecto, Operario y el botón `Omitir Gestobra Dev`) deben propagarse correctamente a **todos** los 17 gráficos, las tarjetas KPI y las tablas.

4. **Calidad de Código y Verificación**:
   - El código en Python debe cumplir con el estándar **PEP 8** y utilizar tipado estático (*type hinting*).
   - Gestión segura de recursos: Utilizar siempre bloques `with` para la gestión de conexiones y punteros a bases de datos.
   - **Verificación Obligatoria**: Tras modificar scripts o componentes, se debe regenerar el dashboard (`python src/dashboard.py`) y validar empíricamente que la página HTML resultante compila sin errores sintácticos ni visuales.
