# Definición del problema e impacto (ODS)

## ODS y meta seleccionados

- **ODS 3 — Salud y bienestar:** garantizar una vida sana y promover el bienestar de todos a todas las edades.
- **Meta 3.8:** lograr la cobertura sanitaria universal, incluido el acceso a servicios de salud esenciales de calidad.
- **Indicador asociado 3.8.1:** cobertura de los servicios de salud esenciales.

## Problema en Costa Rica

**1. Barreras geográficas de acceso al primer nivel de atención.**
El EBAIS es la puerta de entrada al sistema de salud de la CCSS. La Defensoría de los Habitantes (junio 2026) inspeccionó 40 EBAIS y 6 puestos de visita periódica de la Zona Sur y reportó que, en zonas rurales e indígenas, las personas deben caminar horas, viajar en lancha o motocicleta, o pagar transporte privado costoso para llegar a un EBAIS. Señala que la lejanía, la pobreza y la mala conectividad interrumpen la continuidad de los tratamientos y el **seguimiento de enfermedades crónicas**. Entre las comunidades con barreras extremas menciona Biolley, Salitre, Térraba, Sierpe y Alto Conte.

**2. Saturación del primer nivel.**
Según el Programa Estado de la Nación (2024), el país tiene 1 148 EBAIS que atienden en promedio unas 4 584 personas cada uno, un 15 % por encima del estándar de 4 000, y se requerirían unos 189 EBAIS adicionales. El déficit más alto está en Pérez Zeledón (13 equipos), Coronado (9) y Cartago (7).

**3. Envejecimiento acelerado y enfermedades crónicas.**
Las proyecciones del INEC indican que hacia 2050 cerca de 25 de cada 100 personas tendrán 65 años o más, aproximadamente el doble de la proporción actual. El envejecimiento se asocia con más hipertensión, enfermedad cardiovascular y diabetes, y las personas adultas mayores ya representan más de una quinta parte de los egresos hospitalarios de la CCSS.

**Síntesis:** una población cada vez mayor y con más enfermedades crónicas necesita seguimiento continuo, pero en las zonas rurales el acceso físico al EBAIS es difícil y los equipos están saturados. Las descompensaciones (desaturación de oxígeno, taquicardia, fiebre) se detectan tarde.

## Población objetivo

Personas adultas mayores y pacientes crónicos en zonas rurales alejadas de un EBAIS (por ejemplo, la Zona Sur y los cantones rurales de Cartago), que requieren oxigenoterapia o vigilancia de signos vitales en el hogar.

## Cómo lo mitiga la solución

| Necesidad | Aporte del sistema |
|---|---|
| Seguimiento continuo sin desplazarse | Telemetría en tiempo real de FC, SpO₂ y temperatura hacia ThingsBoard |
| Detección temprana | Alarmas automáticas por reglas (SpO₂ < 90 %, T > 38 °C, FC fuera de 50–120 lpm) |
| Respuesta remota | Control RPC de la válvula de oxigenoterapia y ajuste remoto del umbral |
| Conectividad rural inestable | Operación local determinista (FreeRTOS) y reenvío de datos al recuperar la red |
| Varios pacientes por equipo de salud | Arquitectura escalable: un dashboard para múltiples nodos |

## Alcance del prototipo

El prototipo es una prueba de concepto académica y **no es un dispositivo médico certificado**. El nodo emulado permite reproducir eventos críticos de forma controlada para validar el sistema.

## Referencias

1. Defensoría de los Habitantes de la República (2026). *Habitantes de la Zona Sur conviven con desigualdades en los EBAIS* (Comunicado 025, 9 de junio de 2026). https://www.dhr.go.cr/informacion_relevante/comunicados/2026/junio_comunicados/025_Habitantes_Zona_Sur_conviven_desigualdades_Ebais.pdf
2. Programa Estado de la Nación (2024), vía Delfino.cr. *PEN: país requiere 189 EBAIS adicionales*. https://delfino.cr/2024/11/pen-pais-requiere-189-ebais-adicionales
3. Teletica (26 de julio de 2026). *Costa Rica envejece a paso acelerado y enciende alarmas en la salud pública* (con datos del INEC y el Observatorio del Envejecimiento de la UCR). https://www.teletica.com/salud/costa-rica-envejece-a-paso-acelerado-y-enciende-alarmas-en-la-salud-publica_413877
4. Organización Mundial de la Salud. *UHC service coverage index (SDG 3.8.1)*. https://www.who.int/data/gho/data/indicators/indicator-details/GHO/uhc-index-of-service-coverage
