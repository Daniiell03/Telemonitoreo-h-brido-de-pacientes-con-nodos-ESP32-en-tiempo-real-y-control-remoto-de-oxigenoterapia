# Documentación — E1: Propuesta y diseño de arquitectura

Índice del material de diseño de la E1. Cada sección indica **qué es**, **por qué lo pide el instructivo** y **para qué se usa** en las etapas siguientes.

| # | Documento | Qué es | Por qué | Para qué |
|---|---|---|---|---|
| 1 | [`ods.md`](ods.md) | Problema nacional, ODS 3 (meta 3.8), población objetivo y referencias | Objetivo específico 1 y primer punto de la E1 | Introducción del artículo IEEE (E3) |
| 2 | [`requerimientos.md`](requerimientos.md) | Matriz de trazabilidad: 12 RF y 10 RNF con origen, implementación, prueba y responsable | Fase 2 de la metodología | Guion de pruebas para la E2 y sección de resultados del artículo |
| 3 | [`diagramas/casos_de_uso.svg`](diagramas/casos_de_uso.svg) | Actores (paciente, personal de salud) y 9 casos de uso | Fase 3: modelado del comportamiento | Delimitar el alcance del sistema |
| 4 | [`diagramas/conops.svg`](diagramas/conops.svg) | Flujo de datos de extremo a extremo, pasos ① a ⑫ | Fase 3: ConOps | Explicar el sistema completo en la exposición |
| 5 | [`diagramas/bdd.svg`](diagramas/bdd.svg) | SysML BDD: bloques, composición y especialización (nodo real / emulado) | Fase 4 y requisito explícito de la E1 | Descomposición física y lógica del hardware |
| 6 | [`diagramas/ibd_nodo_real.svg`](diagramas/ibd_nodo_real.svg) · [`ibd_nodo_emulado.svg`](diagramas/ibd_nodo_emulado.svg) | SysML IBD: conexiones, pines, buses y protocolos de cada nodo | Fase 4 y requisito explícito de la E1 | Guía de cableado para el montaje |
| 7 | [`diagramas/freertos.svg`](diagramas/freertos.svg) | Tareas con prioridad, núcleo, periodo, cómputo y pila; colas, buzones, mutex y event group | Fase 5 y requisito explícito de la E1 | Plano del firmware y base de la defensa oral |
| 8 | [`dashboard/dashboard_maqueta.png`](dashboard/dashboard_maqueta.png) | Prototipo conceptual del dashboard de ThingsBoard | Requisito explícito de la E1 | Guía para construir el dashboard real |

## Decisiones de diseño clave (para la defensa)

- **Tarea A fijada al núcleo 1:** la pila Wi-Fi y lwIP de ESP-IDF corre en el núcleo 0 con prioridades altas (18–23). Separar núcleos evita que las ráfagas de red afecten el periodo de 20 ms de la tarea A.
- **Colas en vez de variables globales:** `q_telemetria` (A → C) y `q_comandos` (C → B) cumplen el requisito obligatorio. Los buzones `mb_vitales` y `mb_actuador` (colas de longitud 1 con `xQueueOverwrite`/`xQueuePeek`) entregan siempre el dato más reciente sin bloquear al productor.
- **`xQueueSend` con timeout 0 en la tarea A:** si la cola se llena, la tarea A nunca se bloquea; el determinismo tiene prioridad sobre una muestra.
- **Mutex `mtx_i2c` con herencia de prioridad:** protege el bus que comparten MAX30102, MLX90614 y OLED. La tarea D escribe la OLED por páginas (~3 ms cada una) y libera el mutex entre páginas, lo que acota el bloqueo máximo de la tarea A a ~3 ms, por debajo de su periodo de 20 ms.
- **Reconexión por eventos (`eg_red`):** los manejadores de Wi-Fi y MQTT activan los bits `WIFI_OK` y `MQTT_OK`; la tarea C espera esos bits con timeout y nunca usa `while(!connected)`.
- **Buffer `rb_offline`:** durante la prueba de 30 s sin red, la tarea C guarda la telemetría (hasta 5 min) y la reenvía al reconectar, sin huecos en ThingsBoard.
- **Control local independiente de la nube:** la tarea B abre la válvula si la SpO₂ cae bajo el umbral aunque no haya conexión.

## Valores por confirmar en la implementación

Los tiempos de cómputo y tamaños de pila son **estimaciones de diseño**. Se reemplazarán por mediciones reales (osciloscopio en GPIO23, `uxTaskGetStackHighWaterMark`) antes de la E2. Los valores numéricos de la maqueta del dashboard son ilustrativos.

## Regenerar los diagramas

```bash
cd docs/diagramas/src
for f in *.dot; do dot -Tsvg "$f" -o "../${f%.dot}.svg"; dot -Tpng -Gdpi=150 "$f" -o "../${f%.dot}.png"; done
python3 gen_freertos_svg.py
```
