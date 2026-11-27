# Telemonitoreo híbrido de pacientes con nodos ESP32 en tiempo real y control remoto de oxigenoterapia

**Instituto Tecnológico de Costa Rica — Escuela de Ingeniería Electrónica**
Taller de Sistemas Embebidos · II Semestre 2026 · III Proyecto: *Sistemas Embebidos para aplicaciones EDGE to Cloud*

| Integrante | Rol |
|---|---|
| Daniel Chavarría | Rol A — Edge y FreeRTOS |
| Saúl Quesada | Rol B — Conectividad y Nube |

---

## 1. Descripción

Sistema IoT *Edge-to-Cloud* para el telemonitoreo de signos vitales (frecuencia cardíaca, SpO₂ y temperatura corporal) de pacientes en zonas rurales de Costa Rica. Cada paciente es un nodo ESP32 gobernado por **FreeRTOS** que muestrea sus variables de forma determinista, ejecuta control local de una **válvula de oxigenoterapia simulada** y sincroniza telemetría y comandos remotos (RPC) con **ThingsBoard** mediante **MQTT**.

El enfoque es **híbrido**:

- **Nodo 1 — Paciente real:** sensores físicos sobre una persona (MAX30102 y MLX90614).
- **Nodo 2 — Paciente emulado:** señales generadas en laboratorio (generador de señal y potenciómetros), lo que permite provocar de forma reproducible eventos críticos como desaturación de SpO₂, taquicardia o fiebre.

### Alineación con los ODS

- **ODS 3 — Salud y bienestar**, meta **3.8**: lograr la cobertura sanitaria universal y el acceso a servicios de salud esenciales de calidad.
- **Problema:** poblaciones rurales y adultos mayores alejados de un EBAIS u hospital no cuentan con seguimiento continuo de sus signos vitales; las descompensaciones se detectan tarde.
- **Aporte:** monitoreo remoto en tiempo real, alarmas automáticas y actuación remota sobre la oxigenoterapia, con operación local garantizada aunque se pierda la conexión a internet.

---

## 2. Arquitectura del sistema

```
 ┌──────────────── Nodo 1: Paciente real ────────────────┐
 │ MAX30102 (FC, SpO₂) ─┐                                │
 │ MLX90614 (Temp)  ────┼── I2C (mtx_i2c) ── ESP32 ──────┼──┐
 │ OLED SSD1306  ───────┘           │                    │  │
 │ Servo SG90 + final de carrera (válvula O₂)            │  │
 └───────────────────────────────────────────────────────┘  │   Wi-Fi / MQTT
                                                            ├──────────────► ThingsBoard
 ┌─────────────── Nodo 2: Paciente emulado ──────────────┐  │   (telemetría JSON,
 │ Generador de señal (pulso 1–2 Hz) ── ADC1             │  │    RPC, alarmas,
 │ Potenciómetro SpO₂  ───────────────── ADC1 ── ESP32 ──┼──┘    dashboard)
 │ Potenciómetro Temp  ───────────────── ADC1            │
 │ Servo SG90 + final de carrera (válvula O₂)            │
 └───────────────────────────────────────────────────────┘
```

Ambos nodos comparten **el mismo firmware**; el modo se selecciona en compilación (`REAL` o `EMULADO`).

### Telemetría (JSON publicado por MQTT)

```json
{ "fc": 78, "spo2": 97, "temp": 36.7, "valvula": 0, "valvula_fb": 0 }
```

### Comandos RPC desde ThingsBoard

| Método | Parámetro | Efecto |
|---|---|---|
| `setValvula` | `true` / `false` | Abre o cierra la válvula de O₂ |
| `setUmbralSpO2` | entero (%) | Cambia el umbral de apertura automática |

### Regla de alarma

Alarma crítica en ThingsBoard cuando **SpO₂ < 90 %**, **temperatura > 38 °C** o **FC fuera de 50–120 lpm**.

---

