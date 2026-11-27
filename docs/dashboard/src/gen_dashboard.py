import math, random
random.seed(4)
def series(n, base, noise, events=()):
    v=[]
    for i in range(n):
        x=base+random.uniform(-noise,noise)
        for (a,b,delta) in events:
            if a<=i<=b: x+=delta*math.sin(math.pi*(i-a)/(b-a+1e-9)) if b>a else delta
        v.append(x)
    return v
def chart(vals, lo, hi, color, w=760, h=150, thr=None, thrlab="", band=None, gap=None):
    n=len(vals); pts=[]
    path=[]; pen=False
    for i,v in enumerate(vals):
        x=40+i*(w-50)/(n-1); y=10+(hi-v)*(h-30)/(hi-lo)
        if gap and gap[0]<=i<=gap[1]:
            pen=False; continue
        path.append(("M" if not pen else "L")+f"{x:.1f},{y:.1f}"); pen=True
    s=f'<svg style="width:100%;height:{h}px" viewBox="0 0 {w} {h}" preserveAspectRatio="none">'
    for k in range(5):
        val=lo+(hi-lo)*k/4; y=10+(hi-val)*(h-30)/(hi-lo)
        s+=f'<line x1="40" x2="{w-10}" y1="{y}" y2="{y}" stroke="#eceff1"/><text x="34" y="{y+4}" font-size="10" text-anchor="end" fill="#78909c">{val:g}</text>'
    if thr is not None:
        y=10+(hi-thr)*(h-30)/(hi-lo)
        s+=f'<line x1="40" x2="{w-10}" y1="{y}" y2="{y}" stroke="#e53935" stroke-dasharray="5 4"/><text x="{w-12}" y="{y-4}" font-size="10" text-anchor="end" fill="#e53935">{thrlab}</text>'
    if gap:
        x0=40+gap[0]*(w-50)/(n-1); x1=40+gap[1]*(w-50)/(n-1)
        s+=f'<rect x="{x0}" y="10" width="{x1-x0}" height="{h-30}" fill="#fff3e0"/><text x="{(x0+x1)/2}" y="{h/2}" font-size="10" text-anchor="middle" fill="#ef6c00">sin red</text><text x="{(x0+x1)/2}" y="{h/2+13}" font-size="10" text-anchor="middle" fill="#ef6c00">(reenviado)</text>'
    s+=f'<path d="{" ".join(path)}" fill="none" stroke="{color}" stroke-width="2"/>'
    for k,lab in enumerate(["14:00","14:05","14:10","14:15","14:20"]):
        x=40+k*(w-50)/4; anc="end" if k==4 else "middle"; s+=f'<text x="{x}" y="{h-4}" font-size="10" text-anchor="{anc}" fill="#78909c">{lab}</text>'
    return s+'</svg>'
N=120
fc1=series(N,76,3); spo1=series(N,97.2,0.6); t1=series(N,36.7,0.08)
fc2=series(N,82,2,[(70,100,45)]); spo2=series(N,96.5,0.5,[(60,105,-10)]); t2=series(N,37.0,0.06,[(85,119,1.4)])

def kpi(label,val,unit,color,status=""):
    st=f'<div class="st {status}">{"● crítico" if status=="crit" else "● normal"}</div>'
    return f'<div class="kpi"><div class="kl">{label}</div><div class="kv" style="color:{color}">{val}<span>{unit}</span></div>{st}</div>'

