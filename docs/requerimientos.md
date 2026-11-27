# Matriz de trazabilidad de requerimientos

Cada requerimiento se vincula con su origen (instructivo o rúbrica), el elemento del diseño que lo implementa y la prueba con la que se verificará en la E2.

**Leyenda de origen:** INS = instructivo del III Proyecto · RUB = rúbrica E2 · ODS = necesidad del problema.
**Responsable:** A = Daniel Chavarría (Edge y FreeRTOS) · B = Saúl Quesada (Conectividad y Nube).

## Requerimientos funcionales

| ID | Requerimiento | Origen | Implementa | Verificación | Resp. |
|---|---|---|---|---|---|
| RF-01 | Medir FC y SpO₂ del paciente real con el MAX30102 | INS 3.A | Tarea A, nodo 1 | Comparar contra un oxímetro comercial (10 mediciones) | A |
| RF-02 | Medir temperatura corporal con el MLX90614 | INS 3.A | Tarea A, nodo 1 | Comparar contra un termómetro clínico | A |
| RF-03 | Adquirir señales emuladas de pulso, SpO₂ y temperatura por ADC1 | INS 3.A | Tarea A, nodo 2 | Barrido de frecuencia del generador (0.8–2.5 Hz) y de los potenciómetros | B |
| RF-04 | Publicar telemetría JSON por MQTT a ThingsBoard cada 1 s | INS 3.C | Tarea C | Revisar la serie de tiempo en ThingsBoard durante 10 min | B |
| RF-05 | Abrir y cerrar la válvula de O₂ por RPC (`setValvula`) | INS 3.C, RUB | Tarea C → `q_comandos` → Tarea B | Comando desde el widget y respuesta física del servo | B / A |
| RF-06 | Modificar el umbral de SpO₂ por RPC (`setUmbralSpO2`) | INS 3.C | Tarea C → `q_comandos` → Tarea B | Cambiar el umbral y verificar el nuevo punto de disparo | B / A |
| RF-07 | Abrir la válvula automáticamente si SpO₂ < umbral, aun sin red | ODS | Tarea B | Bajar la SpO₂ emulada con el router desconectado | A |
| RF-08 | Reportar el estado real de la válvula (final de carrera) | INS 3.A | Tarea B → `mb_actuador` → Tarea C | Bloquear el servo y verificar la discrepancia en ThingsBoard | A |
| RF-09 | Generar alarma si SpO₂ < 90 %, T > 38 °C o FC fuera de 50–120 lpm | INS 3.C, RUB | Cadena de reglas de ThingsBoard | Forzar cada condición con el nodo emulado | B |
| RF-10 | Mostrar signos vitales y estado de la válvula en la interfaz local | INS 3.B (tarea D) | Tarea D, OLED | Inspección visual con y sin red | A |
| RF-11 | Almacenar la telemetría durante desconexiones y reenviarla al reconectar | INS 3.B, RUB | Tarea C, buffer circular | Corte de 30 s; verificar que no haya huecos en la serie | B |
| RF-12 | Supervisar tareas, memoria y watchdog, y publicar métricas | INS 3.B (tarea E) | Tarea E | Revisar `heap_libre` y `stack_min` en ThingsBoard | A |

## Requerimientos no funcionales

| ID | Requerimiento | Métrica / criterio | Origen | Implementa | Verificación | Resp. |
|---|---|---|---|---|---|---|
| RNF-01 | Muestreo determinista | Periodo de la tarea A = 20 ms, jitter < 1 ms | INS 3.B | `vTaskDelayUntil`, prioridad 5, núcleo 1 | Pin GPIO alternado en cada ciclo, medido con osciloscopio | A |
| RNF-02 | Latencia de control remoto | Respuesta RPC < 1 s | RUB | MQTT QoS 1, tarea B por eventos | Marca de tiempo de ThingsBoard vs. marca de la ESP32 (20 comandos) | B |
| RNF-03 | Reconexión automática | Reconecta sin reset tras un corte de 30 s; < 10 s después del retorno de la red | INS 3.B, RUB | Manejadores de eventos de Wi-Fi y MQTT, sin `while(!connected)` | Prueba de desconexión del router (5 repeticiones) | B |
| RNF-04 | Aislamiento de tareas críticas | 0 periodos perdidos de la tarea A durante cortes y ráfagas de red | INS 2.5, RUB | Prioridades, fijación por núcleo, colas sin bloqueo | Contador de periodos perdidos publicado por la tarea E | A |
| RNF-05 | Protección de recursos | Acceso I2C exclusivo, sin deadlocks ni inversión de prioridad no acotada | INS 3.B, RUB | `mtx_i2c` (mutex con herencia de prioridad); OLED escrita por páginas | Prueba de estrés: OLED a máxima tasa mientras A muestrea | A |
| RNF-06 | Comunicación entre tareas | Sin variables globales compartidas para datos | INS 3.B, RUB | Colas y buzones de FreeRTOS | Revisión de código | A / B |
| RNF-07 | Uso de memoria | Heap libre > 40 kB; margen de pila > 25 % en cada tarea | Buenas prácticas | Tarea E (`uxTaskGetStackHighWaterMark`) | Registro durante 30 min | A |
| RNF-08 | Consumo energético | Perfil estimado por modo (activo y Wi-Fi) | INS 4 (artículo) | Medición de corriente USB | Multímetro o medidor USB en serie | B |
| RNF-09 | Exactitud de medición (nodo real) | FC ± 5 lpm, SpO₂ ± 2 %, T ± 0.5 °C frente a la referencia | ODS | Tarea A, filtrado local | Igual que RF-01 y RF-02 | A |
| RNF-10 | Seguridad de las credenciales | Token y Wi-Fi fuera del repositorio | Buenas prácticas | `menuconfig` / `sdkconfig` en `.gitignore` | Revisión del repositorio | B |
