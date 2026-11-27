import html
W,H=1640,1000
out=[]
def esc(s): return html.escape(s)
def box(x,y,w,h,title,lines,head="#2B6CB0",fill="#FFFFFF",border=None,rx=8,dash=False,bold_border=False):
    b=border or head
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{b}" stroke-width="{2.5 if bold_border else 1.5}" {"stroke-dasharray=\"6 4\"" if dash else ""}/>')
    if title:
        out.append(f'<path d="M{x},{y+rx} a{rx},{rx} 0 0 1 {rx},-{rx} h{w-2*rx} a{rx},{rx} 0 0 1 {rx},{rx} v{26-rx} h-{w} z" fill="{head}"/>')
        out.append(f'<text x="{x+w/2}" y="{y+18}" text-anchor="middle" font-weight="bold" fill="white" font-size="14">{esc(title)}</text>')
        ty=y+46
    else:
        ty=y+22
    for ln in lines:
        wgt=''
        if ln.startswith('*'): ln=ln[1:]; wgt=' font-weight="bold"'
        out.append(f'<text x="{x+12}" y="{ty}" font-size="12.5"{wgt}>{esc(ln)}</text>'); ty+=18
def cbox(x,y,w,h,lines,fill,stroke,shape="rect"):
    if shape=="rect":
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    elif shape=="hex":
        d=18
        out.append(f'<polygon points="{x+d},{y} {x+w-d},{y} {x+w},{y+h/2} {x+w-d},{y+h} {x+d},{y+h} {x},{y+h/2}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    elif shape=="oct":
        d=14
        out.append(f'<polygon points="{x+d},{y} {x+w-d},{y} {x+w},{y+d} {x+w},{y+h-d} {x+w-d},{y+h} {x+d},{y+h} {x},{y+h-d} {x},{y+d}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    elif shape=="cyl":
        e=10
        out.append(f'<path d="M{x},{y+e} a{w/2},{e} 0 0 1 {w},0 v{h-2*e} a{w/2},{e} 0 0 1 -{w},0 z" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        out.append(f'<path d="M{x},{y+e} a{w/2},{e} 0 0 0 {w},0" fill="none" stroke="{stroke}" stroke-width="1.5"/>')
    n=len(lines); ty=y+h/2-(n-1)*8+5
    for i,ln in enumerate(lines):
        wgt=' font-weight="bold"' if i==0 else ''
        out.append(f'<text x="{x+w/2}" y="{ty+i*16}" text-anchor="middle" font-size="12"{wgt}>{esc(ln)}</text>')
def panel(x,y,w,h,label,fill,stroke):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    out.append(f'<text x="{x+w/2}" y="{y+22}" text-anchor="middle" font-size="14" font-weight="bold" fill="{stroke}">{esc(label)}</text>')
def arrow(pts,color="#333",label=None,lpos=None,dash=None,both=False,head=True,lcolor=None):
    d="M"+" L".join(f"{a},{b}" for a,b in pts)
    mid=f'url(#a{color[1:]})'
    out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.8" {f"stroke-dasharray=\"{dash}\"" if dash else ""} {f"marker-end=\"{mid}\"" if head else ""} {f"marker-start=\"url(#s{color[1:]})\"" if both else ""}/>')
    if label:
        lx,ly=lpos
        out.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="11.5" fill="{lcolor or color}" paint-order="stroke" stroke="white" stroke-width="4">{esc(label)}</text>')

colors=["#333","#C53030","#2F855A","#B7791F","#6B46C1","#4A5568"]
defs="".join(f'<marker id="a{c[1:]}" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker><marker id="s{c[1:]}" markerWidth="10" markerHeight="10" refX="1" refY="5" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="{c}"/></marker>' for c in colors)

out.append(f'<text x="{W/2}" y="38" text-anchor="middle" font-size="20" font-weight="bold">Arquitectura de software FreeRTOS — Nodo paciente (firmware común, ESP-IDF v5.5)</text>')

panel(20,70,210,880,"Periféricos","#F7FAFC","#718096")
panel(270,70,470,880,"Núcleo 1 (APP_CPU) — tiempo real","#EBF8FF","#2B6CB0")
panel(1100,170,520,780,"Núcleo 0 (PRO_CPU) — red y supervisión","#FAF5FF","#6B46C1")
out[-1]=out[-1].replace('x="1360.0"','x="1420"')
out.append(f'<text x="920" y="100" text-anchor="middle" font-size="14" font-weight="bold" fill="#2D3748">Comunicación entre tareas</text>')

box(40,130,170,72,None,["*Bus I2C · 400 kHz","MAX30102 · MLX90614","OLED SSD1306"],fill="#FEF3C7",border="#B7791F")
box(40,345,170,72,None,["*ADC1 (nodo emulado)","GPIO34 · 35 · 32","atenuación 12 dB"],fill="#FEF3C7",border="#B7791F")
cbox(32,236,186,76,["mtx_i2c","Mutex · herencia","de prioridad"],"#FEFCBF","#B7791F",shape="hex")
box(40,560,170,56,None,["*LEDC PWM 50 Hz","GPIO18 → servo SG90"],fill="#E6F4EA",border="#2F855A")
box(40,680,170,56,None,["*GPIO entrada","GPIO19 ← final de carrera"],fill="#E6F4EA",border="#2F855A")

box(300,110,410,178,"Tarea A · Muestreo (crítica)",["Prioridad: 5  ·  fijada al núcleo 1","Periodo: 20 ms con vTaskDelayUntil()","Cómputo estimado: ≤ 2 ms  ·  Pila: 4096 B","Lee sensores (I2C) o ADC1 (nodo emulado)","Calcula FC, SpO₂ y T → publica a 1 Hz","Marca de tiempo + GPIO23 para medir jitter"],head="#C53030",bold_border=True)
box(300,500,410,170,"Tarea B · Control local",["Prioridad: 4  ·  fijada al núcleo 1","Activación: comando RPC o cada 100 ms","Cómputo estimado: ≤ 1 ms  ·  Pila: 3072 B","SpO₂ < umbral → abre válvula (aun sin red)","Verifica estado real con final de carrera"],head="#DD6B20",bold_border=True)
box(300,750,410,170,"Tarea D · Interfaz local",["Prioridad: 3  ·  fijada al núcleo 1","Periodo: 500 ms  ·  Pila: 3072 B","OLED por páginas: 8 × ~3 ms, libera","mtx_i2c entre páginas → bloqueo de A acotado","Nodo 2: resumen por log serie"],head="#2C7A7B",bold_border=True)

cbox(790,150,260,72,["q_telemetria","Cola · 20 × telemetria_t","xQueueSend(…, 0) — nunca bloquea a A"],"#C6F6D5","#2F855A")
cbox(790,330,260,72,["mb_vitales","Buzón (cola de longitud 1)","xQueueOverwrite / xQueuePeek"],"#C6F6D5","#2F855A")
cbox(790,480,260,72,["q_comandos","Cola · 5 × comando_t","setValvula · setUmbralSpO2"],"#FED7D7","#C53030")
cbox(790,640,260,72,["mb_actuador","Buzón (longitud 1)","comandada · estadoReal"],"#C6F6D5","#2F855A")

cbox(1120,72,200,70,["ThingsBoard","broker MQTT :1883"],"#F3E8FF","#6B46C1",shape="cyl")
box(1130,205,300,190,"Tarea C · Comunicaciones",["Prioridad: 2  ·  fijada al núcleo 0","Publicación: cada 1000 ms  ·  Pila: 6144 B","q_telemetria → JSON → MQTT (QoS 1)","RPC recibido → q_comandos","Espera eg_red con timeout:","sin while(!connected)"],head="#6B46C1",bold_border=True)
box(1462,235,140,110,None,["*rb_offline","Buffer circular","300 muestras","(5 min a 1 Hz)"],fill="#FFFFFF",border="#6B46C1")
cbox(1130,440,210,80,["eg_red","Event group","WIFI_OK · MQTT_OK"],"#E9D8FD","#6B46C1",shape="oct")
box(1360,430,240,118,None,["*Tareas del sistema (ESP-IDF)","wifi (23) · esp_event (20)","tcpip / lwIP (18)","mqtt_task (5) en núcleo 0","Reconexión por eventos"],fill="#EDF2F7",border="#A0AEC0")
box(1130,700,460,170,"Tarea E · Supervisor",["Prioridad: 1  ·  fijada al núcleo 0","Periodo: 1000 ms  ·  Pila: 3072 B","Task Watchdog (5 s) suscrito por A, B y C","Heap libre y stack high-water de cada tarea","Contador de periodos perdidos de la tarea A","→ métricas en la telemetría (para el artículo)"],head="#4A5568",bold_border=True)

# edges
arrow([(210,166),(298,166)],label="lectura",lpos=(254,158),both=True)
arrow([(210,380),(298,262)],label="lectura",lpos=(262,330))
arrow([(125,236),(125,205)],color="#B7791F",dash="6 4",label="protege",lpos=(170,226))
arrow([(218,266),(298,240)],color="#B7791F",dash="6 4",head=False)
arrow([(218,282),(250,282),(250,830),(298,830)],color="#B7791F",dash="6 4",head=False)
arrow([(710,175),(788,180)],label="1 Hz",lpos=(748,168))
arrow([(1050,186),(1090,186),(1090,250),(1128,250)],color="#2F855A")
arrow([(710,262),(788,358)],label="overwrite",lpos=(760,300),color="#2F855A")
arrow([(790,385),(712,540)],label="peek",lpos=(742,470),color="#2F855A")
arrow([(790,396),(765,396),(765,810),(712,810)],color="#2F855A",dash="5 4",label="peek",lpos=(765,610))
arrow([(1128,370),(1052,505)],color="#C53030",label="RPC",lpos=(1085,425))
arrow([(790,520),(712,580)],color="#C53030")
arrow([(300,592),(212,590)],color="#C53030",label="PWM",lpos=(256,582))
arrow([(210,708),(298,650)],color="#2F855A",label="estado real",lpos=(254,668))
arrow([(710,640),(788,668)],color="#2F855A")
arrow([(1050,676),(1075,676),(1075,385),(1128,385)],color="#2F855A",label="peek",lpos=(1075,600))
arrow([(790,698),(712,880)],color="#2F855A",dash="5 4",label="peek",lpos=(800,790))
arrow([(1360,478),(1342,478)],color="#6B46C1")
arrow([(1235,440),(1235,397)],color="#6B46C1",dash="5 4",label="espera c/ timeout",lpos=(1240,425))
arrow([(1434,290),(1460,290)],color="#6B46C1",both=True)
arrow([(1190,203),(1190,144)],color="#6B46C1",both=True,label="telemetría / RPC",lpos=(1262,180),lcolor="#6B46C1")
arrow([(1128,728),(742,728)],color="#4A5568",dash="2 4",label="monitorea A, B, D",lpos=(940,745))

# legend
lx,ly=790,820
out.append(f'<rect x="{lx}" y="{ly}" width="290" height="120" rx="8" fill="white" stroke="#CBD5E0"/>')
items=[("#2F855A",None,"Datos (telemetría, estado)"),("#C53030",None,"Comandos (RPC → actuador)"),("#B7791F","6 4","Acceso protegido por mutex"),("#4A5568","2 4","Supervisión")]
for i,(c,dsh,t) in enumerate(items):
    y=ly+25+i*24
    out.append(f'<line x1="{lx+15}" y1="{y}" x2="{lx+60}" y2="{y}" stroke="{c}" stroke-width="2.5" {f"stroke-dasharray=\"{dsh}\"" if dsh else ""}/>')
    out.append(f'<text x="{lx+70}" y="{y+4}" font-size="12">{t}</text>')

svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="DejaVu Sans, sans-serif"><defs>{defs}</defs><rect width="100%" height="100%" fill="white"/>'+"\n".join(out)+'</svg>'
open('../freertos.svg','w').write(svg)