def patient(title, sub, mode, fcv, spov, tv, fcs, spos, ts, crit, valve_on, valve_fb, thr, conn, gap=None):
    return f'''
<section class="pcol">
  <div class="phead"><div><b>{title}</b><div class="sub">{sub}</div></div>
    <div class="tags"><span class="tag {mode.lower()}">{mode}</span><span class="tag {'on' if conn else 'off'}">● {'En línea' if conn else 'Desconectado'}</span></div></div>
  <div class="kpis">
    {kpi("Frecuencia cardíaca",fcv," lpm","#1e88e5","crit" if "fc" in crit else "")}
    {kpi("SpO₂",spov," %","#43a047","crit" if "spo2" in crit else "")}
    {kpi("Temperatura",tv," °C","#fb8c00","crit" if "t" in crit else "")}
  </div>
  <div class="card"><div class="ct">SpO₂ — últimos 20 min</div>{chart(spos,80,100,"#43a047",thr=90,thrlab="umbral alarma 90 %",gap=gap)}</div>
  <div class="card"><div class="ct">Frecuencia cardíaca — últimos 20 min</div>{chart(fcs,40,140,"#1e88e5",thr=120,thrlab="límite 120 lpm",gap=gap)}</div>
  <div class="card"><div class="ct">Temperatura — últimos 20 min</div>{chart(ts,36,40,"#fb8c00",thr=38,thrlab="fiebre 38 °C",gap=gap)}</div>
  <div class="ctrl card">
    <div class="ct">Control de oxigenoterapia (RPC)</div>
    <div class="crow">
      <div class="cell"><div class="lbl">Válvula de O₂ <small>setValvula</small></div>
        <div class="switch {'on' if valve_on else ''}"><div class="knob"></div></div><div class="small">{'ABRIR' if valve_on else 'CERRAR'}</div></div>
      <div class="cell"><div class="lbl">Estado real <small>final de carrera</small></div>
        <div class="led {'g' if valve_fb else 'grey'}"></div><div class="small">{'Abierta ✓' if valve_fb else 'Cerrada'}</div></div>
      <div class="cell wide"><div class="lbl">Umbral SpO₂ <small>setUmbralSpO2</small></div>
        <div class="slider"><div class="fill" style="width:{(thr-80)/20*100}%"></div><div class="thumb" style="left:{(thr-80)/20*100}%"></div></div>
        <div class="small">{thr} %  ·  rango 80–100 %</div></div>
    </div>
  </div>
</section>'''

alarms=[("14:19","P2","Fiebre · 38.4 °C","MAYOR","Activa"),
        ("14:17","P2","SpO₂ baja · 84 %","CRÍTICA","Activa"),
        ("14:16","P2","Taquicardia · 126 lpm","MAYOR","Activa"),
        ("14:08","P1","Sensor sin dedo","MENOR","Reconocida")]
rows="".join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td><span class="sev {e.lower()}">{e}</span></td><td>{f}</td></tr>' for a,b,c,e,f in alarms)

