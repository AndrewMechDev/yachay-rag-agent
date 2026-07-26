# Política de Seguridad de la Información — NovaTech Perú S.A.C.

**Código**: POL-OPS-002  
**Versión**: 3.0  
**Vigencia**: Enero 2024  
**Referencia**: ISO/IEC 27001:2022, Ley 29733 (Protección de Datos Personales)  
**Área responsable**: Gerencia de Operaciones — Departamento de Seguridad TI  
**CISO (Chief Information Security Officer)**: Ing. Marcos Huanca — mhuanca@novatech.pe  

---

## 1. Objetivo

Proteger la confidencialidad, integridad y disponibilidad de la información de NovaTech Perú, sus clientes, colaboradores y proveedores, ante amenazas internas y externas.

## 2. Clasificación de la Información

| Nivel | Descripción | Ejemplos | Controles mínimos |
|---|---|---|---|
| **Pública** | Información que puede divulgarse libremente | Sitio web, folletos, comunicados de prensa | Ninguno especial |
| **Interna** | Información para uso interno de NovaTech | Organigramas, manuales de procesos, correos generales | Acceso solo a colaboradores |
| **Confidencial** | Información sensible del negocio | Contratos, datos financieros, estrategias comerciales | Acceso restringido por área + cifrado |
| **Estrictamente confidencial** | Información crítica de alto impacto | Datos personales sensibles, claves de acceso, propiedad intelectual, información de M&A | Acceso solo a autorizados nominalmente + cifrado + auditoría |

## 3. Control de Accesos

### 3.1 Principios
- **Mínimo privilegio**: cada usuario tiene acceso solo a la información y sistemas que necesita para su función.
- **Segregación de funciones**: ninguna persona debe controlar todas las etapas de un proceso crítico.
- **Revisión periódica**: los accesos se revisan trimestralmente por el jefe de cada área.

### 3.2 Gestión de cuentas
- Las cuentas de usuario se crean a solicitud de RRHH (proceso de onboarding) y se desactivan dentro de las **2 horas** siguientes al cese del colaborador.
- Contraseñas: mínimo 12 caracteres, al menos 1 mayúscula, 1 número y 1 carácter especial. Cambio obligatorio cada 90 días. No reutilizar las últimas 5 contraseñas.
- Autenticación multifactor (MFA) obligatoria para: VPN, acceso remoto, correo desde dispositivos externos, sistemas críticos (SAP, panel de administración).
- Bloqueo automático de cuenta tras 5 intentos fallidos (desbloqueo por mesa de ayuda o autogestionado vía MFA).

### 3.3 Acceso a visitantes
- Los visitantes reciben acceso temporal a la red Wi-Fi de invitados (aislada de la red corporativa).
- No se permite el acceso de visitantes a áreas restringidas (centro de datos, sala de servidores) sin acompañamiento de un colaborador autorizado.
- Todo visitante debe registrarse en recepción y portar credencial de visitante visible.

## 4. Seguridad de Dispositivos

### 4.1 Laptops y equipos corporativos
- Cifrado de disco completo (BitLocker en Windows, FileVault en Mac) obligatorio en todos los equipos portátiles.
- Antivirus/EDR (CrowdStrike Falcon) instalado y actualizado en todos los endpoints.
- Actualizaciones de seguridad del sistema operativo: aplicación dentro de los **7 días** siguientes a su publicación (críticas: 48 horas).
- Bloqueo automático de pantalla tras 5 minutos de inactividad.

### 4.2 Dispositivos móviles (BYOD)
- Los colaboradores pueden acceder al correo corporativo desde dispositivos personales bajo las siguientes condiciones:
  - Registro del dispositivo en Microsoft Intune (MDM).
  - PIN o biometría habilitada.
  - Capacidad de borrado remoto de datos corporativos en caso de pérdida o robo.
  - No hacer jailbreak/root al dispositivo.

### 4.3 Medios removibles
- El uso de memorias USB, discos externos y otros medios removibles requiere autorización del Jefe de TI.
- Los puertos USB están deshabilitados por defecto en los equipos corporativos; se habilitan solo con justificación aprobada.
- Los datos copiados a medios removibles deben cifrarse.

## 5. Seguridad de Red

### 5.1 Arquitectura
- Red corporativa segmentada en VLANs: oficinas, servidores, invitados, IoT.
- Firewall perimetral (Palo Alto Networks) con reglas de mínimo privilegio.
- Sistema de detección y prevención de intrusiones (IDS/IPS).
- Filtrado de contenido web (URLs maliciosas, phishing, malware).
- VPN obligatoria para todo acceso remoto a la red corporativa (Cisco AnyConnect).

### 5.2 Monitoreo
- Centro de operaciones de seguridad (SOC) tercerizado (servicio 24/7).
- Correlación de eventos de seguridad (SIEM) con alertas automáticas.
- Escaneo de vulnerabilidades mensual en la infraestructura expuesta a internet.
- Penetration testing anual realizado por un consultor externo independiente.

## 6. Respuesta a Incidentes de Seguridad

### 6.1 Clasificación
| Tipo | Ejemplos | Severidad |
|---|---|---|
| Malware/ransomware | Infección de endpoint o servidor | Crítica |
| Phishing exitoso | Colaborador ingresó credenciales en sitio falso | Alta |
| Fuga de datos | Información confidencial enviada a destinatario no autorizado | Crítica |
| Acceso no autorizado | Cuenta comprometida, acceso externo no legítimo | Alta |
| Denegación de servicio (DDoS) | Ataque que afecta disponibilidad de servicios | Alta |

### 6.2 Procedimiento de respuesta
1. **Detección**: el SOC, un colaborador, o un sistema automatizado detecta el incidente.
2. **Contención inmediata** (primeras 2 horas): aislar el equipo/red afectada, bloquear cuentas comprometidas, preservar evidencia digital.
3. **Notificación**: al CISO (dentro de 30 min), al Gerente de Operaciones (dentro de 1 hora), al Gerente General si es crítico.
4. **Investigación**: análisis forense, determinación del alcance, identificación de datos comprometidos.
5. **Erradicación**: eliminación de la amenaza (malware, acceso no autorizado).
6. **Recuperación**: restauración de sistemas y datos desde backups verificados.
7. **Post-incidente**: informe de lecciones aprendidas, actualización de controles.
8. **Notificación a la ANPDP**: dentro de 72 horas si involucra datos personales (conforme a Ley 29733).

## 7. Capacitación y Concienciación

- **Inducción de seguridad**: todo nuevo colaborador recibe una capacitación de 2 horas en su primera semana.
- **Campaña de phishing simulada**: trimestral. Los colaboradores que caen en la simulación reciben capacitación reforzada.
- **Cápsula informativa mensual**: correo con tips de seguridad, alertas de amenazas recientes, y recordatorios de políticas.
- **Semana de la Ciberseguridad**: evento anual con charlas, talleres prácticos y concursos.

## 8. Contacto

CISO: Ing. Marcos Huanca — mhuanca@novatech.pe — Ext. 3030  
Emergencias de seguridad (24/7): seguridad@novatech.pe + SOC: 01-500-1234
