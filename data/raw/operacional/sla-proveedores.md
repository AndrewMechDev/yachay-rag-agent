# Acuerdos de Nivel de Servicio (SLA) con Proveedores — NovaTech Perú S.A.C.

**Código**: SLA-OPS-001  
**Versión**: 1.5  
**Vigencia**: Enero 2024  
**Área responsable**: Gerencia de Operaciones — Gestión de Proveedores  

---

## 1. Objetivo

Definir los estándares de servicio exigidos a los proveedores clave de NovaTech Perú para garantizar la calidad, disponibilidad y confiabilidad de los servicios contratados.

## 2. Proveedores Críticos y sus SLAs

### 2.1 Proveedor de internet — Movistar Empresas (enlace principal)

| Métrica | SLA contratado | Penalidad por incumplimiento |
|---|---|---|
| Disponibilidad del enlace | ≥ 99.5% mensual | Crédito del 5% de la factura mensual por cada 0.1% debajo del 99.5% |
| Latencia promedio | ≤ 30 ms | — |
| Tiempo de resolución de fallas | ≤ 4 horas para fallas críticas | — |
| Ancho de banda garantizado | 200 Mbps simétrico (80% garantizado) | Crédito proporcional si cae debajo del 80% |

### 2.2 Proveedor de internet backup — Claro Empresas (enlace secundario)

| Métrica | SLA contratado |
|---|---|
| Disponibilidad | ≥ 99.0% mensual |
| Ancho de banda | 100 Mbps simétrico |
| Activación de failover | ≤ 60 segundos tras la caída del enlace principal |

### 2.3 Proveedor de cloud — Oracle Cloud Infrastructure (OCI)

| Métrica | SLA contratado | Referencia |
|---|---|---|
| Disponibilidad de Compute (VM) | ≥ 99.95% mensual | SLA oficial de OCI |
| Disponibilidad de Object Storage | ≥ 99.9% mensual | SLA oficial de OCI |
| Disponibilidad de Autonomous Database | ≥ 99.95% mensual | SLA oficial de OCI |
| Soporte técnico (severidad 1) | Respuesta en ≤ 15 minutos | Contrato de soporte Premier |

### 2.4 Servicio de limpieza — Limtek S.A.C.

| Métrica | SLA contratado | Penalidad |
|---|---|---|
| Frecuencia de limpieza (áreas comunes) | 2 veces al día (mañana y tarde) | Descuento de 5% de la factura mensual por cada incumplimiento documentado |
| Limpieza profunda | 1 vez por semana (fines de semana) | — |
| Reposición de suministros (jabón, papel, gel) | Misma jornada tras el reporte | — |
| Personal mínimo asignado | 3 personas por sede | — |

### 2.5 Servicio de vigilancia — Prosegur Perú

| Métrica | SLA contratado | Penalidad |
|---|---|---|
| Cobertura horaria | 24/7 (guardias en turnos de 12 horas) | Multa de S/ 500 por turno descubierto |
| Número de agentes por sede | Lima: 3 agentes. Arequipa: 2. Trujillo: 2 | Descuento proporcional por agente faltante |
| Rondas de vigilancia nocturna | Cada 2 horas con registro en bitácora | — |
| Respuesta ante alarma | ≤ 5 minutos | — |

### 2.6 Servicio de courier — Olva Courier

| Métrica | SLA contratado |
|---|---|
| Entrega Lima metropolitana (mismo día) | Recogida antes de 12:00 m. → entrega antes de 6:00 p.m. |
| Entrega nacional (ciudades principales) | 24-48 horas hábiles |
| Entrega nacional (otras ciudades) | 48-72 horas hábiles |
| Trazabilidad | Número de guía con tracking en tiempo real |
| Confirmación de entrega | Foto del cargo firmado dentro de 2 horas |

## 3. Proceso de Monitoreo

### 3.1 Medición
- Los SLAs se miden mensualmente con datos objetivos (reportes del proveedor, herramientas de monitoreo propias, registro de incidentes).
- Los resultados se consolidan en un dashboard de Power BI accesible para el Gerente de Operaciones.

### 3.2 Revisión trimestral
- Se realiza una reunión trimestral con cada proveedor crítico para revisar:
  - Cumplimiento de SLAs del período.
  - Incidentes ocurridos y su resolución.
  - Mejoras solicitadas y compromisos.
  - Forecast de necesidades futuras.
- Los proveedores con incumplimiento reiterado (3 meses consecutivos debajo del SLA) son escalados a evaluación por el Comité de Compras.

### 3.3 Evaluación anual
- Cada proveedor recibe una evaluación anual con los siguientes criterios:

| Criterio | Peso |
|---|---|
| Cumplimiento de SLAs | 40% |
| Calidad del servicio (encuesta interna) | 25% |
| Precio competitivo | 15% |
| Capacidad de respuesta ante incidentes | 15% |
| Innovación y mejora continua | 5% |

- Calificación mínima para renovación de contrato: 70/100.
- Proveedores con calificación inferior a 50/100 son reemplazados.

## 4. Penalidades Generales

- Las penalidades acumuladas en un mes no pueden exceder el 20% de la factura mensual del proveedor.
- Los créditos por penalidades se aplican en la siguiente factura.
- El proveedor puede presentar justificaciones documentadas para fuerza mayor (desastres naturales, huelgas nacionales) que excluyen la penalidad.

## 5. Contacto

Coordinadora de Gestión de Proveedores: Claudia Salinas — csainas@novatech.pe — Ext. 3050
