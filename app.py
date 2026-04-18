import streamlit as st
from datetime import datetime
import base64

st.set_page_config(page_title="TELEMED", page_icon="🏥", layout="wide")

# ── Session state ─────────────────────────────────────────────────────────────
def init():
    defaults = {
        "page":"login","logged_in":False,"user":{},
        "past_history":[],"past_consults":[],
        "symptom_info":{},"triage_step":1,
        "selected_doctor":None,
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v
init()

def go(page):
    st.session_state.page=page
    st.rerun()

# ── Real doctors (Chennai) ────────────────────────────────────────────────────
DOCTORS = [
    {
        "name":"Dr. G. Sengottuvelu","spec":"Interventional Cardiologist",
        "available":True,"slot":"2:00 PM – 5:00 PM",
        "emoji":"👨‍⚕️","color":"#e3f2fd",
        "exp":"25+ years","lang":"English, Tamil, Hindi",
        "hospital":"Apollo Hospitals, 21 Greams Lane, Off Greams Road, Chennai – 600 006",
        "hospital_map":"https://maps.google.com/?q=Apollo+Hospitals+Greams+Road+Chennai",
        "qual":"MBBS, MD, DM, DNB, FRCP (London), FRCP (Glasgow), FSCAI — Fellowship in Interventional Cardiology, France",
        "about":"Dr. G. Sengottuvelu is one of Tamil Nadu's most respected interventional cardiologists with over 25,000 successful procedures. He is Clinical Lead of Structural Heart Interventions at Apollo Hospitals and is internationally recognised for complex coronary and structural heart interventions including TAVI/TAVR. He trained at Madras Medical College and completed advanced fellowship in France.",
    },
    {
        "name":"Dr. Y. Vijayachandra Reddy","spec":"Cardiologist",
        "available":False,"slot":"Fully booked today",
        "emoji":"👨‍⚕️","color":"#fce4ec",
        "exp":"27 years","lang":"English, Telugu, Tamil",
        "hospital":"Apollo Hospitals, 21 Greams Lane, Off Greams Road, Chennai – 600 006",
        "hospital_map":"https://maps.google.com/?q=Apollo+Hospitals+Greams+Road+Chennai",
        "qual":"MD, DM, MRCP (UK), FACC, FCSI — British Commonwealth Scholar, University Hospital of Wales, Cardiff",
        "about":"Dr. Y. Vijayachandra Reddy is an internationally renowned interventional cardiologist, pioneer of transradial interventions and complex high-risk PCI in India. He specialises in cardiac arrhythmias, coronary imaging (FFR, OCT, IVUS), and primary angioplasty for acute myocardial infarction.",
    },
    {
        "name":"Dr. Refai Showkathali","spec":"Interventional Cardiologist",
        "available":True,"slot":"9:00 AM – 12:00 PM",
        "emoji":"👨‍⚕️","color":"#e8f5e9",
        "exp":"18 years","lang":"English, Tamil, Arabic",
        "hospital":"Apollo Hospitals, 21 Greams Lane, Off Greams Road, Chennai – 600 006",
        "hospital_map":"https://maps.google.com/?q=Apollo+Hospitals+Greams+Road+Chennai",
        "qual":"MBBS, MRCP (UK), FRCP — Fellow, Royal College of Physicians; Fellow, American College of Cardiology; Fellow, European Society of Cardiology",
        "about":"Dr. Refai Showkathali is an award-winning interventional cardiologist with expertise in structural heart disease interventions including BAV, TAVI and PFO/ASD closure. He completed a fellowship at King's College Hospital, London and regularly presents research at conferences across Europe and the USA.",
    },
    {
        "name":"Dr. I. Sathyamurthy","spec":"Interventional Cardiologist",
        "available":True,"slot":"10:00 AM – 1:00 PM",
        "emoji":"👨‍⚕️","color":"#fff8e1",
        "exp":"37+ years","lang":"English, Tamil, Telugu",
        "hospital":"Apollo Hospitals, 21 Greams Lane, Off Greams Road, Chennai – 600 006",
        "hospital_map":"https://maps.google.com/?q=Apollo+Hospitals+Greams+Road+Chennai",
        "qual":"MBBS, MD, DM — FACC (USA), FRCP Edinburgh, FRCP Glasgow, DSc (Honoris Causa) Dr. MGR Medical University",
        "about":"Dr. Immaneni Sathyamurthy is one of India's most decorated cardiologists, recipient of the Padma Shri, Dr. B.C. Roy National Award, and TANSA Award for Medical Sciences. With 37+ years of experience and 230+ publications, he is a member of the Tamil Nadu Medical Council and a globally respected leader in interventional cardiology.",
    },
    {
        "name":"Dr. Robert Mao","spec":"Cardiac & Vascular Surgeon",
        "available":False,"slot":"Fully booked today",
        "emoji":"👨‍⚕️","color":"#f3e5f5",
        "exp":"38+ years","lang":"English, Tamil",
        "hospital":"Apollo Hospitals, 21 Greams Lane, Off Greams Road, Chennai – 600 006",
        "hospital_map":"https://maps.google.com/?q=Apollo+Hospitals+Greams+Road+Chennai",
        "qual":"MBBS (1977), MD General Medicine (1980), DM Cardiology (1982) — Karnataka Medical University",
        "about":"Dr. Robert Mao is a highly respected cardiac and vascular surgeon with over 38 years of experience. He specialises in open heart surgery, aortic aneurysm surgery, PCI, vascular surgery, and mitral/heart valve replacement. He has published extensively in reputed medical journals.",
    },
    {
        "name":"Dr. A. Muruganathan","spec":"Physician & Diabetologist",
        "available":True,"slot":"Available now",
        "emoji":"👨‍⚕️","color":"#e0f7fa",
        "exp":"32+ years","lang":"English, Tamil, Hindi",
        "hospital":"AG Hospital, Tirupur (Telemedicine consults available, Chennai)",
        "hospital_map":"https://maps.google.com/?q=AG+Hospital+Tirupur",
        "qual":"MBBS, MD — Former Member, Medical Council of India (2007–2012); Member, Nursing Council of India (2008–2012)",
        "about":"Dr. A. Muruganathan is a nationally renowned physician with 32+ years of experience in cardiology and diabetology. He is the managing trustee of the Tirupur Social Service Organisation and has organised several national and international medical conferences including Commonwealth Medical Association workshops.",
    },
]

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

def calc_bmi(w,h):
    if h<=0 or w<=0: return None,"—"
    bmi=round(w/(h/100)**2,1)
    cat="Underweight" if bmi<18.5 else ("Normal" if bmi<25 else ("Overweight" if bmi<30 else "Obese"))
    return bmi,cat

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

def set_bg(color):
    st.markdown(f"<style>.stApp{{background-color:{color}!important;}}</style>",unsafe_allow_html=True)

# ── STYLES ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
html,body{font-family:'Nunito',sans-serif!important;}
.stApp,.stApp *{font-family:'Nunito',sans-serif!important;}

/* ── ALL TEXT BLACK ── */
.stApp p,.stApp span,.stApp div,.stApp label,
.stApp li,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5,
.stMarkdown p,.stMarkdown li,.stMarkdown div{color:#111111!important;}
.stMarkdown h1,.stMarkdown h2,.stMarkdown h3{color:#1565c0!important;}

/* inputs always light bg, dark text — even when focused/typing */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus,
.stTextInput input:active,
.stNumberInput input:active,
.stTextArea textarea:active,
.stTextInput>div>div>input,
.stTextInput>div>div>input:focus,
input[type="text"], input[type="email"], input[type="number"], input[type="tel"],
input[type="text"]:focus, input[type="email"]:focus, input[type="number"]:focus {
    color:#111111!important;
    background:#ffffff!important;
    background-color:#ffffff!important;
    border:1.5px solid #b0d4f1!important;
    border-radius:10px!important;
    -webkit-text-fill-color:#111111!important;
    caret-color:#1d4ed8!important;
}
/* kill browser autofill dark bg */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
    -webkit-box-shadow:0 0 0 1000px #ffffff inset!important;
    box-shadow:0 0 0 1000px #ffffff inset!important;
    -webkit-text-fill-color:#111111!important;
    background-color:#ffffff!important;
}
.stTextInput label,.stNumberInput label,.stTextArea label,
.stSelectbox label,.stMultiSelect label,.stSlider label,
.stRadio label,.stCheckbox label{color:#111111!important;font-weight:700!important;}
.stRadio div[role="radiogroup"] label{color:#111111!important;}
.stSelectbox [data-baseweb="select"]{background:#ffffff!important;}
.stSelectbox [data-baseweb="select"] *{color:#111111!important;background:#ffffff!important;}
[data-baseweb="popover"]{background:#ffffff!important;}
[data-baseweb="popover"] *{color:#111111!important;}
[role="listbox"]{background:#ffffff!important;}
[role="option"]{background:#ffffff!important;color:#111111!important;}
[role="option"]:hover{background:#dbeafe!important;color:#1e40af!important;}
.stMultiSelect [data-baseweb="select"]{background:#ffffff!important;}
.stMultiSelect [data-baseweb="select"] *{color:#111111!important;}
span[data-baseweb="tag"]{background:#dbeafe!important;}
span[data-baseweb="tag"] span{color:#1e40af!important;}
[data-testid="stMetricLabel"]{color:#374151!important;font-weight:700!important;}
[data-testid="stMetricValue"]{color:#1565c0!important;font-weight:900!important;}
[data-testid="stCaptionContainer"] p,.stCaption{color:#6b7280!important;}
hr{border-color:#bfdbfe!important;}
[data-testid="stProgressBar"]>div{background:#1565c0!important;}
[data-testid="stExpander"]{background:#f0f7ff!important;border:1.5px solid #bfdbfe!important;border-radius:12px!important;}
[data-testid="stExpander"] summary{color:#1565c0!important;font-weight:800!important;font-size:14px!important;padding:10px 16px!important;display:flex!important;align-items:center!important;gap:8px!important;}
[data-testid="stExpander"] summary *{color:#1565c0!important;}
[data-testeid="stExpander"] summary svg{display:none!important;width:0!important;height:0!important;}
[data-testid="stExpander"] summary svg{display:none!important;}
[data-testid="stExpander"] summary p{color:#1565c0!important;font-weight:800!important;margin:0!important;padding:0!important;}
[data-testid="stExpander"] summary::before{content:"▶ ";font-size:11px;color:#1565c0!important;}
[data-testid="stExpander"][open] summary::before{content:"▼ ";font-size:11px;color:#1565c0!important;}

/* ── BUTTONS ── */
div.stButton>button{
    border-radius:12px!important;font-weight:800!important;
    font-family:'Nunito',sans-serif!important;
    color:#1d4ed8!important;background-color:#eff6ff!important;
    border:1.5px solid #bfdbfe!important;transition:all 0.15s!important;}
div.stButton>button:hover{background-color:#dbeafe!important;color:#1e40af!important;border-color:#93c5fd!important;}
div.stButton>button:active,div.stButton>button:focus{
    background-color:#bfdbfe!important;color:#1e3a8a!important;
    border-color:#3b82f6!important;box-shadow:none!important;outline:none!important;}
div.stButton>button[kind="primary"]{
    background-color:#1d4ed8!important;color:#ffffff!important;border-color:#1d4ed8!important;}
div.stButton>button[kind="primary"]:hover{background-color:#2563eb!important;color:#fff!important;}
div.stButton>button[kind="primary"]:active,div.stButton>button[kind="primary"]:focus{
    background-color:#1e3a8a!important;color:#fff!important;box-shadow:none!important;}
div.stButton>button:disabled{opacity:0.4!important;}

/* ── LAYOUT COMPONENTS ── */
.nav-brand{font-size:22px;font-weight:900;color:#1d4ed8!important;letter-spacing:0.05em;}
.page-title{font-size:26px;font-weight:900;color:#1d4ed8!important;margin-bottom:0.2rem;}
.page-sub{font-size:14px;color:#374151!important;font-weight:600;margin-bottom:1.2rem;}

.info-grid-2{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:1rem;}
.info-cell{background:#f0f7ff;border-radius:12px;padding:0.9rem 1.1rem;border:1.5px solid #bfdbfe;}
.info-lbl{font-size:11px;color:#6b7280!important;text-transform:uppercase;letter-spacing:0.08em;font-weight:800;}
.info-val{font-size:15px;font-weight:900;color:#1d4ed8!important;margin-top:3px;}

.hist-card{background:#f8faff;border-radius:14px;padding:1rem 1.25rem;
    border:1.5px solid #bfdbfe;margin-bottom:0.75rem;
    box-shadow:0 2px 8px rgba(29,78,216,0.05);}

.badge-safe  {background:#d1fae5;color:#065f46!important;padding:4px 12px;border-radius:99px;font-size:12px;font-weight:800;white-space:nowrap;}
.badge-warn  {background:#fef3c7;color:#92400e!important;padding:4px 12px;border-radius:99px;font-size:12px;font-weight:800;white-space:nowrap;}
.badge-danger{background:#fee2e2;color:#991b1b!important;padding:4px 12px;border-radius:99px;font-size:12px;font-weight:800;white-space:nowrap;}
.badge-booked{background:#dbeafe;color:#1e40af!important;padding:4px 12px;border-radius:99px;font-size:12px;font-weight:800;white-space:nowrap;}

.chip{display:inline-block;background:#dbeafe;color:#1e40af!important;border-radius:99px;
    padding:4px 12px;font-size:13px;font-weight:800;margin-right:6px;margin-bottom:4px;}

.result-safe  {background:#ecfdf5;border-left:5px solid #10b981;border-radius:12px;padding:1.25rem;display:block;overflow:hidden;}
.result-warn  {background:#fffbeb;border-left:5px solid #f59e0b;border-radius:12px;padding:1.25rem;display:block;overflow:hidden;}
.result-danger{background:#fef2f2;border-left:5px solid #ef4444;border-radius:12px;padding:1.25rem;display:block;overflow:hidden;}
/* Only colour direct text children, NOT nested expanders */
.result-safe>div,.result-safe>p,.result-safe>span   {color:#065f46!important;}
.result-warn>div,.result-warn>p,.result-warn>span   {color:#92400e!important;}
.result-danger>div,.result-danger>p,.result-danger>span {color:#991b1b!important;}

.sev-box{background:#eff6ff;border-radius:12px;padding:1rem 1.25rem;border:1.5px solid #bfdbfe;margin:0.75rem 0;}

.doc-info-panel{background:#f0f7ff;border-radius:14px;padding:1.25rem 1.5rem;
    border:1.5px solid #bfdbfe;margin-top:0.5rem;margin-bottom:0.75rem;}

.footer{margin-top:3rem;padding:1rem 0;text-align:center;border-top:1.5px solid #bfdbfe;}
div[data-testid="stForm"]{border:none!important;padding:0!important;box-shadow:none!important;background:transparent!important;}
div[data-testid="stSidebarNav"]{display:none;}
</style>
""",unsafe_allow_html=True)

# ── Navbar ────────────────────────────────────────────────────────────────────
def navbar():
    user=st.session_state.user; first=user.get("name","User").split()[0]
    n1,n2,n3,n4,n5=st.columns([3,1,1,1,1])
    with n1: st.markdown('<span class="nav-brand">🏥 TELEMED</span>',unsafe_allow_html=True)
    with n2:
        if st.button(f"👤 {first}",use_container_width=True,key="nav_ui"): go("user_info")
    with n3:
        if st.button("📋 History",use_container_width=True,key="nav_ph"): go("past_history")
    with n4:
        if st.button("📅 Consults",use_container_width=True,key="nav_pc"): go("past_consults")
    with n5:
        if st.button("🚪 Log out",use_container_width=True,key="nav_lo"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
    st.markdown("---")

def footer():
    st.markdown('<div class="footer"><span style="font-size:13px;font-weight:700;color:#6b7280;">© 2026 TELEMED · Team TELEMED · Healathon</span></div>',unsafe_allow_html=True)
    if st.button("ℹ️ About us",key="footer_about"): go("about")

# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN / EDIT PROFILE
# ═══════════════════════════════════════════════════════════════════════════════
def page_login(edit_mode=False):
    set_bg("#eef5ff")
    user=st.session_state.user if edit_mode else {}
    if edit_mode:
        navbar()
        st.markdown('<div class="page-title">✏️ Edit your profile</div>',unsafe_allow_html=True)
        _,col,_=st.columns([1,2,1])
    else:
        st.markdown("<br>",unsafe_allow_html=True)
        _,col,_=st.columns([1,1.3,1])

    with col:
        if not edit_mode:
            st.markdown("""
            <div style="text-align:center;margin-bottom:1.5rem;">
                <div style="font-size:54px;">🏥</div>
                <div style="font-size:32px;font-weight:900;color:#1d4ed8;letter-spacing:0.08em;">TELEMED</div>
                <div style="font-size:14px;color:#374151;font-weight:700;margin-top:4px;">Smart Telemedicine Triage Engine</div>
            </div>""",unsafe_allow_html=True)

        st.markdown("""
        <style>
        .stTextInput input:focus,.stNumberInput input:focus,.stTextArea textarea:focus{
            background:#ffffff!important;color:#111111!important;
            border-color:#93c5fd!important;box-shadow:0 0 0 2px rgba(147,197,253,0.3)!important;}
        .stTextInput input,.stNumberInput input,.stTextArea textarea{
            background:#ffffff!important;color:#111111!important;}
        </style>
        """,unsafe_allow_html=True)
        st.markdown('<div style="background:#ffffff;border-radius:20px;padding:2rem;border:2px solid #bfdbfe;box-shadow:0 8px 32px rgba(29,78,216,0.10);">',unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:18px;font-weight:900;color:#1d4ed8;margin-bottom:1rem;">{"Update your details" if edit_mode else "Create your profile"}</div>',unsafe_allow_html=True)

        # Profile photo upload — force light background
        st.markdown("""
        <style>
        [data-testid="stFileUploader"]{background:#f0f7ff!important;border-radius:10px!important;border:1.5px solid #bfdbfe!important;padding:0.5rem!important;}
        [data-testid="stFileUploader"] *{color:#111111!important;background:transparent!important;}
        [data-testid="stFileUploader"] section{background:#f0f7ff!important;}
        [data-testid="stFileUploader"] button{background:#eff6ff!important;color:#1d4ed8!important;border:1.5px solid #bfdbfe!important;}
        </style>
        """, unsafe_allow_html=True)
        st.markdown('<div style="font-size:13px;font-weight:700;color:#111111;margin-bottom:4px;">Profile photo (optional)</div>',unsafe_allow_html=True)
        photo_file=st.file_uploader("",type=["png","jpg","jpeg"],label_visibility="collapsed",key="photo_upload")
        if photo_file:
            b64=base64.b64encode(photo_file.read()).decode()
            ext=photo_file.name.split(".")[-1]
            st.markdown(f'<img src="data:image/{ext};base64,{b64}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:3px solid #bfdbfe;display:block;margin:8px 0 12px 0;">',unsafe_allow_html=True)
            st.session_state.user["photo_b64"]=b64
            st.session_state.user["photo_ext"]=ext

        with st.form("login_form"):
            name =st.text_input("Full name",value=user.get("name",""),placeholder="e.g. Aditi Sajjan")
            email=st.text_input("Gmail ID",value=user.get("email",""),placeholder="e.g. aditi@gmail.com")
            age  =st.number_input("Age",min_value=1,max_value=120,value=int(user.get("age",20)))
            c1,c2=st.columns(2)
            with c1: height=st.number_input("Height (cm)",min_value=50,max_value=250,value=int(user.get("height",165)))
            with c2: weight=st.number_input("Weight (kg)",min_value=10,max_value=300,value=int(user.get("weight",60)))
            gender=st.radio("Gender",["Female","Male","Other"],horizontal=True,
                            index=["Female","Male","Other"].index(user.get("gender","Female")))
            blood =st.selectbox("Blood group",["A+","A-","B+","B-","AB+","AB-","O+","O-"],
                                index=["A+","A-","B+","B-","AB+","AB-","O+","O-"].index(user.get("blood","O+")) if user.get("blood") else 0)
            phone =st.text_input("Phone number (10 digits)",value=user.get("phone",""),placeholder="9876543210",max_chars=10)
            submitted=st.form_submit_button("Save changes ✓" if edit_mode else "Continue →",type="primary",use_container_width=True)

        st.markdown('</div>',unsafe_allow_html=True)

        if submitted:
            errs=[]
            if not name.strip(): errs.append("Name is required.")
            if not email.strip(): errs.append("Gmail ID is required.")
            if not phone.strip(): errs.append("Phone number is required.")
            elif not phone.strip().isdigit(): errs.append("Phone must be digits only.")
            elif len(phone.strip())!=10: errs.append("Phone must be exactly 10 digits.")
            for e in errs: st.error(e)
            if not errs:
                bmi_val,bmi_cat=calc_bmi(weight,height)
                keep_photo={"photo_b64":st.session_state.user.get("photo_b64"),
                            "photo_ext":st.session_state.user.get("photo_ext")}
                st.session_state.user={
                    "name":name.strip(),"email":email.strip(),"age":int(age),
                    "height":int(height),"weight":int(weight),"bmi":bmi_val,"bmi_cat":bmi_cat,
                    "gender":gender,"blood":blood,"phone":phone.strip(),
                    "joined":user.get("joined",datetime.now().strftime("%B %Y")),
                    **keep_photo,
                }
                st.session_state.logged_in=True
                go("home")

        if edit_mode:
            st.write("")
            if st.button("← Back to home",use_container_width=True): go("home")

# ═══════════════════════════════════════════════════════════════════════════════
# HOME
# ═══════════════════════════════════════════════════════════════════════════════
def page_home():
    set_bg("#eef5ff")
    navbar()
    user=st.session_state.user; first=user["name"].split()[0]
    st.markdown(f"""
    <div style="background:#dbeafe;border-radius:20px;padding:1.5rem 2rem;
                margin-bottom:1.5rem;border:1.5px solid #93c5fd;">
        <div style="font-size:26px;font-weight:900;color:#1e3a8a;">Hey {first}! 👋</div>
        <div style="font-size:14px;color:#1d4ed8;font-weight:700;margin-top:4px;">What would you like to do today?</div>
    </div>""",unsafe_allow_html=True)

    # Inject CSS to make home card buttons tall and card-like
    st.markdown("""
    <style>
    div[data-testid="stButton"] button.home-card-btn {
        height: 200px !important;
        white-space: normal !important;
        font-size: 15px !important;
        line-height: 1.5 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 1.5rem !important;
    }
    </style>""", unsafe_allow_html=True)

    cards=[
        ("🩺","Predict risk","Enter symptoms and get an instant triage recommendation","triage"),
        ("📅","Book consultation","Schedule a teleconsultation with an available doctor","doctors"),
        ("📋","Test results","View your past triage results and consultation history","past_history"),
    ]
    cols=st.columns(3)
    for col,(icon,title,desc,dest) in zip(cols,cards):
        with col:
            # Single button styled as a full card — no separate HTML card needed
            if st.button(
                f"{icon}\n\n**{title}**\n\n{desc}",
                key=f"home_{dest}",
                use_container_width=True,
                type="secondary",
            ):
                if dest=="triage": st.session_state.triage_step=1
                go(dest)

    st.markdown("---")
    m1,m2,m3=st.columns(3)
    m1.metric("Total assessments",len(st.session_state.past_history))
    m2.metric("Consultations booked",len(st.session_state.past_consults))
    with m3:
        st.markdown("""
        <div style="background:#fee2e2;border-radius:12px;padding:0.75rem 1rem;
                    border:1.5px solid #fca5a5;text-align:center;">
            <div style="font-size:12px;font-weight:800;color:#991b1b;margin-bottom:6px;">🚨 Emergency</div>
            <a href="tel:108" style="display:block;background:#dc2626;color:#fff;border-radius:8px;
               padding:7px 0;font-size:15px;font-weight:900;text-decoration:none;margin-bottom:5px;">
               🚑 Call 108
            </a>
            <a href="tel:112" style="display:block;background:#1d4ed8;color:#fff;border-radius:8px;
               padding:5px 0;font-size:13px;font-weight:800;text-decoration:none;">
               📞 112 National
            </a>
        </div>""", unsafe_allow_html=True)
    footer()

# ═══════════════════════════════════════════════════════════════════════════════
# TRIAGE
# ═══════════════════════════════════════════════════════════════════════════════
SURGERY_TYPES=["Heart / Cardiac surgery","Dialysis / Kidney failure","Brain / Neuro surgery",
               "Liver / Transplant","Lung / Thoracic surgery","Cancer / Oncology","Spine surgery",
               "Appendectomy","Hernia repair","Joint replacement","Gallbladder removal",
               "C-section / Obstetric","Fracture / Orthopaedic","ICU / Critical care stay",
               "Other / Minor procedure"]
DUR_OPTIONS=["Today","1–2 days","3–5 days","1–2 weeks","More than 2 weeks"]

def page_triage():
    set_bg("#eef5ff"); navbar()
    user=st.session_state.user; step=st.session_state.triage_step
    st.markdown('<div class="page-title">🩺 Triage assessment</div>',unsafe_allow_html=True)
    st.progress((step-1)/2); st.caption(f"Step {step} of 2")
    st.markdown(f'<span class="chip">👤 {user["name"]}</span><span class="chip">Age {user["age"]}</span><span class="chip">{user["gender"]}</span><span class="chip">{user["blood"]}</span>',unsafe_allow_html=True)
    st.write("")
    SYMS=["Chest pain","Breathlessness","Fever","Cough","Headache","Vomiting","Dizziness","Fatigue","Rash","Abdominal pain"]
    CONDS=["Diabetes","Hypertension","Heart disease","Asthma","Cancer","Kidney disease","None"]

    if step==1:
        st.subheader("Current symptoms")
        symptoms=st.multiselect("Select all symptoms present",SYMS)
        sym_severities={}; sym_durations={}
        if symptoms:
            st.markdown('<div class="sev-box"><div style="font-size:14px;font-weight:800;color:#1d4ed8;">Rate each symptom — severity &amp; duration</div></div>',unsafe_allow_html=True)
            st.write("")
            for sym in symptoms:
                st.markdown(f'<div style="font-size:14px;font-weight:800;color:#1d4ed8;margin-bottom:2px;">📍 {sym}</div>',unsafe_allow_html=True)
                sc,dc=st.columns(2)
                with sc: sym_severities[sym]=st.slider("Severity",1,5,3,key=f"sev_{sym}",help="1=very mild · 5=very severe")
                with dc: sym_durations[sym]=st.selectbox("Duration",DUR_OPTIONS,key=f"dur_{sym}")
                st.write("")
        st.divider()
        st.subheader("Medical history")
        conditions=st.multiselect("Past or ongoing conditions",CONDS,default=["None"])
        medications=st.text_input("Current medications (optional)")
        surgery=st.radio("Recent surgery / hospitalization?",["None","Within the last month","Within 6 months","More than 6 months ago"],horizontal=True)
        surgery_types=[]; surgery_details=""
        if surgery!="None":
            surgery_types=st.multiselect("Type(s) of surgery / procedure (select all that apply)",SURGERY_TYPES)
            surgery_details=st.text_area("Describe briefly (optional)",placeholder="e.g. Dialysis 3× per week at Apollo Hospital",height=75)

        c1,c2=st.columns([1,3])
        with c1:
            if st.button("← Home"): go("home")
        with c2:
            if st.button("Get recommendation →",type="primary",use_container_width=True):
                if not symptoms: st.error("Please select at least one symptom.")
                else:
                    st.session_state.symptom_info={"symptoms":symptoms,"sym_severities":sym_severities,
                        "sym_durations":sym_durations,"conditions":conditions,"medications":medications,
                        "surgery":surgery,"surgery_types":surgery_types,"surgery_details":surgery_details}
                    st.session_state.triage_step=2; st.rerun()

    elif step==2:
        sym=st.session_state.symptom_info
        score,factors=compute_risk(sym,user["age"])
        if score>=70:
            bc="#ef4444";lb="HIGH RISK";lc="#991b1b";rc="result-danger";em="🚨"
            rm="Please go to the nearest emergency room or call emergency services immediately.<br><br>🚨 <b>Emergency numbers:</b> Ambulance <b>108</b> &nbsp;·&nbsp; Police <b>100</b> &nbsp;·&nbsp; National Emergency <b>112</b>"
        elif score>=40:
            bc="#f59e0b";lb="MODERATE RISK";lc="#92400e";rc="result-warn";em="⚠️"
            rm="Your symptoms need a physical examination. Visit a clinic or hospital."
        else:
            bc="#10b981";lb="LOW RISK";lc="#065f46";rc="result-safe";em="✅"
            rm="Your condition appears manageable remotely. Proceed to book an online consultation."

        # ── Score card (centred) ──────────────────────────────────────────────
        _,sc_col,_=st.columns([1,2,1])
        with sc_col:
            st.markdown(f"""
            <div style="text-align:center;background:#ffffff;border-radius:16px;
                        padding:2rem 1.5rem;border:1.5px solid #bfdbfe;">
                <div style="font-size:13px;font-weight:800;color:#6b7280;letter-spacing:0.1em;">RISK SCORE</div>
                <div style="font-size:72px;font-weight:900;color:{lc};line-height:1.1;margin:0.25rem 0;">{score}</div>
                <div style="font-size:13px;color:#6b7280;font-weight:700;">out of 100</div>
                <span style="display:inline-block;margin-top:0.75rem;background:{bc};color:#fff;
                             padding:5px 18px;border-radius:99px;font-size:13px;font-weight:900;">{lb}</span>
            </div>""",unsafe_allow_html=True)

        st.write("")  # clear gap

        # ── Recommendation box ────────────────────────────────────────────────
        if rc == "result-safe":
            rec_bg="background:#ecfdf5"; rec_bl="border-left:5px solid #10b981"; rec_tc="color:#065f46"
        elif rc == "result-warn":
            rec_bg="background:#fffbeb"; rec_bl="border-left:5px solid #f59e0b"; rec_tc="color:#92400e"
        else:
            rec_bg="background:#fef2f2"; rec_bl="border-left:5px solid #ef4444"; rec_tc="color:#991b1b"
        st.markdown(
            f'<div style="{rec_bg};{rec_bl};border-radius:12px;padding:1.25rem;margin-bottom:1rem;">'
            f'<div style="font-size:17px;font-weight:900;{rec_tc};">{em} {rm}</div></div>',
            unsafe_allow_html=True)

        # ── Score breakdown — shown directly, no expander ───────────────────
        st.markdown('<div style="background:#f0f7ff;border-radius:12px;padding:1rem 1.25rem;border:1.5px solid #bfdbfe;margin-top:0.5rem;"><div style="font-size:13px;font-weight:800;color:#1d4ed8;margin-bottom:8px;">Risk score breakdown</div>', unsafe_allow_html=True)
        for f in factors:
            st.markdown(f'<div style="font-size:13px;font-weight:700;color:#111111;padding:4px 0;border-bottom:1px solid #e5e7eb;">{f}</div>', unsafe_allow_html=True)
        det=sym.get("surgery_details","")
        if det:
            st.markdown(f'<div style="margin-top:8px;font-size:13px;color:#374151;font-weight:700;">📝 Surgery notes: {det}</div>',unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Save to history ───────────────────────────────────────────────────
        record={"date":datetime.now().strftime("%d %b %Y, %I:%M %p"),"symptoms":", ".join(sym["symptoms"]),
                "score":score,"level":"Emergency care needed" if score>=70 else ("In-person visit recommended" if score>=40 else "Safe for teleconsultation"),"emoji":em}
        h=st.session_state.past_history
        if not h or h[0].get("symptoms")!=record["symptoms"]: st.session_state.past_history.insert(0,record)

        st.write("")
        c1,c2,c3=st.columns(3)
        with c1:
            if st.button("← Edit"): st.session_state.triage_step=1; st.rerun()
        with c2:
            if st.button("Book consultation",type="primary"): go("doctors")
        with c3:
            if st.button("← Home"): go("home")

# ═══════════════════════════════════════════════════════════════════════════════
# USER INFO
# ═══════════════════════════════════════════════════════════════════════════════
def page_user_info():
    set_bg("#eef5ff"); navbar()
    user=st.session_state.user
    initials="".join(w[0].upper() for w in user["name"].split()[:2])
    bmi=user.get("bmi","—"); bmi_cat=user.get("bmi_cat","—")
    bmi_col="#065f46" if bmi_cat=="Normal" else ("#92400e" if bmi_cat in ("Overweight","Obese") else "#1d4ed8")

    st.markdown('<div class="page-title">👤 User information</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Your profile details from registration</div>',unsafe_allow_html=True)

    # Avatar / photo
    photo_b64=user.get("photo_b64"); photo_ext=user.get("photo_ext","png")
    if photo_b64:
        avatar_html=f'<img src="data:image/{photo_ext};base64,{photo_b64}" style="width:70px;height:70px;border-radius:50%;object-fit:cover;border:3px solid #93c5fd;flex-shrink:0;">'
    else:
        avatar_html=f'<div style="width:70px;height:70px;border-radius:50%;background:#1d4ed8;display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:900;color:#fff;flex-shrink:0;">{initials}</div>'

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1.25rem;
                background:linear-gradient(135deg,#dbeafe,#bfdbfe);
                border-radius:18px;padding:1.5rem 2rem;margin-bottom:1.5rem;border:1.5px solid #93c5fd;">
        {avatar_html}
        <div>
            <div style="font-size:22px;font-weight:900;color:#1e3a8a;">{user["name"]}</div>
            <div style="font-size:13px;color:#1d4ed8;font-weight:700;">Member since {user.get("joined","—")}</div>
        </div>
    </div>
    <div class="info-grid-2">
        <div class="info-cell"><div class="info-lbl">Full name</div>  <div class="info-val">{user.get("name","—")}</div></div>
        <div class="info-cell"><div class="info-lbl">Gmail ID</div>   <div class="info-val">{user.get("email","—")}</div></div>
        <div class="info-cell"><div class="info-lbl">Age</div>        <div class="info-val">{user.get("age","—")}</div></div>
        <div class="info-cell"><div class="info-lbl">Gender</div>     <div class="info-val">{user.get("gender","—")}</div></div>
        <div class="info-cell"><div class="info-lbl">Blood group</div><div class="info-val">{user.get("blood","—")}</div></div>
        <div class="info-cell"><div class="info-lbl">Phone</div>      <div class="info-val">{user.get("phone","—")}</div></div>
        <div class="info-cell"><div class="info-lbl">Height</div>     <div class="info-val">{user.get("height","—")} cm</div></div>
        <div class="info-cell"><div class="info-lbl">Weight</div>     <div class="info-val">{user.get("weight","—")} kg</div></div>
        <div class="info-cell" style="grid-column:span 2;">
            <div class="info-lbl">BMI</div>
            <div class="info-val" style="color:{bmi_col}!important;">{bmi} &nbsp;·&nbsp; {bmi_cat}</div>
        </div>
    </div>""",unsafe_allow_html=True)

    st.write("")
    c1,c2=st.columns([1,3])
    with c1:
        if st.button("✏️ Edit profile",use_container_width=True): go("edit_profile")
    with c2:
        if st.button("← Back to home",use_container_width=True): go("home")

# ═══════════════════════════════════════════════════════════════════════════════
# PAST HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
def page_past_history():
    set_bg("#eef5ff"); navbar()
    st.markdown('<div class="page-title">📋 Past history</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Your previous symptom assessments</div>',unsafe_allow_html=True)
    history=st.session_state.past_history
    if not history:
        st.markdown("""<div style="text-align:center;padding:3rem 1rem;background:#fff;border-radius:16px;
            border:2px dashed #93c5fd;margin-top:1rem;">
            <div style="font-size:52px;margin-bottom:0.75rem;">📭</div>
            <div style="font-size:18px;font-weight:800;color:#1d4ed8;">Nothing as of now</div>
            <div style="font-size:14px;color:#374151;font-weight:700;margin-top:6px;">Run a triage assessment to see your history here</div>
        </div>""",unsafe_allow_html=True)
    else:
        for h in history:
            badge="badge-danger" if "Emergency" in h["level"] else ("badge-warn" if "In-person" in h["level"] else "badge-safe")
            st.markdown(f"""<div class="hist-card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                    <div>
                        <div style="font-size:15px;font-weight:900;color:#1d4ed8;">{h["emoji"]} {h["level"]}</div>
                        <div style="font-size:13px;color:#374151;font-weight:600;margin-top:4px;">🤒 {h["symptoms"]}</div>
                        <div style="font-size:13px;color:#374151;font-weight:600;">📊 Risk score: <b>{h["score"]} / 100</b></div>
                    </div>
                    <span class="{badge}">{h["date"]}</span>
                </div>
            </div>""",unsafe_allow_html=True)
    st.write("")
    if st.button("← Back to home"): go("home")
    footer()

# ═══════════════════════════════════════════════════════════════════════════════
# PAST CONSULTATIONS — with delete
# ═══════════════════════════════════════════════════════════════════════════════
def page_past_consults():
    set_bg("#eef5ff"); navbar()
    st.markdown('<div class="page-title">📅 Past consultations</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Your previous doctor consultations</div>',unsafe_allow_html=True)
    consults=st.session_state.past_consults
    if not consults:
        st.markdown("""<div style="text-align:center;padding:3rem 1rem;background:#fff;border-radius:16px;
            border:2px dashed #93c5fd;margin-top:1rem;">
            <div style="font-size:52px;margin-bottom:0.75rem;">🗓️</div>
            <div style="font-size:18px;font-weight:800;color:#1d4ed8;">No consultations yet</div>
            <div style="font-size:14px;color:#374151;font-weight:700;margin-top:6px;">Book a consultation with a doctor from the home screen</div>
        </div>""",unsafe_allow_html=True)
    else:
        to_delete=None
        for idx,c in enumerate(consults):
            badge="badge-booked" if "Booked" in c["result"] else ("badge-safe" if "Safe" in c["result"] else ("badge-danger" if "Emergency" in c["result"] else "badge-warn"))
            score_disp=f"{c['score']} / 100" if isinstance(c.get("score"),int) else c.get("score","—")
            em=c.get("emoji","👨‍⚕️"); clr=c.get("color","#e3f2fd")
            col1,col2=st.columns([5,1])
            with col1:
                st.markdown(f"""<div class="hist-card" style="display:flex;align-items:center;gap:1rem;">
                    <div style="width:56px;height:56px;border-radius:50%;background:{clr};
                                display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">{em}</div>
                    <div style="flex:1;">
                        <div style="font-size:15px;font-weight:900;color:#1d4ed8;">{c["doctor"]}</div>
                        <div style="font-size:12px;color:#374151;font-weight:600;">{c["spec"]} · {c["date"]}</div>
                        <div style="font-size:12px;color:#374151;font-weight:600;">Risk score: <b>{score_disp}</b></div>
                    </div>
                    <span class="{badge}">{c["result"]}</span>
                </div>""",unsafe_allow_html=True)
            with col2:
                st.write(""); st.write("")
                if st.button("🗑️ Delete",key=f"del_{idx}",use_container_width=True):
                    to_delete=idx
        if to_delete is not None:
            st.session_state.past_consults.pop(to_delete)
            st.success("Booking deleted."); st.rerun()
    st.write("")
    if st.button("← Back to home"): go("home")
    footer()

# ═══════════════════════════════════════════════════════════════════════════════
# AVAILABLE DOCTORS
# ═══════════════════════════════════════════════════════════════════════════════
def page_doctors():
    set_bg("#eef5ff"); navbar()
    st.markdown('<div class="page-title">🩺 Available doctors</div>', unsafe_allow_html=True)

    # ── Get location via streamlit-js-eval if installed ─────────────────────
    loc = None
    try:
        from streamlit_js_eval import get_geolocation
        loc = get_geolocation()
    except Exception:
        loc = None

    # Get lat/lng either from js-eval or from session state (manual entry)
    if "user_lat" not in st.session_state: st.session_state["user_lat"] = ""
    if "user_lng" not in st.session_state: st.session_state["user_lng"] = ""

    if loc:
        lat = str(round(float(loc["coords"]["latitude"]),  5))
        lng = str(round(float(loc["coords"]["longitude"]), 5))
        st.session_state["user_lat"] = lat
        st.session_state["user_lng"] = lng
    else:
        lat = st.session_state["user_lat"]
        lng = st.session_state["user_lng"]

    if not lat:
        st.markdown("""
        <div style="background:#fffbeb;border-radius:12px;padding:1rem 1.25rem;border:1.5px solid #fcd34d;margin-bottom:1rem;">
            <div style="font-size:14px;font-weight:800;color:#92400e;">📍 Enter your city to find nearby doctors</div>
        </div>""", unsafe_allow_html=True)
        city_in = st.text_input("Your city:", placeholder="e.g. Bengaluru, Chennai, Delhi")
        if city_in and st.button("Find doctors →", type="primary", key="city_btn"):
            import requests as _rq
            try:
                g = _rq.get(f"https://nominatim.openstreetmap.org/search?q={city_in}&format=json&limit=1",
                            headers={"User-Agent":"TELEMED"}, timeout=5).json()
                if g:
                    st.session_state["user_lat"] = str(round(float(g[0]["lat"]),5))
                    st.session_state["user_lng"] = str(round(float(g[0]["lon"]),5))
                    st.rerun()
                else:
                    st.error("City not found, try again.")
            except Exception:
                st.error("Network error. Try a different city name.")
        st.write("")
        if st.button("← Back to home", key="doc_back_err"): go("home")
        footer()
        return

    if lat:
        st.markdown(f"""
        <div style="background:#d1fae5;border-radius:12px;padding:0.9rem 1.5rem;
                    border:1.5px solid #6ee7b7;margin-bottom:1rem;">
            <div style="font-size:14px;font-weight:800;color:#065f46;">
                ✅ Location set ({lat}, {lng}) — showing real doctors near you
            </div>
        </div>""", unsafe_allow_html=True)

        # Coords are in Python — show cards directly + links
        import requests as _rq

        # Reverse geocode to get city
        city = "Bengaluru"
        try:
            _r = _rq.get(
                f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json",
                headers={"User-Agent":"TELEMED/1.0"}, timeout=5
            )
            _a = _r.json().get("address",{})
            city = _a.get("city") or _a.get("town") or _a.get("village") or _a.get("suburb") or _a.get("state") or "your area"
        except Exception:
            pass

        st.markdown(f'<div style="font-size:14px;font-weight:800;color:#1d4ed8;margin-bottom:0.75rem;">📍 Real doctors near <b>{city}</b></div>', unsafe_allow_html=True)

        # Fetch from Overpass
        docs_found = []
        try:
            q = f"""[out:json][timeout:20];(
              node["amenity"="doctors"](around:5000,{lat},{lng});
              node["amenity"="clinic"](around:5000,{lat},{lng});
              node["amenity"="hospital"](around:5000,{lat},{lng});
              node["healthcare"="doctor"](around:5000,{lat},{lng});
            );out body 10;"""
            _resp = _rq.post("https://overpass-api.de/api/interpreter", data=q, timeout=20)
            docs_found = _resp.json().get("elements",[])[:8]
        except Exception:
            pass

        COLORS = ["#fce4ec","#e3f2fd","#e8f5e9","#fff8e1","#f3e5f5","#e0f7fa"]
        EMOJIS = ["👩\u200d⚕️","👨\u200d⚕️","👩\u200d⚕️","👨\u200d⚕️","👩\u200d⚕️","👨\u200d⚕️"]

        if docs_found:
            st.success(f"Found {len(docs_found)} doctors near {city}!")
            for i, node in enumerate(docs_found):
                t = node.get("tags",{})
                name  = t.get("name") or t.get("operator","Clinic")
                spec  = (t.get("healthcare:speciality") or t.get("amenity","General")).replace(";"," · ").replace("_"," ").title()
                addr  = ", ".join(filter(None,[t.get("addr:housenumber",""),t.get("addr:street",""),t.get("addr:city") or t.get("addr:suburb","") or city]))
                phone = t.get("phone") or t.get("contact:phone","")
                nlat  = node.get("lat",lat); nlng = node.get("lon",lng)
                # Link opens Google Maps centred on this exact doctor/clinic location
                mlink      = f"https://www.google.com/maps/search/?api=1&query={name.replace(chr(32),'+')}&query_place_id=&center={nlat},{nlng}"
                dir_link   = f"https://www.google.com/maps/dir/?api=1&destination={nlat},{nlng}&destination_place_id="
                embed_link = f"https://maps.google.com/maps?q={nlat},{nlng}&z=16&output=embed"
                parts_html = ""
                if addr:  parts_html += f'<div style="font-size:11px;color:#374151;margin-top:2px;font-weight:600;">📌 {addr}</div>'
                if phone: parts_html += f'<div style="font-size:11px;color:#374151;margin-top:2px;font-weight:600;">📞 {phone}</div>'
                card_html = (
                    f'<div style="background:#ffffff;border:1.5px solid #bfdbfe;border-radius:14px;'
                    f'padding:14px 16px;margin-bottom:12px;">'
                    f'<div style="display:flex;gap:14px;align-items:flex-start;">'
                    f'<div style="width:52px;height:52px;border-radius:50%;background:{COLORS[i%6]};'
                    f'display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">{EMOJIS[i%6]}</div>'
                    f'<div style="flex:1;">'
                    f'<div style="font-size:15px;font-weight:900;color:#1d4ed8;">{name}</div>'
                    f'<div style="font-size:12px;color:#374151;font-weight:600;margin-top:2px;">{spec}</div>'
                    f'{parts_html}'
                    f'<div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:8px;">'
                    f'<a href="{mlink}" target="_blank" style="font-size:12px;color:#2563eb;font-weight:800;text-decoration:none;">📍 View on Maps</a>'
                    f'<a href="{dir_link}" target="_blank" style="font-size:12px;color:#059669;font-weight:800;text-decoration:none;">🧭 Get directions</a>'
                    f'</div></div></div>'
                    f'<iframe src="{embed_link}" width="100%" height="160" '
                    f'style="border:none;border-radius:10px;margin-top:10px;display:block;" '
                    f'loading="lazy"></iframe>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

                # Book consultation button
                if "expanded_hosp" not in st.session_state:
                    st.session_state["expanded_hosp"] = None
                if st.button(f"📅 Book consultation at {name[:35]}", key=f"book_hosp_{i}", use_container_width=True):
                    st.session_state["expanded_hosp"] = None if st.session_state["expanded_hosp"] == i else i
                    st.rerun()

                if st.session_state.get("expanded_hosp") == i:
                    st.markdown(f'<div style="background:#f0f7ff;border-radius:12px;padding:1rem 1.25rem;border:1.5px solid #bfdbfe;margin-bottom:0.5rem;"><div style="font-size:14px;font-weight:900;color:#1d4ed8;margin-bottom:0.75rem;">👨\u200d⚕️ Available doctors at {name}</div></div>', unsafe_allow_html=True)
                    import random as _rand
                    SPECS2 = ["General Physician","Cardiologist","Dermatologist","Orthopaedic","Gynaecologist","Pulmonologist","ENT Specialist","Neurologist"]
                    DNAMES = ["Dr. Arun Kumar","Dr. Priya Sharma","Dr. Rahul Mehta","Dr. Sunita Reddy","Dr. Vikram Nair","Dr. Kavya Iyer"]
                    SLOTS  = ["9AM–12PM","11AM–2PM","2PM–5PM","4PM–7PM","10AM–1PM"]
                    _rand.seed(i * 13)
                    for di in range(_rand.randint(3,5)):
                        dname  = DNAMES[(i+di) % len(DNAMES)]
                        dspec  = SPECS2[(i+di*2) % len(SPECS2)]
                        dslot  = SLOTS[di % len(SLOTS)]
                        davail = (di % 3 != 2)
                        badge  = ('<span style="background:#d1fae5;color:#065f46;font-size:11px;font-weight:800;padding:2px 8px;border-radius:99px;">🟢 Available</span>'
                                  if davail else
                                  '<span style="background:#fee2e2;color:#991b1b;font-size:11px;font-weight:800;padding:2px 8px;border-radius:99px;">🔴 Fully booked</span>')
                        dc1,dc2 = st.columns([4,1])
                        with dc1:
                            st.markdown(
                                f'<div style="background:#fff;border:1.5px solid #bfdbfe;border-radius:10px;padding:10px 14px;margin-bottom:8px;">'+
                                f'<div style="font-size:14px;font-weight:900;color:#1d4ed8;">{dname}</div>'+
                                f'<div style="font-size:12px;color:#374151;font-weight:600;">{dspec} · {dslot}</div>'+
                                f'<div style="margin-top:4px;">{badge}</div></div>',
                                unsafe_allow_html=True)
                        with dc2:
                            st.write("")
                            if davail:
                                if st.button("Book", key=f"bk_{i}_{di}", type="primary", use_container_width=True):
                                    st.session_state.past_consults.insert(0,{
                                        "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                                        "doctor":dname,"spec":dspec,
                                        "result":"Booked — pending","score":"—",
                                        "emoji":"👨\u200d⚕️","color":COLORS[i%6],
                                    })
                                    st.success(f"✅ Booked with {dname}!")
                                    st.session_state["expanded_hosp"]=None
                                    st.rerun()
                            else:
                                st.button("Full",key=f"bk_{i}_{di}",disabled=True,use_container_width=True)

        else:
            st.markdown(f"""
            <div style="background:#fff;border:1.5px solid #bfdbfe;border-radius:12px;padding:16px;margin-top:0.5rem;">
                <div style="font-size:14px;font-weight:800;color:#1d4ed8;margin-bottom:10px;">
                    No map data for {city} — search here:
                </div>
                <a href="https://www.practo.com" target="_blank"
                   style="display:block;font-size:14px;font-weight:800;color:#7c3aed;margin-bottom:10px;text-decoration:none;">
                   🩺 Practo — Book doctors online
                </a>
                <a href="https://www.google.com/maps/search/doctor+near+me/@{lat},{lng},14z" target="_blank"
                   style="display:block;font-size:14px;font-weight:800;color:#2563eb;text-decoration:none;">
                   🗺️ Google Maps — doctors near me
                </a>
            </div>""", unsafe_allow_html=True)


    else:
        # streamlit-js-eval not installed or waiting — show install instructions + manual fallback
        st.markdown("""
        <div style="background:#fee2e2;border-radius:12px;padding:1rem 1.5rem;
                    border:1.5px solid #fca5a5;margin-bottom:1rem;">
            <div style="font-size:14px;font-weight:900;color:#991b1b;margin-bottom:6px;">
                ⚠️ One-time setup required
            </div>
            <div style="font-size:13px;color:#7f1d1d;font-weight:700;">
                Run this in your terminal then restart the app:
            </div>
            <div style="background:#1e1e1e;color:#4ade80;font-family:monospace;font-size:13px;
                        padding:8px 12px;border-radius:8px;margin-top:8px;">
                py -m pip install streamlit-js-eval
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("**While you install, search manually:**")
        city_input = st.text_input("Enter your city name:", placeholder="e.g. Bengaluru, Delhi, Mumbai")
        if city_input and st.button("Search doctors →", type="primary"):
            import streamlit.components.v1 as components
            q = city_input.replace(" ","+")
            components.html(f"""<!DOCTYPE html><html><head><style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:sans-serif;background:transparent;padding:2px;}}
#status{{font-size:14px;font-weight:700;color:#1d4ed8;padding:8px 0 12px;}}
.card{{background:#fff;border:1.5px solid #bfdbfe;border-radius:12px;padding:12px 14px;margin-bottom:10px;display:flex;gap:12px;}}
.av{{width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;}}
.nm{{font-size:14px;font-weight:900;color:#1d4ed8;}}
.sp{{font-size:12px;color:#374151;font-weight:600;margin-top:2px;}}
.ad{{font-size:11px;color:#6b7280;margin-top:2px;}}
.ml{{font-size:12px;color:#059669;font-weight:700;text-decoration:none;display:block;margin-top:6px;}}
</style></head><body>
<div id="status">🔍 Searching for doctors in {city_input}...</div>
<div id="list"></div>
<script>
var BG=["#fce4ec","#e3f2fd","#e8f5e9","#fff8e1","#f3e5f5","#e0f7fa"];
var EM=["👩\u200d⚕️","👨\u200d⚕️","👩\u200d⚕️","👨\u200d⚕️","👩\u200d⚕️","👨\u200d⚕️"];
fetch("https://nominatim.openstreetmap.org/search?q={q}&format=json&limit=1",{{headers:{{"User-Agent":"TELEMED"}}}})
.then(r=>r.json()).then(res=>{{
  if(!res.length){{document.getElementById("status").innerHTML="City not found.";return;}}
  var LA=parseFloat(res[0].lat),LO=parseFloat(res[0].lon);
  document.getElementById("status").innerHTML="📍 Found {city_input}. Loading doctors...";
  var q2="[out:json][timeout:25];(node[\"amenity\"=\"doctors\"](around:5000,"+LA+","+LO+");node[\"amenity\"=\"clinic\"](around:5000,"+LA+","+LO+");node[\"amenity\"=\"hospital\"](around:5000,"+LA+","+LO+");node[\"healthcare\"=\"doctor\"](around:5000,"+LA+","+LO+"););out body 12;";
  fetch("https://overpass-api.de/api/interpreter",{{method:"POST",body:q2}})
  .then(r=>r.json()).then(d=>{{
    var nodes=(d.elements||[]).slice(0,8);
    if(!nodes.length){{document.getElementById("status").innerHTML='No data. <a href="https://www.google.com/maps/search/doctor+{q}" target="_blank" style="color:#2563eb;font-weight:800;">Search on Google Maps →</a>';return;}}
    document.getElementById("status").innerHTML="<b>"+nodes.length+" doctors found in {city_input}</b>";
    var list=document.getElementById("list");
    nodes.forEach(function(n,i){{
      var t=n.tags||{{}};
      var name=t.name||t.operator||"Clinic";
      var spec=(t["healthcare:speciality"]||t.amenity||"General").replace(/;/g," · ").replace(/_/g," ");
      var addr=[t["addr:housenumber"],t["addr:street"],t["addr:city"]||t["addr:suburb"]||"{city_input}"].filter(Boolean).join(", ");
      var phone=t.phone||t["contact:phone"]||"";
      var ml="https://www.google.com/maps?q="+encodeURIComponent(name)+"&ll="+(n.lat||LA)+","+(n.lon||LO);
      var c=document.createElement("div");c.className="card";
      c.innerHTML='<div class="av" style="background:'+BG[i%6]+'">'+EM[i%6]+'</div>'
        +'<div style="flex:1"><div class="nm">'+name+'</div>'
        +'<div class="sp">'+spec.charAt(0).toUpperCase()+spec.slice(1)+'</div>'
        +(addr?'<div class="ad">📌 '+addr+'</div>':"")
        +(phone?'<div class="ad">📞 '+phone+'</div>':"")
        +'<a class="ml" href="'+ml+'" target="_blank">📍 View on Google Maps →</a>'
        +'</div>';
      list.appendChild(c);
    }});
  }}).catch(()=>{{document.getElementById("status").innerHTML='<a href="https://www.google.com/maps/search/doctor+{q}" target="_blank" style="color:#2563eb;font-weight:800;">Open Google Maps doctors in {city_input} →</a>';}});
}}).catch(()=>{{document.getElementById("status").innerHTML="Error. Try again.";}});
</script></body></html>""", height=1200)

    st.write("")
    if st.button("← Back to home", key="doc_back"): go("home")
    footer()

def _render_doc_list(docs, lat, lng, prefix):
    COLORS = ["#fce4ec","#e3f2fd","#e8f5e9","#fff8e1","#f3e5f5","#e0f7fa"]
    for i, doc in enumerate(docs):
        name     = doc.get("name","")
        spec     = doc.get("spec","")
        hospital = doc.get("hospital","")
        address  = doc.get("address", doc.get("hospital",""))
        exp      = doc.get("exp","")
        avail    = doc.get("available", True)
        slot     = doc.get("slot","Available")
        emoji    = doc.get("emoji","\U0001f468\u200d\u2695\ufe0f")
        clr      = doc.get("color", COLORS[i % len(COLORS)])
        avail_html = (
            f'<span style="color:#065f46;font-size:12px;font-weight:800;">🟢 {slot}</span>'
            if avail else
            '<span style="color:#991b1b;font-size:12px;font-weight:800;">🔴 Fully booked</span>'
        )
        c1, c2, c3 = st.columns([5,1,1])
        with c1:
            st.markdown(f"""<div class="hist-card" style="display:flex;align-items:center;gap:1rem;">
                <div style="width:56px;height:56px;border-radius:50%;background:{clr};
                    display:flex;align-items:center;justify-content:center;font-size:26px;flex-shrink:0;">{emoji}</div>
                <div>
                    <div style="font-size:15px;font-weight:900;color:#1d4ed8;">{name}</div>
                    <div style="font-size:12px;color:#374151;font-weight:600;">{spec}{(" · "+exp) if exp else ""}</div>
                    <div style="font-size:12px;color:#374151;font-weight:600;margin-top:2px;">🏥 {hospital}</div>
                    <div style="margin-top:4px;">{avail_html}</div>
                </div></div>""", unsafe_allow_html=True)
        with c2:
            st.write(""); st.write("")
            if st.button("Info", key=f"{prefix}_info_{i}", use_container_width=True):
                cur = st.session_state.get("selected_doctor")
                st.session_state.selected_doctor = None if cur == f"{prefix}_{i}" else f"{prefix}_{i}"
                st.rerun()
        with c3:
            st.write(""); st.write("")
            if avail:
                if st.button("Book", key=f"{prefix}_d{i}", use_container_width=True, type="primary"):
                    already = [x["doctor"] for x in st.session_state.past_consults if "pending" in x.get("result","")]
                    if name in already:
                        st.warning(f"Already booked with {name}.")
                    else:
                        st.session_state.past_consults.insert(0, {
                            "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                            "doctor": name, "spec": spec,
                            "result": "Booked - pending", "score": "--",
                            "emoji": emoji, "color": clr,
                        })
                        st.success(f"Booked with {name}!")
            else:
                st.button("Full", key=f"{prefix}_d{i}", disabled=True, use_container_width=True)

        if st.session_state.get("selected_doctor") == f"{prefix}_{i}":
            spec_slug  = spec.replace(" ","+")
            addr_slug  = address.replace(" ","+").replace(",","+")
            hosp_link  = (f"https://www.google.com/maps/search/{addr_slug}/@{lat},{lng},15z"
                          if lat else doc.get("hospital_map", f"https://www.google.com/maps/search/{addr_slug}"))
            near_link  = (f"https://www.google.com/maps/search/{spec_slug}+doctor/@{lat},{lng},14z"
                          if lat else f"https://www.google.com/maps/search/{spec_slug}+doctor+near+me")
            loc_note   = f"Near your location ({lat}, {lng})" if lat else "Enable location for personalised results"
            qual  = doc.get("qual","")
            lang  = doc.get("lang","")
            about = doc.get("about", doc.get("bio",""))
            st.markdown(f"""
            <div class="doc-info-panel">
                <div style="font-size:16px;font-weight:900;color:#1d4ed8;margin-bottom:0.75rem;">{emoji} {name}</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:0.75rem;">
                    <div class="info-cell"><div class="info-lbl">Specialisation</div><div class="info-val">{spec}</div></div>
                    <div class="info-cell"><div class="info-lbl">Experience</div><div class="info-val">{exp}</div></div>
                    <div class="info-cell"><div class="info-lbl">Languages</div><div class="info-val" style="font-size:13px!important;">{lang}</div></div>
                    <div class="info-cell"><div class="info-lbl">Qualifications</div><div class="info-val" style="font-size:12px!important;">{qual}</div></div>
                </div>
                <div class="info-cell" style="margin-bottom:0.75rem;">
                    <div class="info-lbl">About</div>
                    <div style="font-size:13px;color:#374151;font-weight:600;margin-top:4px;line-height:1.7;">{about}</div>
                </div>
                <div class="info-cell">
                    <div class="info-lbl">Hospital and address</div>
                    <div style="font-size:13px;font-weight:800;color:#1d4ed8;margin-top:4px;">🏥 {hospital}</div>
                    <div style="font-size:12px;color:#374151;margin-top:2px;">📌 {address}</div>
                    <div style="font-size:11px;color:#6b7280;margin-top:2px;">{loc_note}</div>
                    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:8px;">
                        <a href="{hosp_link}" target="_blank" style="font-size:12px;color:#2563eb;font-weight:800;text-decoration:none;">View on Google Maps</a>
                        <a href="{near_link}" target="_blank" style="font-size:12px;color:#059669;font-weight:800;text-decoration:none;">More {spec} doctors near me</a>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
# ═══════════════════════════════════════════════════════════════════════════════
# ABOUT US
# ═══════════════════════════════════════════════════════════════════════════════
def page_about():
    set_bg("#eef5ff"); navbar()
    st.markdown('<div class="page-title">About TELEMED</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Team TELEMED - Healathon 2026</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#ffffff;border-radius:18px;padding:2rem;border:1.5px solid #bfdbfe;
                box-shadow:0 4px 18px rgba(29,78,216,0.07);margin-bottom:1.5rem;">
        <div style="font-size:18px;font-weight:900;color:#1d4ed8;margin-bottom:0.75rem;">What is TELEMED?</div>
        <div style="font-size:14px;color:#111111;line-height:1.9;font-weight:600;">
            <b>TELEMED</b> is a Smart Telemedicine Triage Engine developed for Healathon 2026.
            It evaluates patient symptoms, severity, medical history, surgical background, age, and BMI
            to compute a personalised risk score and recommend the right care pathway —
            teleconsultation, in-person visit, or emergency care.
        </div>
    </div>
    <div style="background:#ffffff;border-radius:18px;padding:2rem;border:1.5px solid #bfdbfe;
                box-shadow:0 4px 18px rgba(29,78,216,0.07);margin-bottom:1.5rem;">
        <div style="font-size:18px;font-weight:900;color:#1d4ed8;margin-bottom:0.75rem;">Our mission</div>
        <div style="font-size:14px;color:#111111;line-height:1.9;font-weight:600;">
            To make telemedicine safer, smarter, and more equitable — ensuring every patient gets the
            right type of care at the right time, whether in a metro city or a remote village.
        </div>
    </div>
    <div style="background:#ffffff;border-radius:18px;padding:2rem;border:1.5px solid #bfdbfe;
                box-shadow:0 4px 18px rgba(29,78,216,0.07);margin-bottom:1.5rem;">
        <div style="font-size:18px;font-weight:900;color:#1d4ed8;margin-bottom:0.75rem;">Why it matters</div>
        <div style="font-size:14px;color:#111111;line-height:1.9;font-weight:600;">
            India has over <b>1.4 billion people</b> and a doctor-to-patient ratio far below WHO recommendations.
            Telemedicine surged post-COVID but brought risks — patients booking video calls instead of going to
            emergency rooms. TELEMED acts as an intelligent gatekeeper, ensuring only appropriate cases proceed remotely.
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="background:#ffffff;border-radius:18px;padding:2rem;border:1.5px solid #bfdbfe;box-shadow:0 4px 18px rgba(29,78,216,0.07);margin-bottom:1.5rem;"><div style="font-size:18px;font-weight:900;color:#1d4ed8;margin-bottom:1rem;">Meet the team</div></div>', unsafe_allow_html=True)
    team=[("Aditi Naveen Sajjan","CSE 2nd Semester"),
          ("Aishwarya Mohan Kumar","AIML 2nd Semester"),
          ("J Sharrel Angela","CSE 2nd Semester")]
    cols=st.columns(3)
    for col,(name,dept) in zip(cols,team):
        with col:
            st.markdown(f"""<div style="background:#eff6ff;border-radius:14px;padding:1.5rem;text-align:center;border:1.5px solid #bfdbfe;">
                <div style="font-size:40px;margin-bottom:0.5rem;">👩‍💻</div>
                <div style="font-size:15px;font-weight:900;color:#1d4ed8;">{name}</div>
                <div style="font-size:12px;color:#374151;font-weight:700;margin-top:4px;">{dept}</div>
                <div style="font-size:11px;color:#6b7280;font-weight:600;margin-top:2px;">Healathon 2026</div>
            </div>""", unsafe_allow_html=True)
    st.write("")
    if st.button("Back to home", key="about_back"): go("home")
# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in and st.session_state.page != "login":
    st.session_state.page = "login"

p = st.session_state.page
if   p == "login":        page_login()
elif p == "edit_profile": page_login(edit_mode=True)
elif p == "home":         page_home()
elif p == "triage":       page_triage()
elif p == "user_info":    page_user_info()
elif p == "past_history": page_past_history()
elif p == "past_consults":page_past_consults()
elif p == "doctors":      page_doctors()
elif p == "about":        page_about()
