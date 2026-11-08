import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import base64
import json
import io
import warnings
warnings.filterwarnings('ignore')

# Penanganan opsional untuk ReportLab
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

# ==========================================
# 1. KONFIGURASI HALAMAN & EXECUTIVE DESIGN SYSTEM
# ==========================================
st.set_page_config(
    page_title="EcoBuild Pro - Civil Carbon & Cost Intelligence",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_image_base64(fname):
    if not fname or not os.path.exists(fname):
        return None
    ext = fname.split('.')[-1].lower()
    mime = "image/jpeg"
    if ext == "avif":
        mime = "image/avif"
    elif ext == "png":
        mime = "image/png"
    elif ext == "webp":
        mime = "image/webp"
        
    try:
        with open(fname, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:{mime};base64,{data}"
    except Exception:
        return None

def get_existing_image(filename_list):
    for fname in filename_list:
        if fname and os.path.exists(fname):
            return fname
    return None

bg_file = get_existing_image([
    "bg_green_building.avif", 
    "bg_green_building.jpg", 
    "bg_green_building.jpeg", 
    "bg_green_building.png"
])

bg_base64_url = get_image_base64(bg_file)
if not bg_base64_url:
    bg_base64_url = "https://images.unsplash.com/photo-1541888946425-d0fbb186a5b3?q=80&w=1200"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    :root {{
        --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        --color-emerald-900: #064e3b;
        --color-emerald-700: #047857;
        --color-emerald-500: #10b981;
        --color-emerald-100: #d1fae5;
        --color-emerald-50:  #ecfdf5;
        
        --color-amber-600:   #d97706;
        --color-amber-500:   #f59e0b;
        --color-amber-100:   #fef3c7;
        --color-amber-50:    #fffbeb;
        
        --color-rose-600:    #e11d48;
        --color-rose-500:    #ef4444;
        --color-rose-100:    #fee2e2;
        --color-rose-50:     #fef2f2;
        
        --color-blue-600:    #2563eb;
        --color-blue-100:    #dbeafe;
        --color-blue-50:     #eff6ff;
        
        --color-slate-900:   #0f172a;
        --color-slate-800:   #1e293b;
        --color-slate-700:   #334155;
        --color-slate-600:   #475569;
        --color-slate-400:   #94a3b8;
        --color-slate-200:   #e2e8f0;
        --color-slate-100:   #f1f5f9;
        --color-slate-50:    #f8fafc;
    }}
    
    html, body, [class*="css"] {{
        font-family: var(--font-sans);
        color: var(--color-slate-800);
    }}
    
    /* Top Main App Padding & Spacing */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 3.5rem !important;
    }}

    /* ==========================================
       HERO BANNER (EKSEKUTIF)
       ========================================== */
    .hero-container {{
        position: relative;
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.94) 0%, rgba(15, 23, 42, 0.92) 100%), 
                    url('{bg_base64_url}');
        background-size: cover;
        background-position: center;
        padding: 48px 36px;
        border-radius: 20px;
        color: #ffffff !important;
        margin-bottom: 28px;
        box-shadow: 0 16px 36px -10px rgba(6, 78, 59, 0.35), 0 8px 16px -6px rgba(0,0,0,0.15);
        border: 1px solid rgba(255, 255, 255, 0.12);
        overflow: hidden;
    }}
    .hero-badge {{
        background: rgba(16, 185, 129, 0.22);
        color: #6ee7b7 !important;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 16px;
        border: 1px solid rgba(110, 231, 183, 0.35);
        backdrop-filter: blur(8px);
    }}
    .hero-title {{
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 10px;
        letter-spacing: -0.8px;
        color: #ffffff !important;
        line-height: 1.2;
    }}
    .hero-subtitle {{
        font-size: 1.05rem;
        color: #e2e8f0 !important;
        max-width: 860px;
        font-weight: 400;
        line-height: 1.6;
        margin-bottom: 16px;
    }}
    .hero-chips-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 14px;
    }}
    .hero-chip {{
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #f1f5f9;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }}

    /* ==========================================
       KARTU MATRIKS EMISI (EXECUTIVE KPI CARDS)
       ========================================== */
    .exec-metrics-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 20px;
        margin: 24px 0;
    }}
    
    .exec-metric-card {{
        background: #ffffff;
        border-radius: 18px;
        padding: 24px;
        position: relative;
        border: 1px solid var(--color-slate-200);
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.06), 0 8px 10px -6px rgba(15, 23, 42, 0.03);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        overflow: hidden;
    }}
    
    .exec-metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 20px 30px -10px rgba(15, 23, 42, 0.12), 0 10px 10px -5px rgba(15, 23, 42, 0.04);
    }}

    /* Variasi Warna Status Emisi */
    .exec-metric-card.status-optimal {{
        border-top: 5px solid var(--color-emerald-500);
        background: linear-gradient(180deg, #ffffff 0%, var(--color-emerald-50) 100%);
        box-shadow: 0 12px 28px -5px rgba(16, 185, 129, 0.18), 0 4px 6px -2px rgba(0,0,0,0.03);
    }}
    .exec-metric-card.status-optimal:hover {{
        border-color: var(--color-emerald-500);
        box-shadow: 0 18px 36px -5px rgba(16, 185, 129, 0.28);
    }}

    .exec-metric-card.status-moderate {{
        border-top: 5px solid var(--color-amber-500);
        background: linear-gradient(180deg, #ffffff 0%, var(--color-amber-50) 100%);
        box-shadow: 0 12px 28px -5px rgba(245, 158, 11, 0.18), 0 4px 6px -2px rgba(0,0,0,0.03);
    }}
    .exec-metric-card.status-moderate:hover {{
        border-color: var(--color-amber-500);
        box-shadow: 0 18px 36px -5px rgba(245, 158, 11, 0.28);
    }}

    .exec-metric-card.status-critical {{
        border-top: 5px solid var(--color-rose-500);
        background: linear-gradient(180deg, #ffffff 0%, var(--color-rose-50) 100%);
        box-shadow: 0 12px 28px -5px rgba(239, 68, 68, 0.18), 0 4px 6px -2px rgba(0,0,0,0.03);
    }}
    .exec-metric-card.status-critical:hover {{
        border-color: var(--color-rose-500);
        box-shadow: 0 18px 36px -5px rgba(239, 68, 68, 0.28);
    }}

    .exec-metric-card.theme-finance {{
        border-top: 5px solid var(--color-blue-600);
        background: linear-gradient(180deg, #ffffff 0%, var(--color-blue-50) 100%);
        box-shadow: 0 12px 28px -5px rgba(37, 99, 235, 0.14), 0 4px 6px -2px rgba(0,0,0,0.03);
    }}
    .exec-metric-card.theme-finance:hover {{
        border-color: var(--color-blue-600);
        box-shadow: 0 18px 36px -5px rgba(37, 99, 235, 0.24);
    }}

    .exec-metric-card.theme-efficiency {{
        border-top: 5px solid #7c3aed;
        background: linear-gradient(180deg, #ffffff 0%, #f5f3ff 100%);
        box-shadow: 0 12px 28px -5px rgba(124, 58, 237, 0.14), 0 4px 6px -2px rgba(0,0,0,0.03);
    }}
    .exec-metric-card.theme-efficiency:hover {{
        border-color: #7c3aed;
        box-shadow: 0 18px 36px -5px rgba(124, 58, 237, 0.24);
    }}

    .exec-card-head {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }}
    .exec-card-title-group {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .exec-card-icon {{
        font-size: 1.25rem;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 38px;
        border-radius: 11px;
        background: rgba(15, 23, 42, 0.04);
    }}
    .exec-card-title {{
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.7px;
        color: var(--color-slate-600);
    }}
    
    .exec-status-pill {{
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        letter-spacing: 0.4px;
        text-transform: uppercase;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }}
    .pill-optimal {{ background: var(--color-emerald-100); color: var(--color-emerald-900); border: 1px solid #86efac; }}
    .pill-moderate {{ background: var(--color-amber-100); color: #92400e; border: 1px solid #fde68a; }}
    .pill-critical {{ background: var(--color-rose-100); color: #991b1b; border: 1px solid #fca5a5; }}
    .pill-finance {{ background: var(--color-blue-100); color: #1e40af; border: 1px solid #93c5fd; }}
    .pill-efficiency {{ background: #ede9fe; color: #5b21b6; border: 1px solid #c4b5fd; }}

    .exec-card-value {{
        font-size: 2.1rem;
        font-weight: 800;
        color: var(--color-slate-900);
        letter-spacing: -0.6px;
        margin: 6px 0;
        line-height: 1.15;
    }}
    .exec-card-unit {{
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--color-slate-600);
        margin-left: 4px;
    }}
    .exec-card-subtext {{
        font-size: 0.82rem;
        color: var(--color-slate-600);
        margin-top: 10px;
        line-height: 1.45;
        border-top: 1px dashed rgba(148, 163, 184, 0.35);
        padding-top: 10px;
    }}

    /* Streamlit Native Metric Styling */
    div[data-testid="stMetric"] {{
        background: #ffffff;
        border: 1px solid var(--color-slate-200);
        border-radius: 16px;
        padding: 18px 22px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        transition: all 0.25s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        border-color: var(--color-emerald-500);
        box-shadow: 0 12px 24px -5px rgba(0, 0, 0, 0.08);
    }}
    div[data-testid="stMetricLabel"] {{
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        color: var(--color-slate-600) !important;
    }}
    div[data-testid="stMetricValue"] {{
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: var(--color-slate-900) !important;
    }}

    /* ==========================================
       SIDEBAR EKSEKUTIF YANG MENARIK & MODERN
       ========================================== */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #091319 0%, #0d1e27 60%, #081116 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.09) !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: #f1f5f9;
    }}
    .sidebar-brand-card {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 20px 16px;
        text-align: center;
        margin-bottom: 22px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(12px);
    }}
    .sidebar-logo-img {{
        max-width: 135px;
        margin: 0 auto 10px auto;
        display: block;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.35));
    }}
    .sidebar-brand-title {{
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffffff !important;
        letter-spacing: -0.4px;
        margin-bottom: 3px;
    }}
    .sidebar-brand-pill {{
        background: rgba(16, 185, 129, 0.18);
        color: #34d399 !important;
        border: 1px solid rgba(52, 211, 153, 0.35);
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 12px;
        border-radius: 20px;
        display: inline-block;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        margin-top: 4px;
    }}
    .sidebar-nav-label {{
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #94a3b8 !important;
        margin: 16px 0 10px 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    
    /* Navigation Radio Items Styling */
    div[data-testid="stRadio"] > div {{
        gap: 6px;
    }}
    div[data-testid="stRadio"] label {{
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 10px 14px !important;
        transition: all 0.2s ease;
        margin-bottom: 4px;
    }}
    div[data-testid="stRadio"] label:hover {{
        background: rgba(16, 185, 129, 0.12) !important;
        border-color: rgba(52, 211, 153, 0.3) !important;
        transform: translateX(3px);
    }}
    div[data-testid="stRadio"] label[data-checked="true"] {{
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.22) 0%, rgba(6, 78, 59, 0.15) 100%) !important;
        border-left: 4px solid #10b981 !important;
        border-color: rgba(52, 211, 153, 0.4) !important;
        font-weight: 700;
    }}

    .sidebar-status-box {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 14px 16px;
        margin-top: 18px;
    }}
    .sidebar-status-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.78rem;
        padding: 5px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }}
    .sidebar-status-row:last-child {{
        border-bottom: none;
    }}
    
    .sidebar-accreditation {{
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(6, 78, 59, 0.2));
        border: 1px solid rgba(52, 211, 153, 0.3);
        border-radius: 14px;
        padding: 14px 16px;
        margin-top: 18px;
    }}

    /* ==========================================
       MATERIAL INPUT FORM CARD & LAYOUT
       ========================================== */
    .mat-card-header-bar {{
        background: #f8fafc;
        border: 1px solid var(--color-slate-200);
        border-radius: 12px 12px 0 0;
        padding: 10px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 14px;
    }}
    .mat-card-pill {{
        background: linear-gradient(135deg, #064e3b, #047857);
        color: #ffffff;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
    }}
    .mat-card-body {{
        background: #ffffff;
        border: 1px solid var(--color-slate-200);
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
    }}
    .mat-subtotal-pill {{
        background: linear-gradient(90deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid var(--color-slate-200);
        border-radius: 8px;
        padding: 8px 14px;
        margin-top: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.82rem;
    }}

    /* Executive Buttons & Elements */
    .stButton > button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.08) !important;
    }}
    
    /* Tabs Navigation */
    button[data-baseweb="tab"] {{
        border-radius: 8px 8px 0 0 !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        padding: 10px 18px !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DYNAMIC EXCEL ICE DATABASE PARSER
# ==========================================
@st.cache_data
def load_ice_excel_database():
    excel_file = get_existing_image([
        os.path.join("ICE-Educational-V5.0-d2jkasdljwq2k", "ICE DB Educational V5.0 - Jun 2026.xlsx"),
        "ICE DB Educational V5.0 - Jun 2026.xlsx",
        "ICE DB Educational V5.0.xlsx",
        "ICE_Database.xlsx"
    ])
    
    if not excel_file or not os.path.exists(excel_file):
        default_ver = "Educational (V5.0) - Standar Default"
        default_df = pd.DataFrame([
            {"Kategori": "Concrete", "Nama Material": "Beton K-300 (Konvensional)", "Faktor Emisi (kg CO2e/kg)": 0.134, "Satuan": "kg"},
            {"Kategori": "Steel", "Nama Material": "Baja Tulangan (Konvensional)", "Faktor Emisi (kg CO2e/kg)": 1.990, "Satuan": "kg"},
            {"Kategori": "Timber", "Nama Material": "Kayu Olahan / Engineered Timber", "Faktor Emisi (kg CO2e/kg)": 0.300, "Satuan": "kg"},
            {"Kategori": "Clay Bricks", "Nama Material": "Bata Merah Press", "Faktor Emisi (kg CO2e/kg)": 0.240, "Satuan": "kg"},
        ])
        return default_ver, default_df

    try:
        xl = pd.ExcelFile(excel_file)
        sheet_target = "ICE Summary" if "ICE Summary" in xl.sheet_names else xl.sheet_names[0]
        df_raw = xl.parse(sheet_target)
        
        version_str = "Educational (V5.0) - Jun 2026"
        for row_idx in range(min(15, len(df_raw))):
            row_vals = [str(x).strip() for x in df_raw.iloc[row_idx].values if pd.notna(x)]
            for val in row_vals:
                if ("(V5." in val or "Jun 2026" in val or "Educational (V" in val) and len(val) < 40:
                    version_str = val
                    break
        
        materials_list = []
        current_cat = "General Construction Material"
        
        for idx in range(16, len(df_raw)):
            row = df_raw.iloc[idx]
            valid_vals = [x for x in row.values if pd.notna(x)]
            if not valid_vals:
                continue
                
            first_val = str(valid_vals[0]).strip()
            
            # Deteksi Kategori
            if len(valid_vals) == 1 and not first_val.startswith("http") and not first_val.startswith("Module") and not first_val.startswith("Note"):
                current_cat = first_val
                continue
                
            full_name = None
            if len(row) > 19 and pd.notna(row.iloc[19]):
                full_name = str(row.iloc[19]).strip()
            elif len(row) > 5 and pd.notna(row.iloc[5]):
                full_name = str(row.iloc[5]).strip()
                
            carbon_val = None
            if len(row) > 6 and isinstance(row.iloc[6], (int, float)) and pd.notna(row.iloc[6]):
                carbon_val = float(row.iloc[6])
            else:
                for v in valid_vals:
                    if isinstance(v, (int, float)) and 0.0001 <= v <= 100.0:
                        carbon_val = float(v)
                        break
                        
            if full_name and carbon_val is not None and not full_name.startswith("Name Exactly") and not full_name.startswith("Materials") and not full_name.startswith("Introduction"):
                materials_list.append({
                    "Kategori": current_cat,
                    "Nama Material": full_name,
                    "Faktor Emisi (kg CO2e/kg)": round(carbon_val, 6),
                    "Satuan": "kg"
                })
                
        df_out = pd.DataFrame(materials_list).drop_duplicates(subset=["Nama Material"])
        if df_out.empty:
            df_out = pd.DataFrame([
                {"Kategori": "Concrete", "Nama Material": "Beton K-300 (Konvensional)", "Faktor Emisi (kg CO2e/kg)": 0.134, "Satuan": "kg"},
                {"Kategori": "Steel", "Nama Material": "Baja Tulangan (Konvensional)", "Faktor Emisi (kg CO2e/kg)": 1.990, "Satuan": "kg"}
            ])
        return version_str, df_out
    except Exception as e:
        return "Educational (V5.0) - Jun 2026", pd.DataFrame([
            {"Kategori": "Concrete", "Nama Material": "Beton Standard", "Faktor Emisi (kg CO2e/kg)": 0.134, "Satuan": "kg"}
        ])

ice_version, df_ice_materials = load_ice_excel_database()

if "calc_num_items" not in st.session_state:
    st.session_state["calc_num_items"] = 3

if "dist_km" not in st.session_state:
    st.session_state["dist_km"] = 25.0

if "fuel_liter" not in st.session_state:
    st.session_state["fuel_liter"] = 100.0

# ==========================================
# 3. HELPER GENERATOR LAPORAN PDF
# ==========================================
def generate_pdf_report(df_results, total_emission_ton, total_cost, cost_per_ton, transport_emission_kg, equipment_emission_kg, ice_ver):
    if not HAS_REPORTLAB:
        return b""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=15,
        textColor=colors.HexColor('#0F2027'),
        spaceAfter=6
    )
    story.append(Paragraph("<b>EcoBuild Pro v2.0 - Laporan Analisis Emisi Karbon Proyek</b>", title_style))
    story.append(Paragraph(f"<b>Basis Data Material:</b> ICE Database {ice_ver} | <b>Dosen Pengampu:</b> Dr. Ir. Dedy Firmansyah, S.Pd., M.T.", styles['Normal']))
    story.append(Spacer(1, 14))
    
    summary_data = [
        ["Parameter Analisis", "Nilai Output Proyek"],
        ["Total Emisi Karbon Proyek", f"{total_emission_ton:,.2f} Ton CO2e"],
        ["Total Estimasi Biaya Material", f"Rp {total_cost:,.0f}"],
        ["Rasio Biaya / Emisi Karbon", f"Rp {cost_per_ton:,.0f} / Ton CO2e"],
        ["Emisi Pengangkutan Logistik (A4)", f"{transport_emission_kg/1000:,.2f} Ton CO2e"],
        ["Emisi BBM Alat Berat (A5)", f"{equipment_emission_kg/1000:,.2f} Ton CO2e"]
    ]
    
    t_summary = Table(summary_data, colWidths=[240, 260])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B5E20')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E0E0E0'))
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 16))
    
    if not df_results.empty:
        story.append(Paragraph("<b>Rincian Material Proyek & Faktor Emisi ICE:</b>", styles['Heading2']))
        story.append(Spacer(1, 8))
        
        table_data = [["Material", "Jumlah", "Satuan", "Emisi (kg CO2e)", "Biaya (Rp)"]]
        for _, row in df_results.iterrows():
            table_data.append([
                str(row['Material'])[:45],
                f"{row['Jumlah']:,.2f}",
                str(row['Satuan']),
                f"{row['Emisi (kg CO2e)']:,.2f}",
                f"Rp {row['Biaya (Rp)']:,.0f}"
            ])
        
        t_detail = Table(table_data, colWidths=[160, 50, 40, 110, 140])
        t_detail.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
        ]))
        story.append(t_detail)
        
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ==========================================
# 4. SIDEBAR NAVIGASI & EXECUTIVE BRANDING
# ==========================================
def navigate_to(page_name):
    st.session_state["nav_menu"] = page_name

