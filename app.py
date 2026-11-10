import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import base64
import json
import io
import math
import re
import warnings
warnings.filterwarnings('ignore')

# Penanganan opsional untuk ReportLab (PDF)
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

# Penanganan opsional untuk openpyxl (Excel)
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

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
    
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 3.5rem !important;
    }}

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

    .exec-metric-card {{
        background: #ffffff;
        border-radius: 18px;
        padding: 24px;
        position: relative;
        border: 1px solid var(--color-slate-200);
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.06);
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}

    .exec-metric-card.status-optimal {{
        border-top: 5px solid var(--color-emerald-500);
        background: linear-gradient(180deg, #ffffff 0%, var(--color-emerald-50) 100%);
    }}
    .exec-metric-card.status-moderate {{
        border-top: 5px solid var(--color-amber-500);
        background: linear-gradient(180deg, #ffffff 0%, var(--color-amber-50) 100%);
    }}
    .exec-metric-card.status-critical {{
        border-top: 5px solid var(--color-rose-500);
        background: linear-gradient(180deg, #ffffff 0%, var(--color-rose-50) 100%);
    }}
    .exec-metric-card.theme-finance {{
        border-top: 5px solid var(--color-blue-600);
        background: linear-gradient(180deg, #ffffff 0%, var(--color-blue-50) 100%);
    }}
    .exec-metric-card.theme-efficiency {{
        border-top: 5px solid #7c3aed;
        background: linear-gradient(180deg, #ffffff 0%, #f5f3ff 100%);
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
        backdrop-filter: blur(12px);
    }}
    .sidebar-logo-img {{
        max-width: 135px;
        margin: 0 auto 10px auto;
        display: block;
    }}
    .sidebar-brand-title {{
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffffff !important;
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
        margin-top: 4px;
    }}
    .sidebar-nav-label {{
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #94a3b8 !important;
        margin: 16px 0 10px 4px;
    }}
    
    div[data-testid="stRadio"] label {{
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 10px 14px !important;
        margin-bottom: 4px;
    }}
    div[data-testid="stRadio"] label[data-checked="true"] {{
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.22) 0%, rgba(6, 78, 59, 0.15) 100%) !important;
        border-left: 4px solid #10b981 !important;
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

    .stButton > button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# KAMUS PENERJEMAHAN MATERIAL ICE (ID <-> EN)
# ==========================================
TRANSLATIONS_CAT = {
    "Concrete": "Beton & Semen",
    "Steel": "Struktur Baja",
    "Timber": "Kayu & Bekisting",
    "Clay Bricks": "Pasangan Bata",
    "Bricks": "Pasangan Bata",
    "Aggregates": "Agregat & Pasir",
    "Mortar": "Mortar & Spesi",
    "Glass": "Kaca & Fasad",
    "Aluminium": "Aluminium & Kusen",
    "Insulation": "Insulasi & Peredam",
    "Plastics": "Plastik & Pipa",
    "Asphalt": "Pekerjaan Aspal",
    "General Construction Material": "Material Konstruksi Umum",
    "Cement": "Semen"
}

REPLACEMENT_TERMS = [
    ("Reinforced Concrete", "Beton Bertulang"),
    ("Precast Concrete", "Beton Pracetak"),
    ("Ready Mix Concrete", "Beton Ready Mix"),
    ("Structural Steel Section", "Profil Baja Struktur"),
    ("Structural Steel", "Baja Struktur"),
    ("Stainless Steel", "Baja Tahan Karat (Stainless)"),
    ("Galvanised Steel", "Baja Galvanis"),
    ("Galvanized Steel", "Baja Galvanis"),
    ("Steel Rebar", "Baja Tulangan"),
    ("Steel Sections", "Profil Baja"),
    ("Steel Sheet", "Pelat Baja"),
    ("Steel Plate", "Pelat Baja"),
    ("Steel Pipe", "Pipa Baja"),
    ("Steel Wire", "Kawat Baja"),
    ("Steel", "Baja"),
    ("Concrete", "Beton"),
    ("Engineered Timber", "Kayu Olahan / Rekayasa"),
    ("Timber", "Kayu"),
    ("Plywood", "Kayu Lapis / Tripleks"),
    ("Hardwood", "Kayu Keras"),
    ("Softwood", "Kayu Lunak"),
    ("Glulam", "Kayu Glulam"),
    ("CLT", "Kayu CLT"),
    ("Clay Bricks", "Bata Merah Press"),
    ("Brick", "Bata"),
    ("Mortar", "Mortar"),
    ("Cement", "Semen"),
    ("Flat Glass", "Kaca Datar"),
    ("Glass", "Kaca"),
    ("Aluminium Extrusions", "Profil Aluminium"),
    ("Aluminium Sheet", "Pelat Aluminium"),
    ("Aluminium", "Aluminium"),
    ("Copper Pipe", "Pipa Tembaga"),
    ("Copper", "Tembaga"),
    ("Aggregate", "Agregat"),
    ("Sand", "Pasir"),
    ("Gravel", "Kerikil"),
    ("Rockwool", "Rockwool Peredam"),
    ("Glasswool", "Glasswool Peredam"),
    ("Insulation", "Insulasi"),
    ("Asphalt", "Aspal"),
    ("Bitumen", "Bitumen"),
    ("Gypsum Board", "Papan Gypsum / Plafon"),
    ("Plasterboard", "Papan Gypsum"),
    ("Gypsum", "Gipsum"),
    ("PVC Pipe", "Pipa PVC"),
    ("HDPE Pipe", "Pipa HDPE"),
    ("Plastic", "Plastik")
]

def translate_material_to_id(en_name):
    res = str(en_name).strip()
    for en_term, id_term in REPLACEMENT_TERMS:
        if en_term.lower() in res.lower() and id_term.lower() not in res.lower():
            pattern = re.compile(re.escape(en_term), re.IGNORECASE)
            new_res = pattern.sub(id_term, res)
            new_res = re.sub(r'(\b[\w\s]+\b)\s*/\s*\1', r'\1', new_res, flags=re.IGNORECASE)
            res = new_res
    return res.strip()

# ==========================================
# HELPER & PARSER CERDAS UNTUK IMPOR FILE RAB EXCEL / CSV
# ==========================================
def smart_read_rab(file_obj, filename):
    if filename.endswith(".csv"):
        df_raw = pd.read_csv(file_obj, header=None)
    else:
        df_raw = pd.read_excel(file_obj, header=None)
        
    header_row_idx = None
    for idx, row in df_raw.iterrows():
        row_str = " ".join([str(val).lower() for val in row.values if pd.notna(val)])
        if ("material" in row_str or "nama" in row_str or "bahan" in row_str) and ("jumlah" in row_str or "volume" in row_str or "qty" in row_str):
            header_row_idx = idx
            break
            
    file_obj.seek(0)
    if header_row_idx is not None:
        return pd.read_csv(file_obj, header=header_row_idx) if filename.endswith(".csv") else pd.read_excel(file_obj, header=header_row_idx)
    else:
        return pd.read_csv(file_obj) if filename.endswith(".csv") else pd.read_excel(file_obj)

def get_robust_col_map(columns):
    col_map = {}
    cols_clean = [str(c).strip() for c in columns]
    
    for c in cols_clean:
        clow = c.lower()
        if clow in ["material", "nama material", "nama_material", "nama bahan", "bahan"]:
            col_map["Material"] = c
            break
    if "Material" not in col_map:
        for c in cols_clean:
            clow = c.lower()
            if "nama" in clow or ("material" in clow and "tipe" not in clow and "jenis" not in clow):
                col_map["Material"] = c
                break

    for c in cols_clean:
        clow = c.lower()
        if "total" not in clow and ("jumlah" in clow or "volume" in clow or "qty" in clow):
            col_map["Jumlah"] = c
            break

    for c in cols_clean:
        clow = c.lower()
        if clow in ["satuan", "unit"]:
            col_map["Satuan"] = c
            break
    if "Satuan" not in col_map:
        for c in cols_clean:
            clow = c.lower()
            if "satuan" in clow and "harga" not in clow:
                col_map["Satuan"] = c
                break

    for c in cols_clean:
        clow = c.lower()
        if "faktor" in clow or "fe" in clow or "co2e/unit" in clow or "co2e/kg" in clow or "emission factor" in clow:
            col_map["Faktor Emisi"] = c
            break
    if "Faktor Emisi" not in col_map:
        for c in cols_clean:
            clow = c.lower()
            if "total" not in clow and ("emisi" in clow or "co2" in clow):
                col_map["Faktor Emisi"] = c
                break

    for c in cols_clean:
        clow = c.lower()
        if "harga satuan" in clow or "unit price" in clow or "harga/unit" in clow or "harga/satuan" in clow:
            col_map["Harga Satuan"] = c
            break
    if "Harga Satuan" not in col_map:
        for c in cols_clean:
            clow = c.lower()
            if "total" not in clow and ("harga" in clow or "price" in clow):
                col_map["Harga Satuan"] = c
                break
                
    return col_map

# ==========================================
# 2. DYNAMIC EXCEL ICE DATABASE PARSER (MULTILINGUAL)
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
        default_data = [
            {"Kategori": "Concrete", "Nama Material": "Beton K-300 (Konvensional)", "Faktor Emisi (kg CO2e/kg)": 0.134, "Satuan": "kg"},
            {"Kategori": "Steel", "Nama Material": "Baja Tulangan (Konvensional)", "Faktor Emisi (kg CO2e/kg)": 1.990, "Satuan": "kg"},
            {"Kategori": "Timber", "Nama Material": "Kayu Olahan / Engineered Timber", "Faktor Emisi (kg CO2e/kg)": 0.300, "Satuan": "kg"},
            {"Kategori": "Clay Bricks", "Nama Material": "Bata Merah Press", "Faktor Emisi (kg CO2e/kg)": 0.240, "Satuan": "kg"},
        ]
        df_out = pd.DataFrame(default_data)
    else:
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
            default_ver = version_str
        except Exception:
            default_ver = "Educational (V5.0) - Jun 2026"
            df_out = pd.DataFrame([
                {"Kategori": "Concrete", "Nama Material": "Beton Standard", "Faktor Emisi (kg CO2e/kg)": 0.134, "Satuan": "kg"}
            ])

    # Penambahan Kolom Bahasa
    df_out["Kategori (EN)"] = df_out["Kategori"]
    df_out["Kategori (ID)"] = df_out["Kategori (EN)"].map(lambda x: TRANSLATIONS_CAT.get(x, x))
    df_out["Nama Material (EN)"] = df_out["Nama Material"]
    df_out["Nama Material (ID)"] = df_out["Nama Material (EN)"].apply(translate_material_to_id)
    
    def make_bilingual(row):
        id_name = row["Nama Material (ID)"]
        en_name = row["Nama Material (EN)"]
        if id_name.lower() != en_name.lower():
            return f"{id_name} ({en_name})"
        return en_name
        
    df_out["Nama Material (Bilingual)"] = df_out.apply(make_bilingual, axis=1)
    
    return default_ver, df_out

ice_version, df_ice_materials = load_ice_excel_database()

if "calc_num_items" not in st.session_state:
    st.session_state["calc_num_items"] = 3

if "dist_zone" not in st.session_state:
    st.session_state["dist_zone"] = "🟢 Zona Lokal (< 25 km)"

if "dist_km" not in st.session_state:
    st.session_state["dist_km"] = 25.0

if "fuel_liter" not in st.session_state:
    st.session_state["fuel_liter"] = 100.0

if "app_lang" not in st.session_state:
    st.session_state["app_lang"] = "🇮🇩 Bahasa Indonesia"

def get_active_material_options(df_ice, lang_mode):
    if lang_mode == "🇬🇧 English":
        return df_ice["Nama Material (EN)"].tolist()
    elif lang_mode == "🇮🇩🇬🇧 Dwi-Bahasa (Bilingual)":
        return df_ice["Nama Material (Bilingual)"].tolist()
    else:
        return df_ice["Nama Material (ID)"].tolist()

# ==========================================
# 3. HELPER GENERATOR LAPORAN PDF & EXCEL
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

def generate_excel_report(df_results, total_emission_ton, total_cost, cost_per_ton, transport_emission_kg, equipment_emission_kg, ice_ver):
    if not HAS_OPENPYXL:
        return b""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Laporan Emisi & Biaya"
    ws.views.sheetView[0].showGridLines = True

    header_fill = PatternFill(start_color="064E3B", end_color="064E3B", fill_type="solid")
    accent_fill = PatternFill(start_color="ECFDF5", end_color="ECFDF5", fill_type="solid")
    title_font = Font(name="Calibri", size=14, bold=True, color="064E3B")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=11, bold=True)
    regular_font = Font(name="Calibri", size=11)
    
    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    ws['A1'] = "EcoBuild Pro v2.0 - Laporan Analisis Emisi Karbon & Biaya Proyek"
    ws['A1'].font = title_font
    ws['A2'] = f"Basis Data: ICE Database {ice_ver} | Standar Evaluasi: BS EN 15978 (A1-A5)"
    ws['A2'].font = Font(name="Calibri", size=10, italic=True, color="475569")

    ws['A4'] = "RINGKASAN EKSEKUTIF PROYEK"
    ws['A4'].font = bold_font
    
    kpi_headers = ["Parameter Analisis", "Nilai Output Proyek"]
    for col_idx, text in enumerate(kpi_headers, 1):
        cell = ws.cell(row=5, column=col_idx, value=text)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="left", vertical="center")

    kpis = [
        ("Total Emisi Karbon Proyek", total_emission_ton, r'0.00 "Ton CO2e"'),
        ("Total Estimasi Biaya Material", total_cost, r'"Rp "#,##0'),
        ("Rasio Biaya / Emisi Karbon", cost_per_ton, r'"Rp "#,##0 "/ Ton CO2e"'),
        ("Emisi Pengangkutan Logistik (A4)", transport_emission_kg / 1000, r'0.00 "Ton CO2e"'),
        ("Emisi BBM Alat Berat (A5)", equipment_emission_kg / 1000, r'0.00 "Ton CO2e"')
    ]

    for row_idx, (label, val, num_fmt) in enumerate(kpis, 6):
        c1 = ws.cell(row=row_idx, column=1, value=label)
        c2 = ws.cell(row=row_idx, column=2, value=val)
        c1.font = regular_font
        c2.font = bold_font
        c1.border = thin_border
        c2.border = thin_border
        c2.number_format = num_fmt
        c1.fill = accent_fill
        c2.fill = accent_fill

    start_row = 12
    ws.cell(row=start_row, column=1, value="RINCIAN MATERIAL PROYEK & FAKTOR EMISI").font = bold_font
    
    mat_headers = ["No", "Material", "Jumlah / Volume", "Satuan", "Faktor Emisi (kg CO2e/unit)", "Total Emisi (kg CO2e)", "Total Biaya (Rp)"]
    for col_idx, text in enumerate(mat_headers, 1):
        cell = ws.cell(row=start_row+1, column=col_idx, value=text)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    curr_row = start_row + 2
    for idx, row in df_results.iterrows():
        ws.cell(row=curr_row, column=1, value=idx+1).alignment = Alignment(horizontal="center")
        ws.cell(row=curr_row, column=2, value=str(row['Material']))
        
        c_qty = ws.cell(row=curr_row, column=3, value=float(row['Jumlah']))
        c_qty.number_format = "#,##0.00"
        
        ws.cell(row=curr_row, column=4, value=str(row['Satuan'])).alignment = Alignment(horizontal="center")
        
        fe = float(row['Emisi (kg CO2e)']) / float(row['Jumlah']) if float(row['Jumlah']) > 0 else 0
        c_fe = ws.cell(row=curr_row, column=5, value=fe)
        c_fe.number_format = "0.000000"
        
        c_e = ws.cell(row=curr_row, column=6, value=float(row['Emisi (kg CO2e)']))
        c_e.number_format = "#,##0.00"
        
        c_c = ws.cell(row=curr_row, column=7, value=float(row['Biaya (Rp)']))
        c_c.number_format = r'"Rp "#,##0'
        
        for col_idx in range(1, 8):
            cell = ws.cell(row=curr_row, column=col_idx)
            cell.font = regular_font
            cell.border = thin_border
            
        curr_row += 1

    tot_row = curr_row
    ws.cell(row=tot_row, column=1, value="TOTAL MATERIAL").font = bold_font
    ws.cell(row=tot_row, column=1).alignment = Alignment(horizontal="center")
    
    c_tot_e = ws.cell(row=tot_row, column=6, value=f"=SUM(F{start_row+2}:F{tot_row-1})")
    c_tot_e.font = bold_font
    c_tot_e.number_format = "#,##0.00"
    
    c_tot_c = ws.cell(row=tot_row, column=7, value=f"=SUM(G{start_row+2}:G{tot_row-1})")
    c_tot_c.font = bold_font
    c_tot_c.number_format = r'"Rp "#,##0'

    for col_idx in range(1, 8):
        cell = ws.cell(row=tot_row, column=col_idx)
        cell.border = thin_border
        cell.fill = accent_fill

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 14)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()

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

    # SWITCHER BAHASA MATERIAL
    st.markdown('<div class="sidebar-nav-label">🌐 Opsi Bahasa Material</div>', unsafe_allow_html=True)
    st.selectbox(
        "Pilih Bahasa Material ICE:",
        ["🇮🇩 Bahasa Indonesia", "🇬🇧 English", "🇮🇩🇬🇧 Dwi-Bahasa (Bilingual)"],
        key="app_lang",
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="sidebar-nav-label">🧭 Navigasi Utama</div>', unsafe_allow_html=True)
    menu = st.radio(
        "Pilih Menu Utama:",
        ["🏠 Beranda", "🧮 Kalkulator & Analisis Proyek", "📊 Database Material ICE (Otomatis)", "⚖️ Simulasi Komparasi Desain", "📚 Siklus Hidup Emisi & Solusi"],
        key="nav_menu",
        label_visibility="collapsed"
    )

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
            <span style="opacity: 0.8;">Mode Bahasa:</span>
            <span style="font-weight: 700; color: #38bdf8;">{st.session_state['app_lang']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
                <span class="hero-chip">⚡ Quick-Start RAB Presets</span>
                <span class="hero-chip">🚚 Presets Zona Logistik</span>
                <span class="hero-chip">🌐 Multilingual Material Switch</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("🌐 Latar Belakang & Urgensi Sektor Konstruksi")
    col_bg1, col_bg2 = st.columns([1.1, 0.9])
    
    with col_bg1:
        st.write("""
        Industri konstruksi dan teknik sipil bertanggung jawab atas **hampir 40% emisi gas rumah kaca global**. 
        Emisi tidak hanya berasal dari pemakaian listrik saat gedung beroperasi (*Operational Carbon*), tetapi juga sejak 
        proses ekstraksi bahan mentah, pengangkutan logistik, hingga konsumsi BBM alat berat di lapangan (*Embodied & Construction Carbon*).
        
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
        
        Apabila para pelaku di industri **konstruksi dan teknik sipil acuh** terhadap jejak karbon dari material serta pelaksanaan proyek yang mereka bangun, maka akumulasi emisi akan semakin tidak terkendali. Sektor teknik sipil harus mengambil peran aktif dalam memitigasi emisi sejak tahap perencanaan.
        """)

        img_karhutla = get_existing_image(["karhutla.jpg", "karhutla.jfif", "karhutla.jpg.jfif"])
        if img_karhutla:
            st.image(img_karhutla, caption="Refleksi Urgensi Bencana Karhutla & Dampak Emisi Karbon", use_container_width=True)

    st.markdown("---")
    st.info(f"📚 **Basis Data Emisi Karbon Terintegrasi:** Data emisi material pada aplikasi ini terhubung langsung secara otomatis dengan **ICE Database ({ice_version})** dari Circular Ecology & University of Bath.")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 22px 18px 16px 18px; min-height: 145px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 12px;">
            <div>
                <div style="font-size: 1.8rem; margin-bottom: 8px;">📦</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 4px;">Material Carbon</div>
                <div style="font-size: 0.82rem; color: #64748b; line-height: 1.45;">Hitung jejak karbon dari ratusan varian material struktur bersertifikasi ICE.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("Buka Kalkulator ➔", key="btn_nav_mat", use_container_width=True, on_click=navigate_to, args=("🧮 Kalkulator & Analisis Proyek",))

    with col2:
        st.markdown("""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 22px 18px 16px 18px; min-height: 145px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 12px;">
            <div>
                <div style="font-size: 1.8rem; margin-bottom: 8px;">🚛</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 4px;">Logistik & Alat</div>
                <div style="font-size: 0.82rem; color: #64748b; line-height: 1.45;">Integrasi emisi pengangkutan armada truk & BBM solar alat berat di tapak proyek.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("Hitung Logistik ➔", key="btn_nav_log", use_container_width=True, on_click=navigate_to, args=("🧮 Kalkulator & Analisis Proyek",))

    with col3:
        st.markdown("""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 22px 18px 16px 18px; min-height: 145px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 12px;">
            <div>
                <div style="font-size: 1.8rem; margin-bottom: 8px;">⚖️</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 4px;">Komparasi Skenario</div>
                <div style="font-size: 0.82rem; color: #64748b; line-height: 1.45;">Bandingkan Desain Konvensional vs Green Alternative secara instan.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("Mulai Komparasi ➔", key="btn_nav_komp", use_container_width=True, on_click=navigate_to, args=("⚖️ Simulasi Komparasi Desain",))

    with col4:
        st.markdown("""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 22px 18px 16px 18px; min-height: 145px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 12px;">
            <div>
                <div style="font-size: 1.8rem; margin-bottom: 8px;">📚</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 4px;">Siklus Hidup & LCA</div>
                <div style="font-size: 0.82rem; color: #64748b; line-height: 1.45;">Pelajari modul tahapan emisi A1-D dan strategi mitigasi teknis teknik sipil.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("Pelajari LCA ➔", key="btn_nav_lca", use_container_width=True, on_click=navigate_to, args=("📚 Siklus Hidup Emisi & Solusi",))

# ==========================================
# MENU 2: KALKULATOR & ANALISIS PROYEK
# ==========================================
elif menu == "🧮 Kalkulator & Analisis Proyek":
    st.title("🧮 Kalkulator Emisi & Biaya Proyek")
    st.write(f"Mode Bahasa Aktif: **{st.session_state['app_lang']}**. Hitung emisi dan biaya proyek dengan memilih material dari **ICE Database** atau mengisi **Material Kustom** secara bebas.")

    # ---------------------------------------------------------
    # PRESET TEMPLATE RAB PROYEK TIPIKAL (QUICK-START)
    # ---------------------------------------------------------
    st.markdown("### ⚡ Quick-Start: Pilih Template RAB Tipikal Proyek")
    st.caption("Pilih template proyek di bawah ini untuk mengisi formulir material secara otomatis tanpa perlu mengetik satu per satu:")
    
    col_tpl1, col_tpl2, col_tpl3 = st.columns(3)
    
    def apply_preset_template(preset_key):
        if preset_key == "rumah":
            st.session_state["input_num_items"] = 5
            st.session_state["calc_num_items"] = 5
            st.session_state["dist_zone"] = "🟢 Zona Lokal (< 25 km)"
            st.session_state["dist_km"] = 15.0
            st.session_state["fuel_liter"] = 80.0
            
            items = [
                ("Beton Ready Mix", 18000.0, 1250.0),
                ("Baja Tulangan", 2500.0, 14500.0),
                ("Bata Merah Press", 15000.0, 850.0),
                ("Kayu Olahan / Rekayasa", 1200.0, 1800.0),
                ("Kaca Datar", 250.0, 22000.0)
            ]
        elif preset_key == "gedung":
            st.session_state["input_num_items"] = 6
            st.session_state["calc_num_items"] = 6
            st.session_state["dist_zone"] = "🟡 Zona Regional (25 - 100 km)"
            st.session_state["dist_km"] = 55.0
            st.session_state["fuel_liter"] = 450.0
            
            items = [
                ("Beton Ready Mix", 150000.0, 1250.0),
                ("Baja Tulangan", 28000.0, 14500.0),
                ("Profil Baja Struktur", 15000.0, 16500.0),
                ("Profil Aluminium", 3500.0, 48000.0),
                ("Papan Gypsum / Plafon", 6000.0, 8500.0),
                ("Pipa PVC", 1800.0, 28000.0)
            ]
        elif preset_key == "jalan":
            st.session_state["input_num_items"] = 3
            st.session_state["calc_num_items"] = 3
            st.session_state["dist_zone"] = "🟡 Zona Regional (25 - 100 km)"
            st.session_state["dist_km"] = 40.0
            st.session_state["fuel_liter"] = 600.0
            
            items = [
                ("Aspal", 45000.0, 12000.0),
                ("Agregat", 180000.0, 250.0),
                ("Pasir", 60000.0, 180.0)
            ]
            
        opts = get_active_material_options(df_ice_materials, st.session_state["app_lang"])
        for idx, (target_keyword, qty, price) in enumerate(items):
            matched_option = None
            for opt in opts:
                if target_keyword.lower() in opt.lower():
                    matched_option = opt
                    break
            if not matched_option:
                matched_option = opts[idx] if idx < len(opts) else "➕ Material Kustom (Isi Sendiri)"
                
            st.session_state[f"calc_sel_{idx}"] = matched_option
            st.session_state[f"q_val_{idx}"] = qty
            st.session_state[f"p_val_{idx}"] = price
            st.session_state[f"c_qty_{idx}"] = qty
            st.session_state[f"c_price_{idx}"] = price

    with col_tpl1:
        if st.button("🏡 Rumah Tinggal 2 Lantai", use_container_width=True, help="Muat 5 material struktur standar rumah tinggal"):
            apply_preset_template("rumah")
            st.rerun()

    with col_tpl2:
        if st.button("🏢 Gedung Kantor 5 Lantai", use_container_width=True, help="Muat 6 material bertulang & fasad gedung perkantoran"):
            apply_preset_template("gedung")
            st.rerun()

    with col_tpl3:
        if st.button("🛣️ Pekerjaan Jalan Aspal 1 km", use_container_width=True, help="Muat 3 material perkerasan aspal & agregat jalan"):
            apply_preset_template("jalan")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("💾 Backup / Restorasi Proyek (JSON) & Impor File RAB Excel", expanded=False):
        c_exp1, c_exp2 = st.columns(2)
        
        with c_exp1:
            st.subheader("📥 Impor File RAB (.xlsx / .csv)")
            uploaded_rab = st.file_uploader("Unggah file RAB Excel/CSV:", type=["xlsx", "csv"], key="rab_uploader")
            
            if uploaded_rab is not None:
                file_id = f"{uploaded_rab.name}_{uploaded_rab.size}"
                if st.session_state.get("last_uploaded_rab_id") != file_id:
                    try:
                        df_rab = smart_read_rab(uploaded_rab, uploaded_rab.name)
                        df_rab.columns = [str(c).strip() for c in df_rab.columns]
                        
                        col_map = get_robust_col_map(df_rab.columns)

                        if "Material" in col_map and "Jumlah" in col_map:
                            num_r = len(df_rab)
                            st.session_state["calc_num_items"] = num_r
                            st.session_state["input_num_items"] = num_r
                            
                            ice_lookup = {}
                            for _, r_mat in df_ice_materials.iterrows():
                                fe_val = float(r_mat["Faktor Emisi (kg CO2e/kg)"])
                                ice_lookup[str(r_mat["Nama Material (EN)"]).strip().lower()] = fe_val
                                ice_lookup[str(r_mat["Nama Material (ID)"]).strip().lower()] = fe_val
                                ice_lookup[str(r_mat["Nama Material (Bilingual)"]).strip().lower()] = fe_val

                            for idx, row in df_rab.iterrows():
                                mat_v = str(row[col_map["Material"]]).strip()
                                qty_v = float(pd.to_numeric(row[col_map["Jumlah"]], errors='coerce') or 0)
                                sat_v = str(row[col_map["Satuan"]]).strip() if "Satuan" in col_map and pd.notna(row[col_map["Satuan"]]) else "kg"
                                
                                mat_v_low = mat_v.lower()
                                if "Faktor Emisi" in col_map and pd.notna(row[col_map["Faktor Emisi"]]):
                                    fe_v = float(pd.to_numeric(row[col_map["Faktor Emisi"]], errors='coerce') or 1.0)
                                else:
                                    fe_v = ice_lookup.get(mat_v_low, 1.0)

                                if "Harga Satuan" in col_map and pd.notna(row[col_map["Harga Satuan"]]):
                                    hrg_v = float(pd.to_numeric(row[col_map["Harga Satuan"]], errors='coerce') or 10000.0)
                                else:
                                    hrg_v = 15000.0 if mat_v_low in ice_lookup else 10000.0

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
    
    def cb_add_row():
        curr = int(st.session_state.get("input_num_items", st.session_state.get("calc_num_items", 3)))
        nxt = min(30, curr + 1)
        st.session_state["input_num_items"] = nxt
        st.session_state["calc_num_items"] = nxt

    def cb_remove_row():
        curr = int(st.session_state.get("input_num_items", st.session_state.get("calc_num_items", 3)))
        nxt = max(1, curr - 1)
        st.session_state["input_num_items"] = nxt
        st.session_state["calc_num_items"] = nxt

    if "input_num_items" not in st.session_state:
        st.session_state["input_num_items"] = int(st.session_state.get("calc_num_items", 3))

    col_cnt1, col_cnt2, col_cnt3 = st.columns([1.8, 1, 1])
    with col_cnt1:
        num_items = st.number_input(
            "🔢 Jumlah Jenis Material (Form Input):",
            min_value=1,
            max_value=30,
            step=1,
            key="input_num_items"
        )
        st.session_state["calc_num_items"] = num_items
        
    with col_cnt2:
        st.write("")
        st.write("")
        st.button("➕ Tambah Baris", use_container_width=True, on_click=cb_add_row)
            
    with col_cnt3:
        st.write("")
        st.write("")
        st.button("➖ Kurangi Baris", use_container_width=True, on_click=cb_remove_row)

    ice_mat_names = get_active_material_options(df_ice_materials, st.session_state["app_lang"])
    all_mat_options = ["➕ Material Kustom (Isi Sendiri)"] + ice_mat_names

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📦 Formulir Input Material Struktur Proyek")
    st.caption(f"Tampilan pilihan material menyesuaikan dengan bahasa aktif: **{st.session_state['app_lang']}**.")
    
    results = []
    total_mat_emission_kg = 0
    total_mat_cost = 0

    for i in range(num_items):
        def_idx = (i + 1) if (i + 1) < len(all_mat_options) else 0
        curr_selection = st.session_state.get(f"calc_sel_{i}", all_mat_options[def_idx])
        is_custom = (curr_selection == "➕ Material Kustom (Isi Sendiri)")
        
        st.markdown(f"""
        <div class="mat-card-header-bar">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span class="mat-card-pill">ITEM #{i+1}</span>
                <span style="font-weight: 700; color: #1e293b; font-size: 0.95rem;">
                    {'Material Kustom' if is_custom else str(curr_selection)[:55] + ('...' if len(str(curr_selection)) > 55 else '')}
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
            sel_mat = st.selectbox(
                f"Pilih Sumber & Nama Material #{i+1}:",
                options=all_mat_options,
                index=def_idx if curr_selection not in all_mat_options else all_mat_options.index(curr_selection),
                key=f"calc_sel_{i}"
            )

            if sel_mat != "➕ Material Kustom (Isi Sendiri)":
                mat_match = df_ice_materials[
                    (df_ice_materials["Nama Material (ID)"] == sel_mat) |
                    (df_ice_materials["Nama Material (EN)"] == sel_mat) |
                    (df_ice_materials["Nama Material (Bilingual)"] == sel_mat)
                ]
                
                if not mat_match.empty:
                    mat_info = mat_match.iloc[0]
                else:
                    mat_info = {
                        "Satuan": "kg", 
                        "Faktor Emisi (kg CO2e/kg)": 0.134, 
                        "Kategori (ID)": "Material Umum",
                        "Nama Material (ID)": sel_mat
                    }
                    
                mat_name = sel_mat
                unit_str = mat_info["Satuan"]
                factor_val = float(mat_info["Faktor Emisi (kg CO2e/kg)"])
                cat_name = mat_info.get("Kategori (ID)" if "Indonesia" in st.session_state["app_lang"] else "Kategori (EN)", "Material Umum")
                
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

    st.markdown("---")
    
    # ---------------------------------------------------------
    # PRESETS ZONA JARAK LOGISTIK (MODUL A4)
    # ---------------------------------------------------------
    st.subheader("🚚 Pengangkutan Logistik & BBM Alat Berat (Modul A4 - A5)")
    st.caption("Hitung emisi transportasi logistik dari pabrik/kuari ke lokasi proyek dengan memilih preset zona atau memasukkan kilometer manual.")
    
    c_trans1, c_trans2 = st.columns(2)
    with c_trans1:
        st.markdown("**1. Presets Zona Pengangkutan Logistik (A4):**")
        zone_selected = st.radio(
            "Pilih Zona Jarak Pemasok Material:",
            [
                "🟢 Zona Lokal (< 25 km)",
                "🟡 Zona Regional (25 - 100 km)",
                "🔴 Zona Jarak Jauh / Antar Pulau (100 - 500 km)",
                "⚙️ Custom Kilometer (Manual)"
            ],
            key="dist_zone"
        )
        
        if zone_selected == "🟢 Zona Lokal (< 25 km)":
            dist_val = 15.0
        elif zone_selected == "🟡 Zona Regional (25 - 100 km)":
            dist_val = 55.0
        elif zone_selected == "🔴 Zona Jarak Jauh / Antar Pulau (100 - 500 km)":
            dist_val = 250.0
        else:
            dist_val = st.number_input(
                "Jarak Kustom (km):", 
                min_value=0.0, 
                value=float(st.session_state.get("dist_km", 25.0)), 
                step=5.0, 
                key="manual_dist_km"
            )
            
        st.session_state["dist_km"] = dist_val
        st.info(f"📍 **Jarak Aktif Dihitung:** **{dist_val:,.1f} km** *(Estimasi emisi truk ~0.25 kg CO2e / ton-km)*")

    with c_trans2:
        st.markdown("**2. Konsumsi BBM Alat Berat di Tapak Proyek (A5):**")
        st.session_state["fuel_liter"] = st.number_input(
            "Konsumsi Solar Alat Berat (Liter):", 
            min_value=0.0, 
            value=float(st.session_state["fuel_liter"]), 
            step=50.0, 
            key="calc_fuel_liter",
            help="Faktor emisi pembakaran solar industri ~ 2.68 kg CO2e / Liter diesel"
        )
        st.info(f"⛽ **Emisi Alat Berat:** **{st.session_state['fuel_liter'] * 2.68 / 1000:,.2f} Ton CO2e**")

    transport_emission_kg = st.session_state["dist_km"] * 0.25 * 10
    equipment_emission_kg = st.session_state["fuel_liter"] * 2.68
    
    total_project_emission_kg = total_mat_emission_kg + transport_emission_kg + equipment_emission_kg
    total_project_emission_ton = total_project_emission_kg / 1000
    cost_per_ton = (total_mat_cost / total_project_emission_ton) if total_project_emission_ton > 0 else 0

    st.markdown("---")
    st.subheader("📊 Executive Carbon & Cost Intelligence Scorecard")

    col_sc1, col_sc2, col_sc3 = st.columns(3)

    with col_sc1:
        status_class = "status-optimal" if total_project_emission_ton < 10 else ("status-moderate" if total_project_emission_ton < 50 else "status-critical")
        status_label = "STATUS OPTIMAL" if total_project_emission_ton < 10 else ("PERHATIAN" if total_project_emission_ton < 50 else "TINGGI")
        pill_class = "pill-optimal" if total_project_emission_ton < 10 else ("pill-moderate" if total_project_emission_ton < 50 else "pill-critical")
        
        st.markdown(f"""
        <div class="exec-metric-card {status_class}">
            <div>
                <div class="exec-card-head">
                    <div class="exec-card-title-group">
                        <span class="exec-card-icon">🌍</span>
                        <span class="exec-card-title">Total Emisi Karbon Proyek</span>
                    </div>
                    <span class="exec-status-pill {pill_class}">● {status_label}</span>
                </div>
                <div class="exec-card-value">
                    {total_project_emission_ton:,.2f} <span class="exec-card-unit">Ton CO2e</span>
                </div>
            </div>
            <div class="exec-card-subtext">
                Akumulasi emisi material (A1-A3), logistik (A4), dan alat berat (A5).
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_sc2:
        st.markdown(f"""
        <div class="exec-metric-card theme-finance">
            <div>
                <div class="exec-card-head">
                    <div class="exec-card-title-group">
                        <span class="exec-card-icon">💰</span>
                        <span class="exec-card-title">Total Estimasi Biaya</span>
                    </div>
                    <span class="exec-status-pill pill-finance">ANGGARAN</span>
                </div>
                <div class="exec-card-value">
                    Rp {total_mat_cost:,.0f}
                </div>
            </div>
            <div class="exec-card-subtext">
                Estimasi belanja pengadaan {len(results)} jenis material struktur proyek.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_sc3:
        st.markdown(f"""
        <div class="exec-metric-card theme-efficiency">
            <div>
                <div class="exec-card-head">
                    <div class="exec-card-title-group">
                        <span class="exec-card-icon">⚖️</span>
                        <span class="exec-card-title">Rasio Biaya / Emisi</span>
                    </div>
                    <span class="exec-status-pill pill-efficiency">INDEKS EFISIENSI</span>
                </div>
                <div class="exec-card-value">
                    Rp {cost_per_ton:,.0f} <span class="exec-card-unit">/ Ton CO2e</span>
                </div>
            </div>
            <div class="exec-card-subtext">
                Biaya yang dikeluarkan per satu ton emisi karbon yang dihasilkan.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # MODUL CARBON OFFSET
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🌱 Skenario Carbon Offset (Target 10 Tahun)")

    trees_trembesi = math.ceil(total_project_emission_kg / 285) if total_project_emission_kg > 0 else 0
    trees_mahoni = math.ceil(total_project_emission_kg / 140) if total_project_emission_kg > 0 else 0

    col_off1, col_off2 = st.columns(2)

    with col_off1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ecfdf5 0%, #ffffff 100%); border: 1px solid #a7f3d0; border-top: 5px solid #10b981; border-radius: 16px; padding: 20px 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.4rem;">🌳</span>
                    <span style="font-size: 0.85rem; font-weight: 800; color: #064e3b; text-transform: uppercase;">Pohon Trembesi (Samanea saman)</span>
                </div>
                <span style="background: #d1fae5; color: #065f46; font-size: 0.72rem; font-weight: 700; padding: 3px 10px; border-radius: 20px;">SERAPAN TINGGI</span>
            </div>
            <div style="font-size: 2.2rem; font-weight: 800; color: #064e3b; margin: 4px 0;">
                {trees_trembesi:,} <span style="font-size: 1rem; font-weight: 600; color: #047857;">Batang Pohon</span>
            </div>
            <div style="font-size: 0.82rem; color: #047857; margin-top: 10px; border-top: 1px dashed #a7f3d0; padding-top: 10px;">
                Dibutuhkan <b>{trees_trembesi:,} pohon Trembesi</b> untuk menyerap emisi <b>{total_project_emission_ton:,.2f} Ton CO2e</b> dalam 10 tahun.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_off2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%); border: 1px solid #bbf7d0; border-top: 5px solid #059669; border-radius: 16px; padding: 20px 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.4rem;">🌲</span>
                    <span style="font-size: 0.85rem; font-weight: 800; color: #065f46; text-transform: uppercase;">Pohon Mahoni (Swietenia mahagoni)</span>
                </div>
                <span style="background: #dcfce7; color: #166534; font-size: 0.72rem; font-weight: 700; padding: 3px 10px; border-radius: 20px;">STANDAR RTH</span>
            </div>
            <div style="font-size: 2.2rem; font-weight: 800; color: #065f46; margin: 4px 0;">
                {trees_mahoni:,} <span style="font-size: 1rem; font-weight: 600; color: #059669;">Batang Pohon</span>
            </div>
            <div style="font-size: 0.82rem; color: #059669; margin-top: 10px; border-top: 1px dashed #bbf7d0; padding-top: 10px;">
                Dibutuhkan <b>{trees_mahoni:,} pohon Mahoni</b> untuk menyerap emisi <b>{total_project_emission_ton:,.2f} Ton CO2e</b> dalam 10 tahun.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if results:
        df = pd.DataFrame(results)
        tab_a, tab_b = st.tabs(["📊 Visualisasi Grafik & Distribusi Emisi", "📄 Tabel Data Rinci & Ekspor Laporan"])

        with tab_a:
            col_g_top1, col_g_top2 = st.columns(2)
            
            with col_g_top1:
                gauge_max = max(100, math.ceil(total_project_emission_ton * 1.2))
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=total_project_emission_ton,
                    number={'suffix': " Ton CO2e", 'font': {'size': 24, 'family': "Plus Jakarta Sans"}},
                    title={'text': "<b>Status Ambang Batas Emisi Proyek</b>", 'font': {'size': 15, 'family': "Plus Jakarta Sans"}},
                    gauge={
                        'axis': {'range': [0, gauge_max], 'tickwidth': 1, 'tickcolor': "#475569"},
                        'bar': {'color': "#0f172a"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "#e2e8f0",
                        'steps': [
                            {'range': [0, 10], 'color': "#d1fae5"},
                            {'range': [10, 50], 'color': "#fef3c7"},
                            {'range': [50, gauge_max], 'color': "#fee2e2"}
                        ],
                        'threshold': {
                            'line': {'color': "#ef4444", 'width': 4},
                            'thickness': 0.75,
                            'value': total_project_emission_ton
                        }
                    }
                ))
                fig_gauge.update_layout(font_family="Plus Jakarta Sans", margin=dict(t=50, b=20, l=30, r=30), height=300)
                st.plotly_chart(fig_gauge, use_container_width=True)

            with col_g_top2:
                mat_em_ton = total_mat_emission_kg / 1000
                log_em_ton = transport_emission_kg / 1000
                eq_em_ton = equipment_emission_kg / 1000
                
                fig_waterfall = go.Figure(go.Waterfall(
                    name="Akumulasi Emisi",
                    orientation="v",
                    measure=["relative", "relative", "relative", "total"],
                    x=["Material (A1-A3)", "Logistik (A4)", "Alat Berat (A5)", "Total Proyek"],
                    textposition="outside",
                    text=[f"{mat_em_ton:,.2f} Ton", f"{log_em_ton:,.2f} Ton", f"{eq_em_ton:,.2f} Ton", f"{total_project_emission_ton:,.2f} Ton"],
                    y=[mat_em_ton, log_em_ton, eq_em_ton, 0],
                    connector={"line": {"color": "#94a3b8", "width": 2, "dash": "dot"}},
                    decreasing={"marker": {"color": "#10b981"}},
                    increasing={"marker": {"color": "#0284c7"}},
                    totals={"marker": {"color": "#064e3b"}}
                ))
                fig_waterfall.update_layout(title="<b>Akumulasi Emisi Karbon (Waterfall Chart)</b>", font_family="Plus Jakarta Sans", margin=dict(t=50, b=20, l=20, r=20), height=300)
                st.plotly_chart(fig_waterfall, use_container_width=True)

            st.markdown("---")

            col_g1, col_g2 = st.columns(2)
            with col_g1:
                fig_pie = px.pie(df, names="Material", values="Emisi (kg CO2e)", title="Kontribusi Emisi per Jenis Material Struktur", hole=0.45, color_discrete_sequence=px.colors.sequential.Greens_r)
                fig_pie.update_layout(font_family="Plus Jakarta Sans", margin=dict(t=50, b=20, l=20, r=20))
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_g2:
                source_df = pd.DataFrame([
                    {"Sumber": "Material Konstruksi", "Emisi (Ton CO2e)": total_mat_emission_kg / 1000},
                    {"Sumber": "Pengangkutan Logistik (A4)", "Emisi (Ton CO2e)": transport_emission_kg / 1000},
                    {"Sumber": "BBM Alat Berat (A5)", "Emisi (Ton CO2e)": equipment_emission_kg / 1000},
                ])
                fig_bar = px.bar(source_df, x="Sumber", y="Emisi (Ton CO2e)", color="Sumber", title="Komposisi Emisi Karbon Berdasarkan Tahapan Pelaksanaan", color_discrete_map={"Material Konstruksi": "#059669", "Pengangkutan Logistik (A4)": "#0284c7", "BBM Alat Berat (A5)": "#d97706"})
                fig_bar.update_layout(font_family="Plus Jakarta Sans", margin=dict(t=50, b=20, l=20, r=20), showlegend=False)
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
            
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                st.download_button(label="📥 Download Data (CSV)", data=df.to_csv(index=False).encode('utf-8'), file_name="Laporan_Emisi_EcoBuild.csv", mime="text/csv", use_container_width=True)
            with col_d2:
                if HAS_OPENPYXL:
                    excel_bytes = generate_excel_report(df, total_project_emission_ton, total_mat_cost, cost_per_ton, transport_emission_kg, equipment_emission_kg, ice_version)
                    st.download_button(label="📊 Download Laporan Excel (.xlsx)", data=excel_bytes, file_name="Laporan_Resmi_EcoBuild_Pro.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                else:
                    st.button("📊 Download Laporan Excel (.xlsx)", disabled=True, use_container_width=True)
            with col_d3:
                if HAS_REPORTLAB:
                    pdf_bytes = generate_pdf_report(df, total_project_emission_ton, total_mat_cost, cost_per_ton, transport_emission_kg, equipment_emission_kg, ice_version)
                    st.download_button(label="📄 Download Laporan Resmi (PDF)", data=pdf_bytes, file_name="Laporan_Resmi_EcoBuild_Pro.pdf", mime="application/pdf", use_container_width=True)
                else:
                    st.button("📄 Download Laporan Resmi (PDF)", disabled=True, use_container_width=True)
    else:
        st.info("💡 Masukkan jumlah/besaran material pada form di atas untuk menampilkan analisis grafik emisi.")

# ==========================================
# MENU 3: DATABASE MATERIAL ICE (OTOMATIS)
# ==========================================
elif menu == "📊 Database Material ICE (Otomatis)":
    st.title("📊 Master Database Material ICE (Multilingual)")
    
    active_lang = st.session_state["app_lang"]
    st.info(f"""
    **ℹ️ Status Integrasi Database ICE & Mode Bahasa:**  
    * **Versi Database:** `{ice_version}`  
    * **Total Material Terdaftar:** `{len(df_ice_materials)} Jenis Material`  
    * **Mode Bahasa Aktif:** `{active_lang}` *(Dapat diganti kapan saja dari Sidebar)*
    """)

    col_search1, col_search2 = st.columns([1, 2])
    cat_col = "Kategori (ID)" if "Indonesia" in active_lang else ("Kategori (Bilingual)" if "Bilingual" in active_lang else "Kategori (EN)")
    mat_col = "Nama Material (ID)" if "Indonesia" in active_lang else ("Nama Material (Bilingual)" if "Bilingual" in active_lang else "Nama Material (EN)")

    with col_search1:
        cat_options = ["Semua Kategori"] + sorted(list(df_ice_materials[cat_col].unique()))
        cat_select = st.selectbox("🔍 Filter Berdasarkan Kategori:", cat_options)
    with col_search2:
        search_query = st.text_input("🔎 Cari Nama Material Spesifik:", placeholder="Ketik nama material, misal: Beton, Baja, Timber, Aluminium...")

    display_df = df_ice_materials.copy()
    if cat_select != "Semua Kategori":
        display_df = display_df[display_df[cat_col] == cat_select]
    if search_query:
        display_df = display_df[
            display_df["Nama Material (ID)"].str.contains(search_query, case=False, na=False) |
            display_df["Nama Material (EN)"].str.contains(search_query, case=False, na=False)
        ]

    if not display_df.empty:
        c_stat1, c_stat2, c_stat3 = st.columns(3)
        with c_stat1:
            st.metric("Total Material Tampil", f"{len(display_df):,} Jenis")
        with c_stat2:
            avg_fe = display_df["Faktor Emisi (kg CO2e/kg)"].mean()
            st.metric("Rata-rata Faktor Emisi", f"{avg_fe:.4f} kg CO2e/kg")
        with c_stat3:
            min_row = display_df.sort_values(by="Faktor Emisi (kg CO2e/kg)").iloc[0]
            st.metric("Emisi Terendah (Best Eco)", f"{min_row['Faktor Emisi (kg CO2e/kg)']:.4f} kg CO2e/kg")

    st.markdown("<br>", unsafe_allow_html=True)
    
    df_view = display_df[[cat_col, mat_col, "Faktor Emisi (kg CO2e/kg)", "Satuan"]].rename(columns={
        cat_col: "Kategori Material",
        mat_col: "Nama Material Struktur"
    })
    
    st.dataframe(
        df_view,
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
    st.write(f"Mode Bahasa Aktif: **{st.session_state['app_lang']}**. Bandingkan dua opsi desain struktur secara langsung.")

    mat_options = get_active_material_options(df_ice_materials, st.session_state["app_lang"])

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.markdown("""
        <div style="background: #fff1f2; border: 1px solid #fecdd3; border-top: 4px solid #ef4444; border-radius: 12px; padding: 14px 18px; margin-bottom: 12px;">
            <div style="font-weight: 800; color: #9f1239;">🔴 Skenario A (Desain Konvensional / Baseline)</div>
        </div>
        """, unsafe_allow_html=True)
        mat_a = st.selectbox("Pilih Material Skenario A:", mat_options, index=0, key="sa_m")
        vol_a = st.number_input("Jumlah Material A (kg):", min_value=0.0, value=1000.0, step=100.0, key="v_a")
        price_a = st.number_input("Harga Satuan Material A (Rp/kg):", min_value=0.0, value=15000.0, step=1000.0, key="p_comp_a")
        
        row_a = df_ice_materials[
            (df_ice_materials["Nama Material (ID)"] == mat_a) |
            (df_ice_materials["Nama Material (EN)"] == mat_a) |
            (df_ice_materials["Nama Material (Bilingual)"] == mat_a)
        ].iloc[0]
        f_a = float(row_a["Faktor Emisi (kg CO2e/kg)"])
        emisi_a = vol_a * f_a
        cost_a = vol_a * price_a

    with col_s2:
        st.markdown("""
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-top: 4px solid #10b981; border-radius: 12px; padding: 14px 18px; margin-bottom: 12px;">
            <div style="font-weight: 800; color: #065f46;">🟢 Skenario B (Desain Alternatif / Ramah Lingkungan)</div>
        </div>
        """, unsafe_allow_html=True)
        mat_b = st.selectbox("Pilih Material Skenario B:", mat_options, index=min(1, len(mat_options)-1), key="sb_m")
        vol_b = st.number_input("Jumlah Material B (kg):", min_value=0.0, value=1000.0, step=100.0, key="v_b")
        price_b = st.number_input("Harga Satuan Material B (Rp/kg):", min_value=0.0, value=14000.0, step=1000.0, key="p_comp_b")
        
        row_b = df_ice_materials[
            (df_ice_materials["Nama Material (ID)"] == mat_b) |
            (df_ice_materials["Nama Material (EN)"] == mat_b) |
            (df_ice_materials["Nama Material (Bilingual)"] == mat_b)
        ].iloc[0]
        f_b = float(row_b["Faktor Emisi (kg CO2e/kg)"])
        emisi_b = vol_b * f_b
        cost_b = vol_b * price_b

    st.markdown("---")
    st.subheader("📈 Hasil Analisis Komparasi Emisi & Biaya")

    emisi_a_ton = emisi_a / 1000
    emisi_b_ton = emisi_b / 1000
    hemat_emisi_pct = ((emisi_a - emisi_b) / emisi_a * 100) if emisi_a > 0 else 0
    delta_emisi_ton = emisi_a_ton - emisi_b_ton
    delta_cost = cost_b - cost_a
    hemat_biaya_pct = ((cost_a - cost_b) / cost_a * 100) if cost_a > 0 else 0

    col_c1, col_c2, col_c3 = st.columns(3)
    
    with col_c1:
        st.markdown(f"""
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
        Material: <b>{str(mat_a)[:35]}...</b><br>
        FE: <b>{f_a:.6f} kg CO2e/kg</b>
    </div>
</div>
""", unsafe_allow_html=True)
        
    with col_c2:
        st.markdown(f"""
<div class="exec-metric-card status-optimal">
    <div>
        <div class="exec-card-head">
            <div class="exec-card-title-group">
                <span class="exec-card-icon">🟢</span>
                <span class="exec-card-title">Emisi Skenario B</span>
            </div>
            <span class="exec-status-pill pill-optimal">{'REDUKSI ' + f'{hemat_emisi_pct:.1f}%' if hemat_emisi_pct > 0 else '0%'}</span>
        </div>
        <div class="exec-card-value">{emisi_b_ton:,.3f} <span class="exec-card-unit">Ton CO2e</span></div>
    </div>
    <div class="exec-card-subtext">
        Material: <b>{str(mat_b)[:35]}...</b><br>
        <b>Hemat Emisi: {abs(delta_emisi_ton):,.3f} Ton CO2e</b>
    </div>
</div>
""", unsafe_allow_html=True)

    with col_c3:
        cost_diff_str = f"Hemat: Rp {abs(delta_cost):,.0f} ({abs(hemat_biaya_pct):.1f}%)" if delta_cost < 0 else (f"Investasi: +Rp {delta_cost:,.0f}" if delta_cost > 0 else "Biaya Sama")
        st.markdown(f"""
<div class="exec-metric-card theme-finance">
    <div>
        <div class="exec-card-head">
            <div class="exec-card-title-group">
                <span class="exec-card-icon">💼</span>
                <span class="exec-card-title">Komparasi Anggaran</span>
            </div>
            <span class="exec-status-pill pill-finance">BIAYA PROYEK</span>
        </div>
        <div class="exec-card-value">Rp {cost_b:,.0f}</div>
    </div>
    <div class="exec-card-subtext">
        Baseline (A): <b>Rp {cost_a:,.0f}</b><br>
        <b>{cost_diff_str}</b>
    </div>
</div>
""", unsafe_allow_html=True)

    col_ch1, col_ch2 = st.columns(2)
    with col_ch1:
        comp_df = pd.DataFrame([
            {"Skenario": "Skenario A (Baseline)", "Emisi (Ton CO2e)": emisi_a_ton},
            {"Skenario": "Skenario B (Green Design)", "Emisi (Ton CO2e)": emisi_b_ton},
        ])
        fig_comp = px.bar(comp_df, x="Skenario", y="Emisi (Ton CO2e)", color="Skenario", title="Komparasi Total Emisi Karbon (Ton CO2e)", color_discrete_map={"Skenario A (Baseline)": "#ef4444", "Skenario B (Green Design)": "#10b981"})
        fig_comp.update_layout(font_family="Plus Jakarta Sans", margin=dict(t=50, b=20, l=20, r=20), showlegend=False)
        st.plotly_chart(fig_comp, use_container_width=True)

    with col_ch2:
        cost_df = pd.DataFrame([
            {"Skenario": "Skenario A (Baseline)", "Biaya (Rp)": cost_a},
            {"Skenario": "Skenario B (Green Design)", "Biaya (Rp)": cost_b},
        ])
        fig_cost = px.bar(cost_df, x="Skenario", y="Biaya (Rp)", color="Skenario", title="Komparasi Total Biaya Material (Rp)", color_discrete_map={"Skenario A (Baseline)": "#64748b", "Skenario B (Green Design)": "#0284c7"})
        fig_cost.update_layout(font_family="Plus Jakarta Sans", margin=dict(t=50, b=20, l=20, r=20), showlegend=False)
        st.plotly_chart(fig_cost, use_container_width=True)

# ==========================================
# MENU 5: SIKLUS HIDUP EMISI & SOLUSI
# ==========================================
elif menu == "📚 Siklus Hidup Emisi & Solusi":
    st.title("📚 Edukasi: Siklus Hidup Karbon dalam Teknik Sipil")
    st.write("Analisis Komprehensif Penilaian Siklus Hidup (*Life Cycle Assessment / LCA*) pada Struktur Bangunan Gedung.")

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
        fig_lca_donut = px.pie(lca_chart_df, names="Tahapan LCA", values="Proporsi (%)", hole=0.45, title="Estimasi Kontribusi Emisi Karbon (%)", color_discrete_sequence=px.colors.qualitative.Dark24)
        fig_lca_donut.update_layout(font_family="Plus Jakarta Sans", margin=dict(t=50, b=20, l=20, r=20))
        st.plotly_chart(fig_lca_donut, use_container_width=True)

    with col_lca2:
        st.markdown("""
        **Penjelasan Pembagian Siklus Hidup (Standar BS EN 15978):**
        * **A1-A3 (Product Stage):** *Cradle-to-Gate* — Ekstraksi dan pabrikasi material.
        * **A4-A5 (Construction Stage):** Pengiriman logistik material dan bahan bakar alat berat.
        * **B1-B7 (Use Stage):** Penggunaan energi listrik HVAC/penerangan selama puluhan tahun.
        * **C1-C4 (End of Life Stage):** Pembongkaran gedung, pemilahan, dan pembuangan akhir.
        * **Modul D:** Potensi penghematan emisi dari daur ulang (*Recycling / Reuse*).
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
        col_t1a, col_t1b = st.columns(2)
        with col_t1a:
            st.error("""
            **🔥 Sumber Emisi Utama:**
            * Pembakaran batu kapur pada kiln semen dengan suhu $>1400^\\circ\\text{C}$.
            * Penggunaan batu bara koks pada peleburan bijih besi.
            """)
        with col_t1b:
            st.success("""
            **💡 Solusi & Best Practices:**
            * Gunakan *Fly Ash* atau *GGBFS / Slag* 30%-50% pada beton.
            * Manfaatkan baja daur ulang *Electric Arc Furnace* (EAF).
            """)

    with t2:
        st.markdown("### 2. Transport Carbon: Pengangkutan Logistik (Modul A4)")
        col_t2a, col_t2b = st.columns(2)
        with col_t2a:
            st.error("""
            **🔥 Sumber Emisi Utama:**
            * Konsumsi solar armada truk tronton & pengangkutan jarak jauh.
            """)
        with col_t2b:
            st.success("""
            **💡 Solusi & Best Practices:**
            * Prioritaskan produsen material lokal dalam radius $< 100\\text{ km}$.
            """)

    with t3:
        st.markdown("### 3. Construction Carbon: Pelaksanaan di Lapangan (Modul A5)")
        col_t3a, col_t3b = st.columns(2)
        with col_t3a:
            st.error("""
            **🔥 Sumber Emisi Utama:**
            * BBM solar ekskavator, crane, dan genset lokasi proyek.
            """)
        with col_t3b:
            st.success("""
            **💡 Solusi & Best Practices:**
            * Gunakan beton pracetak (precast) dan bekisting aluminium berulang.
            """)

    with t4:
        st.markdown("### 4. Operational Carbon: Pengoperasian Gedung (Modul B1 - B7)")
        col_t4a, col_t4b = st.columns(2)
        with col_t4a:
            st.error("""
            **🔥 Sumber Emisi Utama:**
            * Beban listrik AC/HVAC dan pencahayaan harian gedung.
            """)
        with col_t4b:
            st.success("""
            **💡 Solusi & Best Practices:**
            * Terapkan desain ventilasi pasif dan panel surya (BIPV).
            """)

    with t5:
        st.markdown("### 5. End-of-Life & Beyond: Daur Ulang (Modul C1 - C4 & D)")
        col_t5a, col_t5b = st.columns(2)
        with col_t5a:
            st.error("""
            **🔥 Sumber Emisi Utama:**
            * Penghancuran beton dan pembuangan puing ke tempat pembuangan akhir.
            """)
        with col_t5b:
            st.success("""
            **💡 Solusi & Best Practices:**
            * Terapkan *Design for Deconstruction* (DfD) dan daur ulang puing beton (RCA).
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
