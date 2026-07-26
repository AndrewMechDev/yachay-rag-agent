# Plan de Continuidad de Negocio (BCP) — NovaTech Perú S.A.C.

**Código**: PLN-OPS-001  
**Versión**: 2.0  
**Vigencia**: Enero 2024  
**Área responsable**: Gerencia de Operaciones + Gerencia General  

---

## 1. Objetivo

Garantizar que NovaTech Perú pueda mantener sus operaciones críticas ante eventos disruptivos (desastres naturales, ciberataques, pandemias, fallas de infraestructura), minimizando el impacto en clientes, colaboradores y la continuidad financiera.

## 2. Alcance

Este plan cubre los procesos críticos de negocio identificados en las tres sedes (Lima, Arequipa, Trujillo) y los servicios de TI que los soportan.

## 3. Análisis de Impacto al Negocio (BIA)

### 3.1 Procesos críticos y tiempos de recuperación

| Proceso | Área | RTO (Recovery Time Objective) | RPO (Recovery Point Objective) | Impacto de interrupción |
|---|---|---|---|---|
| Facturación y cobranza | Finanzas | 4 horas | 1 hora | Pérdida de ingresos, incumplimiento tributario |
| Nómina y pago de haberes | RRHH | 8 horas | 4 horas | Incumplimiento laboral, malestar del personal |
| Atención al cliente | Operaciones | 2 horas | 30 minutos | Pérdida de clientes, daño reputacional |
| Plataforma de servicios digitales | Tecnología | 1 hora | 15 minutos | Incumplimiento de SLAs, penalidades contractuales |
| Correo electrónico corporativo | TI | 4 horas | 1 hora | Interrupción de comunicaciones |
| ERP (SAP) | TI | 4 horas | 1 hora | Paralización de operaciones administrativas |

### 3.2 Escenarios de riesgo

| Escenario | Probabilidad | Impacto | Prioridad |
|---|---|---|---|
| Terremoto (Perú = zona sísmica alta) | Alta | Muy alto | Crítica |
| Ciberataque (ransomware) | Alta | Muy alto | Crítica |
| Falla de centro de datos principal | Media | Alto | Alta |
| Pandemia / emergencia sanitaria | Media | Alto | Alta |
| Corte prolongado de energía eléctrica | Media | Medio | Media |
| Incendio en sede | Baja | Muy alto | Alta |
| Inundación | Baja | Medio | Media |

## 4. Estrategias de Continuidad

### 4.1 Infraestructura de TI
- **Centro de datos principal**: Lima (San Isidro), con UPS (autonomía 2 horas) y grupo electrógeno (autonomía 48 horas).
- **Centro de datos secundario (DR)**: Oracle Cloud Infrastructure (OCI), región São Paulo. Réplica de sistemas críticos con failover automático.
- **Backup**: Copias de seguridad diarias almacenadas en OCI Object Storage con retención de 90 días. RPO objetivo: 1 hora para sistemas críticos (replicación incremental).
- **Red**: enlace de internet principal (fibra óptica Movistar) + enlace secundario (Claro) con failover automático en todas las sedes.

### 4.2 Sede alterna
- En caso de inutilización de la sede principal (Lima), las operaciones se trasladan a la sede de Arequipa (capacidad para absorber 60% del personal crítico de Lima).
- Todo el personal no operativo trabaja de forma remota (laptops, VPN, Teams).
- Los servidores on-premise tienen réplica en OCI; el failover se activa en menos de 1 hora.

### 4.3 Comunicación de crisis
- **Árbol de llamadas**: cadena de contacto jerárquica (Gerencia General → Gerentes de área → Jefes → Colaboradores), activada por el Coordinador BCP.
- **Canal de emergencia**: grupo de WhatsApp "BCP NovaTech" (solo gerentes y coordinadores de área).
- **Comunicado externo**: a clientes y proveedores, emitido por Marketing y Legal dentro de las primeras 4 horas del evento.

## 5. Equipo de Gestión de Crisis

| Rol | Titular | Suplente | Teléfono de emergencia |
|---|---|---|---|
| Director de Crisis | Gerente General — Carlos Medina | Gerente de Operaciones — Diego Ramírez | 999-111-222 |
| Coordinador BCP | Jefe de TI — Roberto Cárdenas | Jefe de Infraestructura — Marcos Huanca | 999-333-444 |
| Comunicaciones | Jefe de Marketing — Lucía Fernández | Asistente de Gerencia — Paola Rivera | 999-555-666 |
| RRHH y Bienestar | Gerente de RRHH — Natalia Ochoa | Coordinadora de Bienestar — Sofía Pardo | 999-777-888 |
| Legal | Gerente Legal — Dr. César Vargas | Oficial de Cumplimiento — Dra. Ana Torres | 999-999-000 |

## 6. Procedimiento de Activación

### Nivel 1: Incidente de TI (sin activar BCP)
- Gestionado por el proceso de incidentes (GUI-OPS-001).
- No se activa el equipo de crisis.

### Nivel 2: Interrupción significativa (activación parcial del BCP)
- Se activa cuando un proceso crítico está interrumpido por más de 2 horas sin perspectiva de resolución inmediata.
- El Coordinador BCP convoca al equipo de crisis.
- Se evalúa la activación de la sede alterna y/o el failover a OCI.

### Nivel 3: Desastre mayor (activación total del BCP)
- Se activa cuando la sede principal queda inutilizada (terremoto, incendio, inundación).
- El Director de Crisis declara el estado de emergencia.
- Se ejecutan todos los planes: sede alterna, trabajo remoto, failover OCI, comunicación de crisis.

## 7. Pruebas y Actualización

- **Prueba de failover de TI**: semestral (simulación de caída de centro de datos y activación de DR en OCI).
- **Simulacro de evacuación**: anual en cada sede, coordinado con Defensa Civil.
- **Prueba de comunicación de crisis**: trimestral (activación del árbol de llamadas sin interrumpir operaciones).
- **Actualización del plan**: anual o cuando haya cambios significativos (nueva sede, nuevo sistema crítico, cambio organizacional).
- **Auditoría externa del BCP**: cada 2 años.

## 8. Contacto

Coordinador BCP: Roberto Cárdenas — rcardenas@novatech.pe — Ext. 3020 / Emergencia: 999-333-444
