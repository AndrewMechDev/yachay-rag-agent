# Guía de Gestión de Incidentes de TI — NovaTech Perú S.A.C.

**Código**: GUI-OPS-001  
**Versión**: 2.5  
**Vigencia**: Enero 2024  
**Área responsable**: Gerencia de Operaciones — Departamento de TI  
**Mesa de ayuda**: soporte@novatech.pe | Ext. 3000  

---

## 1. Definición de Incidente

Un incidente es cualquier evento no planificado que interrumpe o degrada un servicio de TI, afectando la operación normal de uno o más colaboradores. Ejemplos: caída de un sistema, lentitud extrema de la red, pérdida de acceso al correo, falla de hardware.

**No confundir con**:
- **Solicitud de servicio**: petición planificada (ej. "necesito una nueva cuenta de correo"). Se gestiona por el proceso de solicitudes, no de incidentes.
- **Problema**: causa raíz subyacente de uno o más incidentes recurrentes. Se gestiona por el proceso de gestión de problemas.

## 2. Clasificación de Severidad

| Nivel | Nombre | Descripción | Usuarios afectados | Ejemplo |
|---|---|---|---|---|
| **P1** | Crítico | Servicio principal caído sin workaround | >50% de usuarios o toda una sede | ERP SAP no accesible; servidor de correo caído |
| **P2** | Alto | Funcionalidad importante degradada, afecta un área completa | Un área o equipo completo (10-50 usuarios) | VPN corporativa intermitente; sistema de facturación lento |
| **P3** | Medio | Funcionalidad secundaria afectada, existe workaround | 1-10 usuarios | Impresora de un piso no funciona; aplicación específica con error |
| **P4** | Bajo | Impacto mínimo, inconveniente menor | 1 usuario | Teclado defectuoso; problema de configuración personal |

## 3. Tiempos de Respuesta y Resolución (SLA)

| Severidad | Tiempo de respuesta | Tiempo de resolución objetivo | Escalamiento automático |
|---|---|---|---|
| P1 | 15 minutos | 4 horas | A los 30 min: Jefe de TI. A la 1 hora: Gerente de Operaciones. A las 2 horas: Gerencia General |
| P2 | 30 minutos | 8 horas | A las 2 horas: Jefe de TI. A las 4 horas: Gerente de Operaciones |
| P3 | 2 horas | 24 horas | A las 8 horas: Jefe de TI |
| P4 | 8 horas | 72 horas | No aplica |

**Horario de cobertura**:
- Nivel 1 (Mesa de ayuda): Lunes a viernes, 7:00 a.m. a 8:00 p.m.
- Nivel 2 (Ingeniería): Lunes a viernes, 8:00 a.m. a 7:00 p.m.
- P1 (guardia): 24/7 (rotación semanal entre ingenieros senior).

## 4. Proceso de Atención

### 4.1 Reporte del incidente
El usuario reporta el incidente por cualquiera de estos canales:
1. **Mesa de ayuda telefónica**: Ext. 3000 (atención inmediata).
2. **Correo electrónico**: soporte@novatech.pe (tiempo de respuesta: según severidad).
3. **Portal de autoservicio**: https://soporte.novatech.pe (formulario con campos guiados).
4. **Microsoft Teams**: canal "Soporte TI" (para incidentes no urgentes).

### 4.2 Registro y clasificación
- La mesa de ayuda registra el incidente en ServiceNow (sistema ITSM) con: fecha/hora del reporte, nombre y área del usuario afectado, descripción del incidente, servicio/sistema afectado, severidad asignada, y número de ticket (formato INC-YYYYMMDD-XXXX).
- El usuario recibe confirmación automática por correo con el número de ticket.

### 4.3 Diagnóstico y resolución

**Nivel 1 — Mesa de ayuda (primera línea)**
- Intenta resolver el incidente con la base de conocimiento (KB) o procedimientos estándar.
- Si resuelve: documenta la solución, cierra el ticket, encuesta de satisfacción al usuario.
- Si no resuelve en 30 minutos: escala a Nivel 2.

**Nivel 2 — Ingeniería (segunda línea)**
- Especialistas por dominio (redes, servidores, aplicaciones, bases de datos, seguridad).
- Realiza diagnóstico profundo, acceso a logs, configuración avanzada.
- Si resuelve: documenta la solución, devuelve ticket a mesa de ayuda para cierre.
- Si no resuelve: escala a Nivel 3 o al proveedor externo.

**Nivel 3 — Arquitectura / Proveedores (tercera línea)**
- Arquitectos de TI o proveedor del sistema (Oracle, Microsoft, AWS, etc.).
- Intervención en código, infraestructura crítica, o parches del fabricante.

### 4.4 War room (solo P1)
Para incidentes P1, se convoca un war room:
- Participan: Jefe de TI, ingenieros asignados, gerente del área afectada.
- Se comunica un canal de Teams exclusivo para el incidente.
- Actualizaciones cada 30 minutos al Gerente de Operaciones y a los usuarios afectados.
- El war room permanece activo hasta la resolución.

## 5. Comunicación durante Incidentes

| Severidad | Comunicación al usuario | Frecuencia |
|---|---|---|
| P1 | Correo masivo + mensaje en Teams "Avisos TI" | Cada 30 minutos hasta la resolución |
| P2 | Correo al área afectada | Cada 2 horas |
| P3 | Actualizaciones en el ticket | Al resolver |
| P4 | Actualizaciones en el ticket | Al resolver |

## 6. Post-Mortem (Solo P1 y P2)

Todo incidente P1 y P2 requiere un informe post-mortem dentro de las **48 horas hábiles** posteriores a la resolución:

### 6.1 Contenido del informe
1. **Cronología detallada**: hora de inicio, detección, diagnóstico, resolución y cierre.
2. **Impacto**: número de usuarios afectados, sistemas impactados, duración total.
3. **Causa raíz**: análisis técnico de por qué ocurrió el incidente.
4. **Acciones correctivas**: qué se hizo para resolverlo.
5. **Acciones preventivas**: qué se va a hacer para que no vuelva a ocurrir (con responsable y plazo).
6. **Lecciones aprendidas**: qué funcionó bien y qué se puede mejorar en la gestión del incidente.

### 6.2 Revisión
- El informe es revisado por el Jefe de TI y el Gerente de Operaciones.
- Las acciones preventivas se registran como tareas en Jira con seguimiento semanal.
- Los post-mortem se archivan en la base de conocimiento para referencia futura.

## 7. Métricas y Reportes

| Métrica | Objetivo | Frecuencia de medición |
|---|---|---|
| Cumplimiento de SLA (tiempo de respuesta) | ≥ 95% | Mensual |
| Cumplimiento de SLA (tiempo de resolución) | ≥ 90% | Mensual |
| Tasa de resolución en primer contacto (Nivel 1) | ≥ 70% | Mensual |
| Satisfacción del usuario (encuesta post-cierre) | ≥ 4.0 / 5.0 | Mensual |
| Número de incidentes P1 | Tendencia a la baja | Trimestral |
| MTTR (Mean Time To Resolve) para P1 | ≤ 2 horas | Mensual |

## 8. Contacto

| Rol | Nombre | Correo | Extensión |
|---|---|---|---|
| Jefe de Mesa de Ayuda | Jorge Delgado | jdelgado@novatech.pe | 3010 |
| Jefe de Infraestructura TI | Roberto Cárdenas | rcardenas@novatech.pe | 3020 |
| Gerente de Operaciones | Ing. Diego Ramírez | dramirez@novatech.pe | 3100 |
