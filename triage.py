# ── Surgery risk ──────────────────────────────────────────────────────────────
SURGERY_RISK_MAP=[
    (["dialysis","kidney dialysis"],35),(["heart","cardiac","bypass","open heart","cabg","valve"],32),
    (["brain","neuro","craniotomy"],30),(["liver","hepatic","transplant"],28),
    (["lung","thoracic","pneumonectomy"],26),(["cancer","oncology","tumor","tumour","chemo"],25),
    (["spine","spinal","laminectomy"],20),(["appendix","appendectomy"],12),
    (["hernia"],10),(["knee","hip","joint","replacement","arthroscopy"],10),
    (["gallbladder","cholecystectomy"],8),(["caesarean","c-section","cesarean"],8),
    (["fracture","ortho","bone"],7),(["icu","intensive care","critical"],20),
]

def surgery_risk_score(stype, sdetail, stimeline):
    tmap={"Within the last month":8,"Within 6 months":4,"More than 6 months ago":1}
    type_map={
        "Heart / Cardiac surgery":32,"Dialysis / Kidney failure":35,"Brain / Neuro surgery":30,
        "Liver / Transplant":28,"Lung / Thoracic surgery":26,"Cancer / Oncology":25,
        "Spine surgery":20,"Appendectomy":12,"Hernia repair":10,"Joint replacement":10,
        "Gallbladder removal":8,"C-section / Obstetric":8,"Fracture / Orthopaedic":7,
        "ICU / Critical care stay":20,"Other / Minor procedure":5,
    }
    tpts=tmap.get(stimeline,0)
    type_pts=type_map.get(stype,5)
    pts=tpts+type_pts
    if sdetail:
        txt=sdetail.lower()
        for kws,bonus in SURGERY_RISK_MAP:
            if any(k in txt for k in kws):
                pts=max(pts,type_pts+tpts+bonus//3); break
    return min(pts,40), stype

def compute_risk(sym,age):
    score=0; factors=[]
    HS={"Chest pain","Breathlessness"}; MS={"Fever","Vomiting","Dizziness","Abdominal pain"}
    HC={"Heart disease","Cancer","Kidney disease"}
    sym_sevs=sym.get("sym_severities",{}); sym_durs=sym.get("sym_durations",{})
    dur_pts={"Today":0,"1–2 days":3,"3–5 days":6,"1–2 weeks":10,"More than 2 weeks":15}
    for s in sym.get("symptoms",[]):
        sev=sym_sevs.get(s,3); dur=sym_durs.get(s,"Today")
        base=20 if s in HS else (10 if s in MS else 4)
        mult={1:0.6,2:0.8,3:1.0,4:1.3,5:1.6}[sev]
        pts=round(base*mult)+dur_pts.get(dur,0); score+=pts
        sl=["","Mild","Mild-moderate","Moderate","Moderate-severe","Severe"][sev]
        dot="🔴" if s in HS else ("🟠" if s in MS else "🟡")
        factors.append(f"{dot} {s} — {sl}, {dur} (+{pts})")
    if age>=60: score+=20; factors.append("👴 Age ≥ 60 (+20)")
    elif age>=45: score+=10; factors.append("🧑 Age 45–59 (+10)")
    for c in sym.get("conditions",[]):
        if c!="None":
            if c in HC: score+=20; factors.append(f"🔴 {c} (+20)")
            else: score+=10; factors.append(f"🟠 {c} (+10)")
    st_=sym.get("surgery","None"); styps=sym.get("surgery_types",[]); sdet=sym.get("surgery_details","")
    if not styps and sym.get("surgery_type"): styps=[sym.get("surgery_type")]
    if st_!="None" and styps:
        for styp in styps:
            s_pts,s_label=surgery_risk_score(styp,sdet,st_)
            score+=s_pts; factors.append(f"🏥 {s_label} ({st_}) (+{s_pts})")
    return min(score,100),factors