## 3. Arquitectura de software (FreeRTOS)

| Tarea | Prioridad | Núcleo | Función |
|---|---|---|---|
| **A — Muestreo** | 5 (alta) | 1 | Lectura periódica determinista de sensores (I2C o ADC1) y procesamiento local; envía a `q_telemetria` |
| **B — Control** | 4 | 1 | Evalúa umbrales y comandos de `q_comandos`; acciona el servo y lee la retroalimentación del final de carrera |
| **D — Interfaz local** | 3 | 1 | Muestra signos vitales y estado de la válvula en la OLED (log serie en el nodo 2) |
| **C — Comunicaciones** | 2 | 0 | Wi-Fi, MQTT, reconexión asíncrona y buffer de telemetría durante desconexiones |
| **E — Supervisor** | 1 (baja) | 0 | Watchdog, memoria libre y pilas (`uxTaskGetStackHighWaterMark`); métricas para el artículo |

**Mecanismos de sincronización**

- `q_telemetria`: cola A → C con la telemetría procesada.
- `q_comandos`: cola C → B con los comandos RPC.
- `mb_vitales` y `mb_actuador`: buzones (colas de longitud 1) con el dato más reciente para B, C y D.
- `mtx_i2c`: mutex que protege el bus I2C compartido por MAX30102, MLX90614 y OLED (con herencia de prioridad).
- `eg_red`: event group con los bits `WIFI_OK` y `MQTT_OK` para la reconexión asíncrona.

El detalle completo está en [`docs/diagramas/freertos.svg`](docs/diagramas/freertos.svg).

**Tolerancia a fallos de red:** reconexión a Wi-Fi y al broker por eventos, sin bucles `while(!connected)`. Durante la desconexión, las tareas A y B siguen ejecutándose y la tarea C almacena la telemetría para reenviarla al recuperar la red.

---

## 4. Roles y responsabilidades

### Rol A — Edge y FreeRTOS · *Daniel Chavarría*

- Tareas **A** (muestreo), **B** (control), **D** (interfaz local) y **E** (supervisor).
- Drivers: bus I2C con mutex, MAX30102, MLX90614, OLED, servo y final de carrera.
- Montaje y pruebas del **Nodo 1 (paciente real)**.
- Diagramas SysML **BDD** e **IBD** y diagrama de arquitectura de FreeRTOS.
- Medición de tiempos de ejecución y periodicidad de la tarea A.

### Rol B — Conectividad y Nube · *Saúl Quesada*

- Tarea **C** (Wi-Fi, MQTT, reconexión asíncrona y buffer offline).
- ThingsBoard: dispositivos, dashboard, widget RPC y cadena de reglas con alarmas.
- Montaje y pruebas del **Nodo 2 (paciente emulado)** con generador de señal y potenciómetros.
- Justificación ODS, casos de uso y **ConOps**.
- Medición de latencia de telemetría y de respuesta RPC.

### Responsabilidades compartidas

- Integración del firmware común y del repositorio.
- Matriz de trazabilidad de requerimientos.
- Pruebas de resiliencia (desconexión del router durante 30 s).
- Artículo científico IEEE.
- **Ambos integrantes deben dominar todo el código** para la defensa oral.

---

## 5. Hardware

| Componente | Cantidad | Nodo |
|---|---|---|
| ESP32 DevKit (ESP-WROOM-32, Xtensa LX6 doble núcleo) | 2 | 1 y 2 |
| Sensor MAX30102 (FC y SpO₂) | 1 | 1 |
| Sensor MLX90614 (temperatura IR) | 1 | 1 |
| Pantalla OLED SSD1306 0.96" I2C | 1–2 | 1 (opcional en 2) |
| Servo SG90 | 2 | 1 y 2 |
| Final de carrera (microswitch) | 2 | 1 y 2 |
| Potenciómetro 10 kΩ | 2 | 2 |
| Resistencias 1 kΩ, protoboards, cables | — | 1 y 2 |
| Generador de señal (laboratorio) | 1 | 2 |