html=f'''<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}} body{{margin:0;font-family:"DejaVu Sans",Arial,sans-serif;background:#eceff1;color:#263238;width:1720px}}
.top{{background:#305680;color:white;padding:12px 22px;display:flex;justify-content:space-between;align-items:center}}
.top b{{font-size:19px}} .top .r{{font-size:13px;opacity:.9}}
.note{{background:#fff8e1;color:#795548;font-size:12px;padding:6px 22px;border-bottom:1px solid #ffe082}}
.wrap{{display:grid;grid-template-columns:1fr 1fr 360px;gap:14px;padding:14px}}
.pcol{{display:flex;flex-direction:column;gap:10px}}
.phead{{background:white;border-radius:6px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 1px 2px #0002}}
.sub{{font-size:12px;color:#607d8b}} .tags{{display:flex;gap:6px}}
.tag{{font-size:11px;padding:3px 8px;border-radius:10px;background:#eceff1}} .tag.real{{background:#e3f2fd;color:#1565c0}} .tag.emulado{{background:#fff3e0;color:#e65100}}
.tag.on{{background:#e8f5e9;color:#2e7d32}} .tag.off{{background:#ffebee;color:#c62828}}
.kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}
.kpi{{background:white;border-radius:6px;padding:10px 12px;box-shadow:0 1px 2px #0002}}
.kl{{font-size:12px;color:#607d8b}} .kv{{font-size:34px;font-weight:bold}} .kv span{{font-size:14px;color:#90a4ae;margin-left:3px}}
.st{{font-size:11px;color:#2e7d32}} .st.crit{{color:#c62828;font-weight:bold}}
.card{{background:white;border-radius:6px;padding:8px 10px;box-shadow:0 1px 2px #0002}} .ct{{font-size:13px;font-weight:bold;color:#37474f;margin-bottom:2px}}
.crow{{display:flex;gap:14px;align-items:flex-start;margin-top:6px}} .cell{{flex:1;text-align:center}} .cell.wide{{flex:1.6}}
.lbl{{font-size:12px;color:#455a64;margin-bottom:6px}} .lbl small{{display:block;color:#90a4ae;font-family:monospace}}
.switch{{width:56px;height:28px;border-radius:14px;background:#b0bec5;margin:0 auto;position:relative}} .switch.on{{background:#43a047}}
.knob{{width:24px;height:24px;border-radius:50%;background:white;position:absolute;top:2px;left:2px;box-shadow:0 1px 2px #0004}} .switch.on .knob{{left:30px}}
.led{{width:26px;height:26px;border-radius:50%;margin:0 auto;border:2px solid #cfd8dc}} .led.g{{background:radial-gradient(#a5d6a7,#2e7d32)}} .led.grey{{background:#cfd8dc}}
.small{{font-size:11px;color:#546e7a;margin-top:5px}}
.slider{{height:8px;background:#cfd8dc;border-radius:4px;position:relative;margin:12px 6px 0}} .fill{{height:8px;background:#305680;border-radius:4px}}
.thumb{{width:18px;height:18px;border-radius:50%;background:#305680;position:absolute;top:-5px;margin-left:-9px;border:2px solid white;box-shadow:0 1px 2px #0005}}
.side{{display:flex;flex-direction:column;gap:10px}}
table{{width:100%;border-collapse:collapse;font-size:11px}} th{{text-align:left;color:#78909c;font-weight:normal;border-bottom:1px solid #eceff1;padding:4px 3px}} td{{padding:5px 3px;border-bottom:1px solid #f5f5f5;vertical-align:top}}
.sev{{font-size:10px;padding:2px 5px;border-radius:3px;color:white}} .sev.crítica{{background:#c62828}} .sev.mayor{{background:#ef6c00}} .sev.menor{{background:#f9a825}}
.big{{font-size:30px;font-weight:bold;color:#c62828}} .met td:first-child{{color:#607d8b}} .met td:last-child{{text-align:right;font-weight:bold}}
.rules li{{font-size:12px;margin-bottom:4px}}
</style></head><body>
<div class="top"><b>Telemonitoreo híbrido de pacientes — Panel de enfermería</b><div class="r">ThingsBoard · Prototipo conceptual E1 · 27/11/2026 14:20</div></div>
<div class="note">Maqueta conceptual con datos ilustrativos. El paciente 2 muestra un evento emulado (desaturación, taquicardia, fiebre) y un corte de red de 30 s con reenvío de datos.</div>
<div class="wrap">
{patient("Paciente 1","Nodo real · MAX30102 + MLX90614","REAL",76,97,36.7,fc1,spo1,t1,[],False,False,90,True)}
{patient("Paciente 2","Nodo emulado · generador + potenciómetros","EMULADO",126,84,38.4,fc2,spo2,t2,["fc","spo2","t"],True,True,90,True,gap=(40,47))}
<aside class="side">
  <div class="card"><div class="ct">Alarmas activas</div><div class="big">3</div><div class="small" style="text-align:left">generadas por la cadena de reglas</div></div>
  <div class="card"><div class="ct">Registro de alarmas</div><table><tr><th>Hora</th><th>Pac.</th><th>Alarma</th><th>Sev.</th><th>Estado</th></tr>{rows}</table></div>
  <div class="card"><div class="ct">Reglas configuradas</div><ul class="rules">
    <li>SpO₂ &lt; 90 % → <b>CRÍTICA</b></li><li>FC &lt; 50 o &gt; 120 lpm → <b>MAYOR</b></li><li>T &gt; 38 °C → <b>MAYOR</b></li><li>Sin telemetría &gt; 10 s → <b>MENOR</b></li></ul></div>
  <div class="card"><div class="ct">Salud del sistema (Tarea E)</div><table class="met">
    <tr><td>Latencia RPC (últ. 20)</td><td>320 ms</td></tr><tr><td>Periodos perdidos tarea A</td><td>0</td></tr>
    <tr><td>Heap libre nodo 1 / 2</td><td>148 / 151 kB</td></tr><tr><td>Reconexiones hoy</td><td>2</td></tr><tr><td>Muestras reenviadas</td><td>30</td></tr></table>
    <div class="small" style="text-align:left">Valores ilustrativos: se reemplazan por mediciones reales en la E2.</div></div>
</aside>
</div></body></html>'''
open('../dashboard_maqueta.html','w').write(html)