if "nav_menu" not in st.session_state:
    st.session_state["nav_menu"] = "🏠 Beranda"

logo_path = get_existing_image(["logo_kingsman.png", "logo_kingsman.jpg", "logo.png", "logo.jpg"])
logo_base64 = get_image_base64(logo_path)

with st.sidebar:
    # 1. Executive Brand Box
    if logo_base64:
        logo_html = f'<img src="{logo_base64}" class="sidebar-logo-img" alt="Kingsman Logo" />'
    else:
        logo_html = '<div style="font-size: 2.2rem; margin-bottom: 8px;">🏗️</div>'
        
    st.markdown(f"""
    <div class="sidebar-brand-card">
        {logo_html}
        <div class="sidebar-brand-title">EcoBuild Pro</div>
        <div style="font-size: 0.78rem; opacity: 0.85; color: #cbd5e1; margin-bottom: 4px;">Civil Carbon & Cost Intelligence</div>
        <span class="sidebar-brand-pill">● v2.0 Executive Edition</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Navigasi Menu
    st.markdown('<div class="sidebar-nav-label">🧭 Navigasi Utama</div>', unsafe_allow_html=True)
    menu = st.radio(
        "Pilih Menu Utama:",
        ["🏠 Beranda", "🧮 Kalkulator & Analisis Proyek", "📊 Database Material ICE (Otomatis)", "⚖️ Simulasi Komparasi Desain", "📚 Siklus Hidup Emisi & Solusi"],
        key="nav_menu",
        label_visibility="collapsed"
    )

    # 3. Status Engine & Database
    st.markdown(f"""
    <div class="sidebar-status-box">
        <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #38bdf8; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            <span>⚡</span> Status Engine & Basis Data
        </div>
        <div class="sidebar-status-row">
            <span style="opacity: 0.8;">Database ICE:</span>
            <span style="font-weight: 700; color: #34d399;">v5.0 Terhubung</span>
        </div>
        <div class="sidebar-status-row">
            <span style="opacity: 0.8;">Katalog Material:</span>
            <span style="font-weight: 700; color: #f1f5f9;">{len(df_ice_materials):,} Jenis</span>
        </div>
        <div class="sidebar-status-row">
            <span style="opacity: 0.8;">Standar Emisi:</span>
            <span style="font-weight: 700; color: #f1f5f9;">BS EN 15978 (A1-D)</span>
        </div>
        <div class="sidebar-status-row">
            <span style="opacity: 0.8;">Modul Logistik:</span>
            <span style="font-weight: 700; color: #38bdf8;">Terkalibrasi</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. Box Dosen Pengampu & Pengesahan Akademik
    accreditation_card_html = (
        '<div class="sidebar-accreditation">'
        '<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">'
        '<span style="font-size: 1.15rem;">&#127891;</span>'
        '<span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: #34d399;">Dosen Pengampu</span>'
        '</div>'
        '<div style="font-size: 0.94rem; font-weight: 800; color: #ffffff; line-height: 1.3;">'
        'Dr. Ir. Dedy Firmansyah, S.Pd., M.T.'
        '</div>'
        '<div style="font-size: 0.74rem; opacity: 0.85; margin-top: 5px; color: #cbd5e1; line-height: 1.4;">'
        'Bidang Rekayasa Teknik Sipil, Manajemen Konstruksi & Bangunan Ramah Lingkungan'
        '</div>'
        '</div>'
    )
    st.markdown(accreditation_card_html, unsafe_allow_html=True)

    # 5. Footer Sidebar
    st.markdown("""
    <div style="text-align: center; margin-top: 24px; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.06); font-size: 0.73rem; color: #94a3b8;">
        Dikembangkan oleh <b>CV Kingsman IDN</b><br>
        EcoBuild Civil Intelligence Platform © 2026
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# MENU 1: BERANDA
# ==========================================
if menu == "🏠 Beranda":
    st.markdown("""
        <div class="hero-container">
            <div class="hero-badge">🌿 Green Building & Civil Engineering Intelligence</div>
            <div class="hero-title">EcoBuild Pro Simulator</div>
            <div class="hero-subtitle">Platform analisis kuantitatif jejak emisi karbon (Embodied & Construction Carbon) serta optimasi biaya untuk proyek konstruksi teknik sipil yang berkelanjutan.</div>
            <div class="hero-chips-row">
                <span class="hero-chip">🏛️ ICE Database v5.0 Synced</span>
                <span class="hero-chip">📊 Optimasi Biaya RAB & Emisi</span>
                <span class="hero-chip">🚚 Emisi Tahap Pelaksanaan (A4-A5)</span>
                <span class="hero-chip">📈 Standar LCA EN 15978</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("🌐 Latar Belakang & Urgensi Sektor Konstruksi")
    col_bg1, col_bg2 = st.columns([1.1, 0.9])
    
    with col_bg1:
        st.write("""
        Industri konstruksi dan teknik sipil bertanggung jawab atas **hampir 40% emisi gas rumah kaca global**. 
        Emisi tidak hanya berasal dari pemakaian listrik saat gedung beroperasi (*Operational Carbon*), tetapi juga sejak 
        proses ekstraksi bahan mentah, pengangkutan logistik, hingga konsumsi BBM alat-alat berat di lapangan (*Embodied & Construction Carbon*).
        
        **EcoBuild Pro** hadir sebagai *software* berbasis data untuk menghitung dampak karbon secara komprehensif, 
        menguji efisiensi biaya, serta membandingkan alternatif material ramah lingkungan secara interaktif.
        """)

        img_gas = get_existing_image(["gas_emisi.jpg", "gas_emisi.jpeg", "gas-rumah-kaca.jpg"])
        if img_gas:
            st.image(img_gas, caption="Emisi Gas Rumah Kaca Sektor Industri & Pabrikasi Material", use_container_width=True)

    with col_bg2:
        st.warning("""
        🔥 **Pengingat Urgensi Iklim & Tanggung Jawab Profesi:**
        Bencana Kebakaran Hutan dan Lahan (Karhutla) di Indonesia menjadi bukti nyata masifnya pelepasan emisi karbon ke atmosfer yang memperparah pemanasan global. 
        
        Apabila para pelaku di industri **konstruksi dan teknik sipil acuh** terhadap jejak karbon dari material serta pelaksanaan proyek yang mereka bangun, maka akumulasi emisi akan semakin tidak terkendali. Sektor teknik sipil harus mengambil peran aktif dalam memitigasi emisi sejak tahap perencanaan, bukan justru memperberat krisis lingkungan yang ada.
        """)

        img_karhutla = get_existing_image(["karhutla.jpg", "karhutla.jfif", "karhutla.jpg.jfif"])
        if img_karhutla:
            st.image(img_karhutla, caption="Refleksi Urgensi Bencana Karhutla & Dampak Emisi Karbon", use_container_width=True)

    st.markdown("---")
    st.info(f"📚 **Basis Data Emisi Karbon Terintegrasi:** Data emisi material pada aplikasi ini terhubung langsung secara otomatis dengan **ICE Database ({ice_version})** dari Circular Ecology & University of Bath.")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info("### 📦 Material Carbon\nHitung jejak karbon dari berbagai jenis material struktur.")
        st.button("Buka Kalkulator ➔", key="btn_nav_mat", use_container_width=True, on_click=navigate_to, args=("🧮 Kalkulator & Analisis Proyek",))

    with col2:
        st.warning("### 🚛 Logistik & Alat\nIntegrasi emisi pengangkutan truk & BBM solar alat berat.")
        st.button("Hitung Logistik ➔", key="btn_nav_log", use_container_width=True, on_click=navigate_to, args=("🧮 Kalkulator & Analisis Proyek",))

    with col3:
        st.success("### ⚖️ Komparasi Skenario\nBandingkan Desain Konvensional vs Green Design secara instan.")
        st.button("Mulai Komparasi ➔", key="btn_nav_komp", use_container_width=True, on_click=navigate_to, args=("⚖️ Simulasi Komparasi Desain",))

    with col4:
        st.error("### 📚 Siklus Hidup & LCA\nPelajari modul tahap emisi A1-D dan strategi teknisnya.")
        st.button("Pelajari LCA ➔", key="btn_nav_lca", use_container_width=True, on_click=navigate_to, args=("📚 Siklus Hidup Emisi & Solusi",))

# ==========================================
# MENU 2: KALKULATOR & ANALISIS PROYEK
# ==========================================
elif menu == "🧮 Kalkulator & Analisis Proyek":
    st.title("🧮 Kalkulator Emisi & Biaya Proyek")
    st.write("Hitung jejak emisi karbon dan estimasi biaya proyek dengan memilih material dari **ICE Database** atau mengisi **Material Kustom** secara fleksibel.")

    with st.expander("💾 Backup / Restorasi Proyek (JSON) & Impor File RAB Excel", expanded=False):
        c_exp1, c_exp2 = st.columns(2)
        
        with c_exp1:
            st.subheader("📥 Impor File RAB (.xlsx / .csv)")
            uploaded_rab = st.file_uploader("Unggah file RAB Excel/CSV:", type=["xlsx", "csv"], key="rab_uploader")
            
            if uploaded_rab is not None:
                file_id = f"{uploaded_rab.name}_{uploaded_rab.size}"
                if st.session_state.get("last_uploaded_rab_id") != file_id:
                    try:
                        df_rab = pd.read_csv(uploaded_rab) if uploaded_rab.name.endswith(".csv") else pd.read_excel(uploaded_rab)
                        df_rab.columns = [str(c).strip() for c in df_rab.columns]
                        
                        col_map = {}
                        for c in df_rab.columns:
                            clow = c.lower()
                            if "material" in clow or "nama" in clow or "bahan" in clow:
                                col_map["Material"] = c
                            elif "harga" in clow or "price" in clow or "rp" in clow:
                                col_map["Harga Satuan"] = c
                            elif "faktor" in clow or "emisi" in clow or "co2" in clow:
                                col_map["Faktor Emisi"] = c
                            elif "satuan" in clow or "unit" in clow:
                                col_map["Satuan"] = c
                            elif "jumlah" in clow or "volume" in clow or "qty" in clow:
                                col_map["Jumlah"] = c

                        if "Material" in col_map and "Jumlah" in col_map:
                            num_r = len(df_rab)
                            st.session_state["calc_num_items"] = num_r
                            st.session_state["input_num_items"] = num_r
                            
                            ice_lookup = dict(zip(df_ice_materials["Nama Material"], df_ice_materials["Faktor Emisi (kg CO2e/kg)"]))
                            
                            for idx, row in df_rab.iterrows():
                                mat_v = str(row[col_map["Material"]]).strip()
                                qty_v = float(pd.to_numeric(row[col_map["Jumlah"]], errors='coerce') or 0)
                                sat_v = str(row[col_map["Satuan"]]).strip() if "Satuan" in col_map and pd.notna(row[col_map["Satuan"]]) else "kg"
                                
                                if "Faktor Emisi" in col_map and pd.notna(row[col_map["Faktor Emisi"]]):
                                    fe_v = float(pd.to_numeric(row[col_map["Faktor Emisi"]], errors='coerce') or 1.0)
                                elif mat_v in ice_lookup:
                                    fe_v = float(ice_lookup[mat_v])
                                else:
                                    fe_v = 1.0

                                if "Harga Satuan" in col_map and pd.notna(row[col_map["Harga Satuan"]]):
                                    hrg_v = float(pd.to_numeric(row[col_map["Harga Satuan"]], errors='coerce') or 10000.0)
                                else:
                                    hrg_v = 15000.0 if mat_v in ice_lookup else 10000.0

                                st.session_state[f"calc_sel_{idx}"] = "➕ Material Kustom (Isi Sendiri)"
                                st.session_state[f"c_name_{idx}"] = mat_v
                                st.session_state[f"c_unit_{idx}"] = sat_v
                                st.session_state[f"c_fact_{idx}"] = fe_v
                                st.session_state[f"c_price_{idx}"] = hrg_v
                                st.session_state[f"c_qty_{idx}"] = qty_v
                            
                            st.session_state["last_uploaded_rab_id"] = file_id
                            st.success(f"✅ Berhasil mengimpor {num_r} item material secara presisi!")
                            st.rerun()
                        else:
                            st.error("File RAB wajib memiliki minimal kolom 'Material' dan 'Jumlah'.")
                    except Exception as e:
                        st.error(f"Gagal membaca file RAB: {e}")

        with c_exp2:
            st.subheader("💾 Backup Draft Proyek (JSON)")
            save_data = {
                "calc_num_items": st.session_state.get("calc_num_items", 3),
                "dist_km": st.session_state["dist_km"],
                "fuel_liter": st.session_state["fuel_liter"]
            }
            st.download_button(
                label="📥 Export Draft Proyek (JSON)",
                data=json.dumps(save_data, indent=2),
                file_name="draft_proyek_ecobuild.json",
                mime="application/json",
                use_container_width=True
            )

    st.markdown("---")
    
    # KONTROL JUMLAH & PRESET CEPAT
    col_cnt1, col_cnt2, col_cnt3 = st.columns([1.5, 1, 1.2])
    with col_cnt1:
        num_items = st.number_input(
            "🔢 Jumlah Jenis Material:",
            min_value=1,
            max_value=30,
            value=int(st.session_state.get("calc_num_items", 3)),
            step=1,
            key="input_num_items"
        )
        st.session_state["calc_num_items"] = num_items
        
    with col_cnt2:
        st.write("")
        st.write("")
        if st.button("➕ Tambah Baris", use_container_width=True, help="Tambahkan 1 baris input material"):
            st.session_state["calc_num_items"] = min(30, int(st.session_state["calc_num_items"]) + 1)
            st.rerun()
            
    with col_cnt3:
        st.write("")
        st.write("")
        if st.button("⚡ Muat Contoh Proyek", use_container_width=True, help="Isi otomatis dengan simulasi proyek gedung standar"):
            st.session_state["calc_num_items"] = 3
            st.session_state["dist_km"] = 30.0
            st.session_state["fuel_liter"] = 150.0
            
            # Cari material umum jika ada
            c_mat = [m for m in df_ice_materials["Nama Material"] if "concrete" in m.lower() or "beton" in m.lower()]
            s_mat = [m for m in df_ice_materials["Nama Material"] if "steel" in m.lower() or "baja" in m.lower()]
            t_mat = [m for m in df_ice_materials["Nama Material"] if "brick" in m.lower() or "timber" in m.lower() or "kayu" in m.lower()]
            
            mat1 = c_mat[0] if c_mat else df_ice_materials["Nama Material"].iloc[0]
            mat2 = s_mat[0] if s_mat else (df_ice_materials["Nama Material"].iloc[1] if len(df_ice_materials) > 1 else mat1)
            mat3 = t_mat[0] if t_mat else (df_ice_materials["Nama Material"].iloc[2] if len(df_ice_materials) > 2 else mat1)
            
            st.session_state["calc_sel_0"] = mat1
            st.session_state["p_val_0"] = 1200.0
            st.session_state["q_val_0"] = 25000.0
            
            st.session_state["calc_sel_1"] = mat2
            st.session_state["p_val_1"] = 14500.0
            st.session_state["q_val_1"] = 3500.0
            
            st.session_state["calc_sel_2"] = mat3
            st.session_state["p_val_2"] = 1800.0
            st.session_state["q_val_2"] = 8000.0
            st.rerun()

    ice_mat_names = df_ice_materials["Nama Material"].tolist()
    all_mat_options = ["➕ Material Kustom (Isi Sendiri)"] + ice_mat_names

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📦 Formulir Input Material Struktur Proyek")
    st.caption("Pilih material dari database resmi ICE atau input spesifikasi kustom Anda sendiri.")
    
    results = []
    total_mat_emission_kg = 0
    total_mat_cost = 0

    # LOOP FORM INPUT MATERIAL DENGAN LAYOUT RAPI & EXECUTIVE
    for i in range(num_items):
        def_idx = (i + 1) if (i + 1) < len(all_mat_options) else 0
        curr_selection = st.session_state.get(f"calc_sel_{i}", all_mat_options[def_idx])
        is_custom = (curr_selection == "➕ Material Kustom (Isi Sendiri)")
        
        # Header Kartu Item Material
        st.markdown(f"""
        <div class="mat-card-header-bar">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span class="mat-card-pill">ITEM #{i+1}</span>
                <span style="font-weight: 700; color: #1e293b; font-size: 0.95rem;">
                    {'Material Kustom' if is_custom else curr_selection[:55] + ('...' if len(curr_selection) > 55 else '')}
                </span>
            </div>
            <span style="font-size: 0.74rem; font-weight: 700; padding: 3px 10px; border-radius: 6px; 
                         background: {'#fef3c7' if is_custom else '#e0f2fe'}; 
                         color: {'#92400e' if is_custom else '#0369a1'}; 
                         border: 1px solid {'#fde68a' if is_custom else '#bae6fd'};">
                {'🛠️ KUSTOM MANUAL' if is_custom else '📦 DATABASE ICE'}
            </span>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            # Step 1: Pilihan Material (Full Width)
            sel_mat = st.selectbox(
                f"Pilih Sumber & Nama Material #{i+1}:",
                options=all_mat_options,
                index=def_idx,
                key=f"calc_sel_{i}",
                help="Gunakan pencarian untuk memilih material dari Circular Ecology ICE Database atau pilih Material Kustom."
            )

            # Step 2: Form Parameter Tertata Rapi
            if sel_mat != "➕ Material Kustom (Isi Sendiri)":
                mat_match = df_ice_materials[df_ice_materials["Nama Material"] == sel_mat]
                if not mat_match.empty:
                    mat_info = mat_match.iloc[0]
                else:
                    mat_info = {"Satuan": "kg", "Faktor Emisi (kg CO2e/kg)": 0.134, "Kategori": "General"}
                    
                mat_name = sel_mat
                unit_str = mat_info["Satuan"]
                factor_val = float(mat_info["Faktor Emisi (kg CO2e/kg)"])
                cat_name = mat_info.get("Kategori", "Material Umum")
                
                c_m1, c_m2, c_m3 = st.columns([1.2, 1, 1])
                with c_m1:
                    st.markdown(f"""
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 14px; min-height: 72px; display: flex; flex-direction: column; justify-content: center;">
                        <div style="font-size: 0.70rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Faktor Emisi ICE ({unit_str})</div>
                        <div style="font-size: 1.05rem; font-weight: 800; color: #0f172a; margin-top: 2px;">
                            {factor_val:.6f} <span style="font-size: 0.72rem; color: #10b981; font-weight: 600;">kg CO2e/{unit_str}</span>
                        </div>
                        <div style="font-size: 0.70rem; color: #94a3b8; margin-top: 2px;">Kat: {cat_name[:30]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c_m2:
                    price_val = st.number_input(
                        f"Harga Satuan (Rp/{unit_str}) #{i+1}:",
                        min_value=0.0,
                        value=float(st.session_state.get(f"p_val_{i}", 15000.0)),
                        step=1000.0,
                        key=f"p_val_{i}"
                    )
                with c_m3:
                    qty_val = st.number_input(
                        f"Volume Kebutuhan ({unit_str}) #{i+1}:",
                        min_value=0.0,
                        value=float(st.session_state.get(f"q_val_{i}", 0.0)),
                        step=50.0,
                        key=f"q_val_{i}"
                    )
            else:
                c_c1, c_c2 = st.columns([2.5, 1])
                with c_c1:
                    mat_name = st.text_input(
                        f"Nama Material Kustom #{i+1}:",
                        value=st.session_state.get(f"c_name_{i}", f"Material Kustom {i+1}"),
                        key=f"c_name_{i}"
                    )
                with c_c2:
                    unit_str = st.text_input(
                        f"Satuan (kg/m3/ton) #{i+1}:",
                        value=st.session_state.get(f"c_unit_{i}", "kg"),
                        key=f"c_unit_{i}"
                    )
                    
                c_c3, c_c4, c_c5 = st.columns([1, 1, 1])
                with c_c3:
                    factor_val = st.number_input(
                        f"Faktor Emisi (kg CO2e/{unit_str}):",
                        min_value=0.0,
                        value=float(st.session_state.get(f"c_fact_{i}", 1.0)),
                        step=0.05,
                        key=f"c_fact_{i}"
                    )
                with c_c4:
                    price_val = st.number_input(
                        f"Harga Satuan (Rp/{unit_str}):",
                        min_value=0.0,
                        value=float(st.session_state.get(f"c_price_{i}", 10000.0)),
                        step=1000.0,
                        key=f"c_price_{i}"
                    )
                with c_c5:
                    qty_val = st.number_input(
                        f"Volume Kebutuhan ({unit_str}):",
                        min_value=0.0,
                        value=float(st.session_state.get(f"c_qty_{i}", 0.0)),
                        step=10.0,
                        key=f"c_qty_{i}"
                    )

            # Kalkulasi Real-time Item
            e_kg = qty_val * factor_val
            c_rp = qty_val * price_val
            if qty_val > 0:
                results.append({
                    "Material": mat_name,
                    "Jumlah": qty_val,
                    "Satuan": unit_str,
                    "Emisi (kg CO2e)": e_kg,
                    "Biaya (Rp)": c_rp
                })
                total_mat_emission_kg += e_kg
                total_mat_cost += c_rp

            # Real-time Subtotal Pill
            st.markdown(f"""
            <div class="mat-subtotal-pill">
                <div style="color: #475569;">
                    🌿 <b>Emisi Item:</b> <span style="color: {'#059669' if e_kg > 0 else '#94a3b8'}; font-weight: 700;">{e_kg:,.2f} kg CO2e</span> ({e_kg/1000:,.3f} Ton)
                </div>
                <div style="color: #475569;">
                    💰 <b>Subtotal Biaya:</b> <span style="color: {'#0284c7' if c_rp > 0 else '#94a3b8'}; font-weight: 700;">Rp {c_rp:,.0f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin-bottom: 22px;'></div>", unsafe_allow_html=True)

    # SEKSI EMISI LOGISTIK & ALAT BERAT
    st.markdown("---")
    st.subheader("🚚 Pengangkutan Logistik & BBM Alat Berat (Modul A4 - A5)")
    st.caption("Hitung emisi transportasi logistik dari pabrik/kuari ke proyek serta konsumsi solar alat berat di lapangan.")
    
    c_trans1, c_trans2 = st.columns(2)
    with c_trans1:
        st.session_state["dist_km"] = st.number_input(
            "Jarak Pengangkutan Rata-rata (km):", 
            min_value=0.0, 
            value=float(st.session_state["dist_km"]), 
            step=5.0, 
            key="calc_dist_km",
            help="Faktor emisi armada truk logistik ~ 0.25 kg CO2e / ton-km (estimasi muatan 10 Ton)"
        )
    with c_trans2:
        st.session_state["fuel_liter"] = st.number_input(
            "Konsumsi Solar Alat Berat di Tapak Proyek (Liter):", 
            min_value=0.0, 
            value=float(st.session_state["fuel_liter"]), 
            step=50.0, 
            key="calc_fuel_liter",
            help="Faktor emisi pembakaran solar industri ~ 2.68 kg CO2e / Liter diesel"
        )

    transport_emission_kg = st.session_state["dist_km"] * 0.25 * 10
    equipment_emission_kg = st.session_state["fuel_liter"] * 2.68
    
    total_project_emission_kg = total_mat_emission_kg + transport_emission_kg + equipment_emission_kg
    total_project_emission_ton = total_project_emission_kg / 1000
    cost_per_ton = (total_mat_cost / total_project_emission_ton) if total_project_emission_ton > 0 else 0

    # ==========================================
    # KARTU MATRIKS EMISI (BORDER SHADOW & STATUS COLORS)
    # ==========================================
    st.markdown("---")
    st.subheader("📊 Executive Carbon & Cost Intelligence Scorecard")
    
    # Logika Penentuan Status Emisi
    if total_project_emission_ton == 0:
        status_class = "status-optimal"
        pill_class = "pill-optimal"
        status_badge = "⚪ DATA KOSONG"
        status_desc = "Masukkan volume material di atas untuk menghasilkan kalkulasi emisi proyek."
    elif total_project_emission_ton < 10.0:
        status_class = "status-optimal"
        pill_class = "pill-optimal"
        status_badge = "🟢 STATUS OPTIMAL"
        status_desc = "Jejak karbon terkontrol & efisien (Memenuhi Benchmark Green Building)"
    elif total_project_emission_ton <= 50.0:
        status_class = "status-moderate"
        pill_class = "pill-moderate"
        status_badge = "🟡 STATUS MODERAT"
        status_desc = "Intensitas karbon rata-rata industri; disarankan optimasi substitusi material"
    else:
        status_class = "status-critical"
        pill_class = "pill-critical"
        status_badge = "🔴 STATUS KRITIS"
        status_desc = "Intensitas karbon tinggi; segera pertimbangkan material substitusi rendah emisi"

    pct_mat = (total_mat_emission_kg / total_project_emission_kg * 100) if total_project_emission_kg > 0 else 0
    pct_trans = (transport_emission_kg / total_project_emission_kg * 100) if total_project_emission_kg > 0 else 0
    pct_eq = (equipment_emission_kg / total_project_emission_kg * 100) if total_project_emission_kg > 0 else 0

    st.markdown(f"""
    <div class="exec-metrics-grid">
        <!-- KARTU 1: TOTAL EMISI KARBON -->
        <div class="exec-metric-card {status_class}">
            <div>
                <div class="exec-card-head">
                    <div class="exec-card-title-group">
                        <span class="exec-card-icon">🌍</span>
                        <span class="exec-card-title">Total Emisi Karbon Proyek</span>
                    </div>
                    <span class="exec-status-pill {pill_class}">{status_badge}</span>
                </div>
                <div class="exec-card-value">
                    {total_project_emission_ton:,.2f}
                    <span class="exec-card-unit">Ton CO2e</span>
                </div>
            </div>
            <div class="exec-card-subtext">
                <b>{status_desc}</b><br>
                <span style="font-size: 0.77rem; color: #64748b; margin-top: 5px; display: inline-block;">
                    Porsi: Material <b>{pct_mat:.1f}%</b> • Logistik <b>{pct_trans:.1f}%</b> • Alat <b>{pct_eq:.1f}%</b>
                </span>
            </div>
        </div>

        <!-- KARTU 2: ESTIMASI BIAYA MATERIAL -->
        <div class="exec-metric-card theme-finance">
            <div>
                <div class="exec-card-head">
                    <div class="exec-card-title-group">
                        <span class="exec-card-icon">💼</span>
                        <span class="exec-card-title">Total Estimasi Biaya</span>
                    </div>
                    <span class="exec-status-pill pill-finance">💰 ANGGARAN</span>
                </div>
                <div class="exec-card-value">
                    Rp {total_mat_cost:,.0f}
                </div>
            </div>
            <div class="exec-card-subtext">
                Estimasi belanja pengadaan {len(results)} jenis material struktur proyek.<br>
                <span style="font-size: 0.77rem; color: #64748b; margin-top: 5px; display: inline-block;">
                    Berdasarkan standar harga satuan yang Anda masukkan
                </span>
            </div>
        </div>

        <!-- KARTU 3: EFISIENSI BIAYA / EMISI -->
        <div class="exec-metric-card theme-efficiency">
            <div>
                <div class="exec-card-head">
                    <div class="exec-card-title-group">
                        <span class="exec-card-icon">⚖️</span>
                        <span class="exec-card-title">Rasio Biaya / Emisi</span>
                    </div>
                    <span class="exec-status-pill pill-efficiency">⚡ INDEKS EFISIENSI</span>
                </div>
                <div class="exec-card-value">
                    Rp {cost_per_ton:,.0f}
                    <span class="exec-card-unit">/ Ton CO2e</span>
                </div>
            </div>
            <div class="exec-card-subtext">
                Indeks belanja modal per Ton emisi karbon yang dihasilkan.<br>
                <span style="font-size: 0.77rem; color: #64748b; margin-top: 5px; display: inline-block;">
                    Membantu mengevaluasi *cost-effectiveness* dekarbonisasi struktur
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # TABEL & GRAFIK HASIL PERHITUNGAN
    if results:
        df = pd.DataFrame(results)
        tab_a, tab_b = st.tabs(["📊 Visualisasi Grafik & Distribusi Emisi", "📄 Tabel Data Rinci & Ekspor Laporan"])

        with tab_a:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                fig_pie = px.pie(
                    df, 
                    names="Material", 
                    values="Emisi (kg CO2e)", 
                    title="Kontribusi Emisi per Jenis Material Struktur", 
                    hole=0.45,
                    color_discrete_sequence=px.colors.sequential.Greens_r
                )
                fig_pie.update_layout(
                    font_family="Plus Jakarta Sans",
                    margin=dict(t=50, b=20, l=20, r=20),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_g2:
                source_df = pd.DataFrame([
                    {"Sumber": "Material Konstruksi", "Emisi (Ton CO2e)": total_mat_emission_kg / 1000},
                    {"Sumber": "Pengangkutan Logistik (A4)", "Emisi (Ton CO2e)": transport_emission_kg / 1000},
                    {"Sumber": "BBM Alat Berat (A5)", "Emisi (Ton CO2e)": equipment_emission_kg / 1000},
                ])
                fig_bar = px.bar(
                    source_df, 
                    x="Sumber", 
                    y="Emisi (Ton CO2e)", 
                    color="Sumber", 
                    title="Komposisi Emisi Karbon Berdasarkan Tahapan Pelaksanaan",
                    color_discrete_map={
                        "Material Konstruksi": "#059669",
                        "Pengangkutan Logistik (A4)": "#0284c7",
                        "BBM Alat Berat (A5)": "#d97706"
                    }
                )
                fig_bar.update_layout(
                    font_family="Plus Jakarta Sans",
                    margin=dict(t=50, b=20, l=20, r=20),
                    showlegend=False
                )
                st.plotly_chart(fig_bar, use_container_width=True)

        with tab_b:
            st.dataframe(
                df, 
                use_container_width=True,
                column_config={
                    "Jumlah": st.column_config.NumberColumn(format="%.2f"),
                    "Emisi (kg CO2e)": st.column_config.NumberColumn(format="%.2f kg CO2e"),
                    "Biaya (Rp)": st.column_config.NumberColumn(format="Rp %d")
                }
            )
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Data Perhitungan (CSV)",
                    data=csv_data,
                    file_name="Laporan_Emisi_EcoBuild.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_d2:
                if HAS_REPORTLAB:
                    pdf_bytes = generate_pdf_report(
                        df_results=df,
                        total_emission_ton=total_project_emission_ton,
                        total_cost=total_mat_cost,
                        cost_per_ton=cost_per_ton,
                        transport_emission_kg=transport_emission_kg,
                        equipment_emission_kg=equipment_emission_kg,
                        ice_ver=ice_version
                    )
                    st.download_button(
                        label="📄 Download Laporan Resmi (PDF)",
                        data=pdf_bytes,
                        file_name="Laporan_Resmi_EcoBuild_Pro.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.button(
                        "📄 Download Laporan Resmi (PDF)", 
                        disabled=True, 
                        use_container_width=True, 
                        help="Modul ReportLab belum terpasang di sistem python."
                    )
    else:
        st.info("💡 Masukkan jumlah/besaran material pada form di atas untuk menampilkan analisis grafik emisi dan laporan PDF.")

# ==========================================
# MENU 3: DATABASE MATERIAL ICE (OTOMATIS)
# ==========================================
elif menu == "📊 Database Material ICE (Otomatis)":
    st.title("📊 Master Database Material ICE (Auto-Sync)")
    
    st.info(f"""
    **ℹ️ Status Integrasi Database ICE:**  
    * **Versi Database Terdeteksi:** `{ice_version}`  
    * **Total Material Terdaftar:** `{len(df_ice_materials)} Jenis Material`  
    * **Mekanisme Update:** Data dibaca **langsung secara otomatis dari file Excel ICE**. Jika terdapat pembaruan data, developer/admin cukup mengganti file `.xlsx` di repository.
    """)

    col_search1, col_search2 = st.columns([1, 2])
    with col_search1:
        cat_select = st.selectbox("🔍 Filter Berdasarkan Kategori:", ["Semua Kategori"] + sorted(list(df_ice_materials["Kategori"].unique())))
    with col_search2:
        search_query = st.text_input("🔎 Cari Nama Material Spesifik:", placeholder="Ketik nama material, misal: Concrete, Steel, Timber, Aluminium...")

    display_df = df_ice_materials.copy()
    if cat_select != "Semua Kategori":
        display_df = display_df[display_df["Kategori"] == cat_select]
    if search_query:
        display_df = display_df[display_df["Nama Material"].str.contains(search_query, case=False, na=False)]

    st.markdown(f"**Menampilkan `{len(display_df)}` dari `{len(df_ice_materials)}` material.**")
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Faktor Emisi (kg CO2e/kg)": st.column_config.NumberColumn(format="%.6f kg CO2e/kg")
        }
    )

# ==========================================
# MENU 4: SIMULASI KOMPARASI DESAIN
# ==========================================
elif menu == "⚖️ Simulasi Komparasi Desain":
    st.title("⚖️ Simulasi Komparasi: Skenario A vs Skenario B")
    st.write("Bandingkan dua opsi desain struktur secara langsung untuk mengevaluasi potensi dekarbonisasi material.")

    mat_options = df_ice_materials["Nama Material"].tolist()

    col_s1, col_s2 = st.columns(2)

    emisi_a = 0
    with col_s1:
        st.markdown("""
        <div style="background: #fff1f2; border: 1px solid #fecdd3; border-top: 4px solid #ef4444; border-radius: 12px; padding: 14px 18px; margin-bottom: 12px;">
            <div style="font-weight: 800; color: #9f1239; font-size: 1rem;">🔴 Skenario A (Desain Konvensional / Baseline)</div>
            <div style="font-size: 0.8rem; color: #881337;">Material standar tanpa substitusi rendah karbon</div>
        </div>
        """, unsafe_allow_html=True)
        mat_a = st.selectbox("Pilih Material Skenario A:", mat_options, index=0, key="sa_m")
        vol_a = st.number_input("Jumlah Material A (kg):", min_value=0.0, value=1000.0, key="v_a")
        
        f_a = float(df_ice_materials[df_ice_materials["Nama Material"] == mat_a].iloc[0]["Faktor Emisi (kg CO2e/kg)"])
        emisi_a = vol_a * f_a

    emisi_b = 0
    with col_s2:
        st.markdown("""
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-top: 4px solid #10b981; border-radius: 12px; padding: 14px 18px; margin-bottom: 12px;">
            <div style="font-weight: 800; color: #065f46; font-size: 1rem;">🟢 Skenario B (Desain Alternatif / Ramah Lingkungan)</div>
            <div style="font-size: 0.8rem; color: #064e3b;">Material inovatif dengan faktor emisi lebih rendah</div>
        </div>
        """, unsafe_allow_html=True)
        mat_b = st.selectbox("Pilih Material Skenario B:", mat_options, index=min(1, len(mat_options)-1), key="sb_m")
        vol_b = st.number_input("Jumlah Material B (kg):", min_value=0.0, value=1000.0, key="v_b")
        
        f_b = float(df_ice_materials[df_ice_materials["Nama Material"] == mat_b].iloc[0]["Faktor Emisi (kg CO2e/kg)"])
        emisi_b = vol_b * f_b

    st.markdown("---")
    st.subheader("📈 Hasil Perbandingan Komparasi Emisi")

    emisi_a_ton = emisi_a / 1000
    emisi_b_ton = emisi_b / 1000
    hemat_emisi_pct = ((emisi_a - emisi_b) / emisi_a * 100) if emisi_a > 0 else 0
    delta_ton = abs(emisi_a_ton - emisi_b_ton)

    # Executive Komparasi Metric Cards
    st.markdown(f"""
    <div class="exec-metrics-grid" style="grid-template-columns: 1fr 1fr;">
        <div class="exec-metric-card status-critical">
            <div>
                <div class="exec-card-head">
                    <div class="exec-card-title-group">
                        <span class="exec-card-icon">🔴</span>
                        <span class="exec-card-title">Emisi Skenario A</span>
                    </div>
                    <span class="exec-status-pill pill-critical">BASELINE</span>
                </div>
                <div class="exec-card-value">{emisi_a_ton:,.3f} <span class="exec-card-unit">Ton CO2e</span></div>
            </div>
            <div class="exec-card-subtext">
                Material: <b>{mat_a[:45]}</b><br>
                Faktor Emisi: <b>{f_a:.6f} kg CO2e/kg</b>
            </div>
        </div>
        
        <div class="exec-metric-card status-optimal">
            <div>
                <div class="exec-card-head">
                    <div class="exec-card-title-group">
                        <span class="exec-card-icon">🟢</span>
                        <span class="exec-card-title">Emisi Skenario B</span>
                    </div>
                    <span class="exec-status-pill pill-optimal">{'HEMAT ' + f'{hemat_emisi_pct:.1f}%' if hemat_emisi_pct > 0 else 'HEMAT 0%'}</span>
                </div>
                <div class="exec-card-value">{emisi_b_ton:,.3f} <span class="exec-card-unit">Ton CO2e</span></div>
            </div>
            <div class="exec-card-subtext">
                Material: <b>{mat_b[:45]}</b><br>
                <b>Potensi Reduksi: {delta_ton:,.3f} Ton CO2e ({hemat_emisi_pct:.1f}%)</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    comp_df = pd.DataFrame([
        {"Skenario": "Skenario A (Baseline)", "Emisi (Ton CO2e)": emisi_a_ton},
        {"Skenario": "Skenario B (Green Design)", "Emisi (Ton CO2e)": emisi_b_ton},
    ])

    fig_comp = px.bar(
        comp_df, 
        x="Skenario", 
        y="Emisi (Ton CO2e)", 
        color="Skenario", 
        title="Visualisasi Komparasi Total Emisi Karbon (Ton CO2e)",
        color_discrete_map={
            "Skenario A (Baseline)": "#ef4444",
            "Skenario B (Green Design)": "#10b981"
        }
    )
    fig_comp.update_layout(font_family="Plus Jakarta Sans", margin=dict(t=50, b=20, l=20, r=20), showlegend=False)
    st.plotly_chart(fig_comp, use_container_width=True)

# ==========================================
# MENU 5: SIKLUS HIDUP EMISI & SOLUSI
# ==========================================
elif menu == "📚 Siklus Hidup Emisi & Solusi":
    st.title("📚 Edukasi: Siklus Hidup Karbon dalam Teknik Sipil")
    st.write("Analisis Komprehensif Penilaian Siklus Hidup (*Life Cycle Assessment / LCA*) pada Struktur Bangunan Gedung dan Infrastruktur.")

    st.subheader("📊 Tipikal Distribusi Emisi Karbon Bangunan Gedung (Masa Layan 50 Tahun)")
    col_lca1, col_lca2 = st.columns([1, 1])
    
    with col_lca1:
        lca_chart_df = pd.DataFrame([
            {"Tahapan LCA": "Produksi Material (A1-A3)", "Proporsi (%)": 28},
            {"Tahapan LCA": "Pengangkutan & Logistik (A4)", "Proporsi (%)": 4},
            {"Tahapan LCA": "Konstruksi di Lapangan (A5)", "Proporsi (%)": 5},
            {"Tahapan LCA": "Operasional 50 Tahun (B1-B7)", "Proporsi (%)": 60},
            {"Tahapan LCA": "Pembongkaran & Akhir Masa Layan (C1-C4)", "Proporsi (%)": 3},
        ])
        fig_lca_donut = px.pie(
            lca_chart_df, 
            names="Tahapan LCA", 
            values="Proporsi (%)", 
            hole=0.45,
            title="Estimasi Kontribusi Emisi Karbon (%)",
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig_lca_donut.update_layout(font_family="Plus Jakarta Sans", margin=dict(t=50, b=20, l=20, r=20))
        st.plotly_chart(fig_lca_donut, use_container_width=True)

    with col_lca2:
        st.markdown("""
        **Penjelasan Pembagian Siklus Hidup (Standar BS EN 15978):**
        * **A1-A3 (Product Stage):** *Cradle-to-Gate* — Pembakaran batu kapur, peleburan bijih besi, dan pembuatan bahan siap pakai.
        * **A4-A5 (Construction Stage):** Pengiriman logistik material ke tapak proyek serta bahan bakar alat-alat berat di lapangan.
        * **B1-B7 (Use Stage):** Penggunaan listrik HVAC/AC, penerangan, dan pemeliharaan gedung selama puluhan tahun.
        * **C1-C4 (End of Life Stage):** Proses perubuhan gedung, pemilahan, pengangkutan limbah puing, dan pembuangan akhir.
        * **Modul D (Beyond System Boundary):** Potensi penghematan emisi dari daur ulang material (*Recycling / Reuse*).
        """)

    st.markdown("---")
    st.subheader("🔍 Detail Tahapan LCA & Strategi Mitigasi Teknik Sipil")

    t1, t2, t3, t4, t5 = st.tabs([
        "1️⃣ Material & Ekstraksi (A1-A3)", 
        "2️⃣ Pengangkutan Logistik (A4)", 
        "3️⃣ Pelaksanaan Konstruksi (A5)", 
        "4️⃣ Operasional Bangunan (B1-B7)", 
        "5️⃣ Pembongkaran & Daur Ulang (C1-C4 & D)"
    ])

    with t1:
        st.markdown("### 1. Embodied Carbon: Material & Ekstraksi (Modul A1 - A3)")
        st.write("Tahap ini mencakup ekstraksi bahan mentah, pengangkutan ke pabrik pemrosesan, dan manufaktur material konstruksi.")
        col_t1a, col_t1b = st.columns(2)
        with col_t1a:
            st.error("""
            **🔥 Sumber Emisi Utama:**
            * **Kalsinasi Batu Kapur:** Pembakaran $\\text{CaCO}_3 \\rightarrow \\text{CaO} + \\text{CO}_2$ pada kiln semen dengan suhu $>1400^\\circ\\text{C}$.
            * **Peleburan Bijih Besi:** Penggunaan batu bara koks (*coking coal*) pada *Blast Furnace* pabrik baja.
            * **Pembuatan Kaca & Keramik:** Pembakaran bahan mentah menggunakan gas alam cair bertekanan tinggi.
            """)
        with col_t1b:
            st.success("""
            **💡 Solusi & Best Practices:**
            * **Substitusi Semen (SCM):** Gunakan *Fly Ash*, *GGBFS / Slag*, atau *Pozzolan* alami hingga 30%-50% volume campuran beton.
            * **Baja Daur Ulang:** Gunakan baja hasil *Electric Arc Furnace* (EAF) yang menghemat emisi hingga 60%.
            * **Kayu Rekayasa:** Manfaatkan *Cross-Laminated Timber* (CLT) sebagai pengikat karbon (*Carbon Sink*).
            """)

    with t2:
        st.markdown("### 2. Transport Carbon: Pengangkutan Logistik (Modul A4)")
        st.write("Emisi gas buang dari armada angkutan bahan mentah dari kuari (*quarry*) ke pabrik pengolahan, serta pendistribusian material ke tapak proyek.")
        col_t2a, col_t2b = st.columns(2)
        with col_t2a:
            st.error("""
            **🔥 Sumber Emisi Utama:**
            * **Konsumsi Solar Transportasi:** Truk tronton/dumper, kapal tongkang, dan kereta api pengangkut material berat.
            * **Jarak Pasok Rantai Logistik:** Pengimporan material struktur khusus dari luar daerah/luar negeri.
            * **Beban Muatan Kosong (*Empty Return Runs*):** Truk yang kembali ke pabrik dalam kondisi kosong.
            """)
        with col_t2b:
            st.success("""
            **💡 Solusi & Best Practices:**
            * **Local Material Sourcing:** Memprioritaskan pembelian material dari produsen dalam radius $< 100\\text{ km}$ dari tapak proyek.
            * **Optimasi Rute & Armada:** Menggunakan truk bermesin efisien (Euro IV/VI) dan memaksimalkan kapasitas muatan angkut.
            * **Transportasi Jalur Laut/Kereta:** Mengalihkan moda transportasi darat jarak jauh ke rute kapal/kereta yang beremisi lebih rendah per ton-km.
            """)

    with t3:
        st.markdown("### 3. Construction Carbon: Pelaksanaan di Lapangan (Modul A5)")
        st.write("Seluruh emisi yang timbul dari aktivitas di lokasi pembangunan proyek sejak pekerjaan tanah (*earthworks*) hingga penyelesaian gedung.")
        col_t3a, col_t3b = st.columns(2)
        with col_t3a:
            st.error("""
            **🔥 Sumber Emisi Utama:**
            * **BBM Alat Berat:** Ekskavator, *Bulldozer*, *Tower Crane*, Mesin Pancang (*Piling Rig*), dan Genset lapangan.
            * **Pembersihan Lahan (*Land Clearing*):** Hilangnya tutupan vegetasi dan gangguan pada struktur tanah alami.
            * **Material Waste:** Sisa potongan baja tulangan, beton yang mengeras di truk *mixer*, dan acuan kayu (*formwork*) sekali pakai.
            """)
        with col_t3b:
            st.success("""
            **💡 Solusi & Best Practices:**
            * **Konstruksi Precast / Modular:** Memindahkan porsi pekerjaan beton ke pabrik agar penggunaan alat berat di lapangan efisien.
            * **Alat Berat Listrik / Hibrida:** Mengalihkan mesin berbahan bakar diesel ke armada alat berat listrik (*Electrified Heavy Equipment*).
            * **Penggunaan Bekisting Baja/Aluminium:** Menggantikan tripleks sekali pakai dengan sistem acuan yang bisa dipasang ulang ratusan kali.
            """)

    with t4:
        st.markdown("### 4. Operational Carbon: Pengoperasian Gedung (Modul B1 - B7)")
        st.write("Emisi yang dihasilkan dari konsumsi energi harian saat gedung dihuni selama puluhan tahun.")
        col_t4a, col_t4b = st.columns(2)
        with col_t4a:
            st.error("""
            **🔥 Sumber Emisi Utama:**
            * **Sistem HVAC (AC):** Penggunaan beban listrik chiller/pembeku dan kebocoran bahan pendingin (*refrigerant*).
            * **Pencahayaan & Peralatan Listrik:** Konsumsi listrik terus-menerus dari jaringan PLN berbasis fosil/batu bara.
            * **Konsumsi Air Bersih & Pompa:** Energi untuk memompa dan mengolah air di dalam gedung.
            """)
        with col_t4b:
            st.success("""
            **💡 Solusi & Best Practices:**
            * **Desain Arsitektur Pasif:** Memaksimalkan orientasi bangunan untuk pencahayaan alami dan ventilasi silang (*cross-ventilation*).
            * **Pemasangan PV Solar Panel:** Mengintegrasikan panel surya (*Building Integrated Photovoltaics / BIPV*) pada atap atau fasad.
            * **Fasad Berkinerja Tinggi:** Menggunakan kaca *Low-E* berlapis ganda (*Double Glazing*) untuk mengurangi panas matahari yang masuk ke gedung.
            """)

    with t5:
        st.markdown("### 5. End-of-Life & Beyond: Daur Ulang (Modul C1 - C4 & D)")
        st.write("Proses perubuhan struktur gedung saat akhir masa layan, pengangkutan sampah bangunan, serta potensi manfaat daur ulang.")
        col_t5a, col_t5b = st.columns(2)
        with col_t5a:
            st.error("""
            **🔥 Sumber Emisi Utama:**
            * **Pembongkaran Struktur (Demolisi):** Energi dari alat pemukul (*breaker*), peledakan, dan penghancuran beton.
            * **Pengangkutan Puing ke TPA:** Emisi pengiriman limbah konstruksi ke tempat pembuangan akhir.
            * **Emisi Landfill:** Penguraian sisa kayu/organik yang menghasilkan gas metana ($\\text{CH}_4$).
            """)
        with col_t5b:
            st.success("""
            **💡 Solusi & Best Practices:**
            * **Design for Deconstruction (DfD):** Merancang sambungan baut (*bolted connections*) agar elemen struktur mudah dibongkar dan dipakai ulang.
            * **Recycled Concrete Aggregate (RCA):** Menghancurkan puing beton lama untuk dijadikan agregat kasar campuran beton baru atau lapis pondasi jalan.
            * **Daur Ulang Baja 100%:** Melakukan peleburan ulang seluruh baja tulangan dan baja profil bekas perubuhan.
            """)

# ==========================================
# FOOTER EKSEKUTIF
# ==========================================
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #94a3b8; font-size: 0.88rem;'>"
    "EcoBuild Pro v2.0 • Executive Civil Carbon & Cost Intelligence • Designed by <b>CV Kingsman IDN</b>"
    "</p>", 
    unsafe_allow_html=True
)