> Las señales emuladas se conectan al **ADC1 (GPIO32–39)**, ya que el ADC2 no está disponible con el Wi-Fi activo. Con atenuación de 12 dB el rango útil es de ~0.15 a 2.45 V: el generador usa offset de 1.3 V y amplitud pico ≤ 1.0 V, y cada potenciómetro lleva una resistencia de 3.3 kΩ en serie hacia 3.3 V. Ver [`docs/diagramas/ibd_nodo_emulado.svg`](docs/diagramas/ibd_nodo_emulado.svg).

---

## 6. Documentación de diseño (E1)

| Documento | Contenido |
|---|---|
| [Justificación ODS](docs/ods.md) | Problema en Costa Rica, ODS 3 meta 3.8 y referencias |
| [Matriz de requerimientos](docs/requerimientos.md) | Requerimientos funcionales y no funcionales con su verificación |
| [Casos de uso](docs/diagramas/casos_de_uso.svg) · [ConOps](docs/diagramas/conops.svg) | Modelado del comportamiento |
| [BDD](docs/diagramas/bdd.svg) · [IBD nodo real](docs/diagramas/ibd_nodo_real.svg) · [IBD nodo emulado](docs/diagramas/ibd_nodo_emulado.svg) | Modelado estructural SysML |
| [Arquitectura FreeRTOS](docs/diagramas/freertos.svg) | Tareas, prioridades, colas, mutex y núcleos |
| [Maqueta del dashboard](docs/dashboard/dashboard_maqueta.png) | Prototipo conceptual de ThingsBoard |

---

## 7. Estructura del repositorio

```
├── firmware/        # Proyecto ESP-IDF común a ambos nodos
├── thingsboard/     # Exportaciones del dashboard y cadena de reglas
├── docs/            # Material de diseño E1 (ver docs/README.md)
│   ├── ods.md
│   ├── requerimientos.md
│   ├── diagramas/   # Casos de uso, ConOps, BDD, IBD, FreeRTOS (SVG + PNG + fuentes)
│   └── dashboard/   # Maqueta del dashboard de ThingsBoard
├── paper/           # Artículo IEEE (E3)
└── README.md
```

---

## 8. Compilación y carga

Requisitos: **ESP-IDF v5.5** en Linux.

```bash
get_idf
cd firmware
idf.py set-target esp32
idf.py menuconfig        # Wi-Fi, token de ThingsBoard y modo REAL/EMULADO
idf.py build
idf.py -p /dev/ttyUSB0 flash monitor
```

Salir del monitor: `Ctrl + ]`.

---

## 9. Cronograma

| Entregable | Fecha | Valor |
|---|---|---|
| **E1** — Propuesta y diseño de arquitectura | Semana 17 (23–28 nov.) | 5 % |
| **E2** — Demostración técnica y validación | Semana 18 (30 nov.–5 dic.) | 10 % |
| **E3** — Artículo científico IEEE | Semana 19 (7–10 dic.) | 5 % |

---

## 10. Avances por rol

### Daniel Chavarría — Rol A

| Fecha | Avance | Commit / evidencia |
|---|---|---|
| 26/11/2026 | Instalación de ESP-IDF v5.5 y prueba `hello_world` en ESP32 | — |
| 27/11/2026 | Material de diseño E1: ODS, requerimientos, diagramas SysML, FreeRTOS y maqueta del dashboard | `docs/` |

### Saúl Quesada — Rol B

| Fecha | Avance | Commit / evidencia |
|---|---|---|
| | | |

---

## 11. Trabajo futuro

El proyecto continuará como desarrollo personal después del curso. Líneas previstas:

- Migrar los nodos a una PCB propia y un formato portátil para el paciente.
- Control en lazo cerrado de la oxigenoterapia a partir de la SpO₂ medida.
- Escalar a múltiples pacientes por estación y comunicación directa entre nodos.
