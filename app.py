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
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

# ==========================================
# KONFIGURASI HALAMAN UTAMA
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
    mime = {
        "avif": "image/avif",
        "png": "image/png",
        "webp": "image/webp",
        "svg": "image/svg+xml"
    }.get(ext, "image/jpeg")
    try:
        with open(fname, "rb") as f:
            return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"
    except Exception:
        return None

def get_existing_image(filenames):
    search_dirs = ["", "assets", "images", "img", "static"]
    for d in search_dirs:
        for f in filenames:
            if not f:
                continue
            cand = os.path.join(d, f) if d else f
            if os.path.exists(cand):
                return cand
    return None

bg_url = get_image_base64(get_existing_image([
    "bg_green_building.avif", "bg_green_building.jpg", "bg_green_building.jpeg", "bg_green_building.png"
])) or "https://images.unsplash.com/photo-1541888946425-d0fbb186a5b3?q=80&w=1400"

# ==========================================
# CUSTOM CSS STYLING (ADAPTIVE LIGHT & DARK THEME)
# ==========================================
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 3rem !important;
    max-width: 1380px;
}

/* HERO BANNER (Selalu kontras tinggi di Light & Dark Mode) */
.hero-box {
    background: linear-gradient(135deg, rgba(6, 78, 59, 0.95) 0%, rgba(15, 23, 42, 0.93) 100%), url('{bg_url}');
    background-size: cover;
    background-position: center;
    padding: 46px 38px;
    border-radius: 22px;
    color: #ffffff !important;
    margin-bottom: 26px;
    box-shadow: 0 20px 38px -14px rgba(6, 78, 59, 0.4);
    border: 1px solid rgba(110, 231, 183, 0.25);
}

.hero-badge {
    background: rgba(16, 185, 129, 0.22);
    color: #6ee7b7 !important;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.4px;
    display: inline-block;
    margin-bottom: 14px;
    border: 1px solid rgba(110, 231, 183, 0.4);
}

.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 10px;
    line-height: 1.15;
    color: #ffffff !important;
}

.hero-sub {
    font-size: 1.03rem;
    color: #e2e8f0 !important;
    max-width: 880px;
    line-height: 1.6;
    margin-bottom: 18px;
}

.hero-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 10px;
}

.hero-pill-item {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.22);
    padding: 6px 14px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #f8fafc !important;
}

/* ADAPTIVE CARDS (Otomatis mengikuti tema Light / Dark Streamlit) */
.feature-card {
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(148, 163, 184, 0.28);
    box-shadow: 0 8px 20px -8px rgba(15, 23, 42, 0.12);
    height: 100%;
    transition: transform 0.2s ease;
}

.feature-title {
    font-size: 1rem;
    font-weight: 700;
    color: #10b981;
    margin-bottom: 6px;
}

.feature-desc {
    font-size: 0.85rem;
    color: var(--text-color);
    opacity: 0.88;
    line-height: 1.5;
}

.metric-card {
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(148, 163, 184, 0.28);
    box-shadow: 0 10px 24px -8px rgba(15, 23, 42, 0.12);
}

.m-opt { border-top: 5px solid #10b981; background: linear-gradient(180deg, rgba(16, 185, 129, 0.14) 0%, var(--secondary-background-color) 100%); }
.m-mod { border-top: 5px solid #f59e0b; background: linear-gradient(180deg, rgba(245, 158, 11, 0.14) 0%, var(--secondary-background-color) 100%); }
.m-crit { border-top: 5px solid #ef4444; background: linear-gradient(180deg, rgba(239, 68, 68, 0.14) 0%, var(--secondary-background-color) 100%); }
.m-fin { border-top: 5px solid #2563eb; background: linear-gradient(180deg, rgba(37, 99, 235, 0.14) 0%, var(--secondary-background-color) 100%); }
.m-eff { border-top: 5px solid #7c3aed; background: linear-gradient(180deg, rgba(124, 58, 237, 0.14) 0%, var(--secondary-background-color) 100%); }
.m-int { border-top: 5px solid #0d9488; background: linear-gradient(180deg, rgba(13, 148, 136, 0.14) 0%, var(--secondary-background-color) 100%); }

.m-lbl {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.4px;
    color: var(--text-color);
    opacity: 0.8;
}

.m-val {
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--text-color);
    margin: 6px 0;
}

.m-sub {
    font-size: 0.78rem;
    color: var(--text-color);
    opacity: 0.82;
    border-top: 1px dashed rgba(148, 163, 184, 0.4);
    padding-top: 8px;
    margin-top: 8px;
}

/* SIDEBAR DARK GLASS (Kontras sempurna di Light Mode maupun Dark Mode) */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071318 0%, #0d212b 100%) !important;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stRadio label span {
    color: #f1f5f9 !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.22) !important;
    color: #f8fafc !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] span,
section[data-testid="stSidebar"] div[data-baseweb="select"] div {
    color: #f8fafc !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    fill: #f8fafc !important;
}

section[data-testid="stSidebar"] div[data-testid="stAlert"] {
    background-color: rgba(16, 185, 129, 0.14) !important;
    border: 1px solid rgba(52, 211, 153, 0.35) !important;
    color: #ecfdf5 !important;
}

section[data-testid="stSidebar"] div[data-testid="stAlert"] * {
    color: #ecfdf5 !important;
}

.sb-card {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 18px;
    padding: 18px 14px;
    text-align: center;
    margin-bottom: 16px;
    color: #f8fafc !important;
}

/* KARTU ITEM MATERIAL & SUBTOTAL (Adaptif Light & Dark Mode) */
.mat-bar {
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    border: 1px solid rgba(148, 163, 184, 0.35);
    border-bottom: none;
    border-radius: 12px 12px 0 0;
    padding: 10px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 14px;
}

.mat-bar b {
    color: var(--text-color);
}

.mat-pill {
    background: #059669;
    color: #ffffff !important;
    font-size: 0.74rem;
    font-weight: 700;
    padding: 3px 11px;
    border-radius: 14px;
    margin-right: 6px;
}

.mat-badge-src {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.35);
    font-size: 0.74rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 12px;
}

.sub-pill {
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    border: 1px solid rgba(148, 163, 184, 0.35);
    border-radius: 10px;
    padding: 9px 14px;
    margin-top: 8px;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    font-size: 0.85rem;
}

.sub-pill span, .sub-pill b {
    color: var(--text-color);
}

.eco-box {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.45);
    border-left: 5px solid #10b981;
    border-radius: 10px;
    padding: 10px 14px;
    margin-top: 6px;
    font-size: 0.84rem;
    color: var(--text-color);
    line-height: 1.48;
}

.eco-box code {
    background: rgba(16, 185, 129, 0.22) !important;
    color: var(--text-color) !important;
    padding: 2px 6px;
    border-radius: 5px;
    font-weight: 700;
}

.lca-card {
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    border: 1px solid rgba(148, 163, 184, 0.3);
    border-left: 5px solid #10b981;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}
</style>""", unsafe_allow_html=True)


# ==========================================
# KAMUS & DATABASE ICE MULTILINGUAL (LENGKAP)
# ==========================================
TRANS_CAT = {
    "Concrete": "Beton & Semen",
    "Cement": "Semen & Binder",
    "Steel": "Struktur & Tulangan Baja",
    "Timber": "Kayu & Bekisting",
    "Clay Bricks": "Pasangan Bata Merah",
    "Bricks": "Pasangan Bata & Blok",
    "Aggregates": "Agregat, Pasir & Kerikil",
    "Mortar": "Mortar & Spesi",
    "Glass": "Kaca & Fasad",
    "Aluminium": "Aluminium & Kusen",
    "Insulation": "Insulasi & Peredam",
    "Plastics": "Plastik, Pipa & Geosintetik",
    "Asphalt": "Pekerjaan Aspal & Jalan",
    "Copper": "Tembaga & MEP",
    "Lead": "Timbal",
    "Zinc": "Seng & Pelapis",
    "Plaster": "Plesteran & Gipsum",
    "Stone": "Batu Alam & Granit",
    "Tiles": "Keramik & Penutup Lantai",
    "Bitumen": "Bitumen & Waterproofing",
    "Paint": "Cat & Pelapis",
    "General Construction Material": "Material Konstruksi Umum"
}

TERMS_ID = [
    ("Reinforced Concrete", "Beton Bertulang"),
    ("Precast Concrete", "Beton Pracetak"),
    ("Prestressed Concrete", "Beton Prategang"),
    ("Ready Mix Concrete", "Beton Ready Mix"),
    ("Aerated Concrete", "Beton Ringan Aerasi (AAC)"),
    ("Structural Steel", "Baja Struktur"),
    ("Stainless Steel", "Baja Tahan Karat"),
    ("Galvanised Steel", "Baja Galvanis"),
    ("Galvanized Steel", "Baja Galvanis"),
    ("Steel Rebar", "Baja Tulangan"),
    ("Steel Section", "Profil Baja"),
    ("Steel Sheet", "Pelat Baja"),
    ("Wire Rod", "Baja Kawat"),
    ("Cold Rolled", "Canai Dingin"),
    ("Hot Rolled", "Canai Panas"),
    ("Recycled Steel", "Baja Daur Ulang"),
    ("Steel", "Baja"),
    ("Concrete", "Beton"),
    ("Engineered Timber", "Kayu Rekayasa"),
    ("Glulam", "Kayu Laminasi (Glulam)"),
    ("Cross Laminated Timber", "Kayu Lapis Silang (CLT)"),
    ("Timber", "Kayu"),
    ("Plywood", "Kayu Lapis (Plywood)"),
    ("Chipboard", "Papan Partikel"),
    ("Clay Bricks", "Bata Merah Press"),
    ("Engineering Bricks", "Bata Teknik Kuat Tekan Tinggi"),
    ("Concrete Blocks", "Batako Beton"),
    ("Brick", "Bata"),
    ("Mortar", "Mortar"),
    ("Portland Cement", "Semen Portland (OPC)"),
    ("Cement", "Semen"),
    ("Toughened Glass", "Kaca Tempered"),
    ("Double Glazed", "Kaca Ganda Isolasi"),
    ("Float Glass", "Kaca Polos"),
    ("Glass", "Kaca"),
    ("Extruded Aluminium", "Profil Aluminium Ekstrusi"),
    ("Cast Aluminium", "Aluminium Cor"),
    ("Recycled Aluminium", "Aluminium Daur Ulang"),
    ("Aluminium", "Aluminium"),
    ("Crushed Rock", "Batu Pecah (Split)"),
    ("Aggregate", "Agregat"),
    ("Sand", "Pasir"),
    ("Gravel", "Kerikil"),
    ("Mineral Wool", "Wol Mineral Peredam"),
    ("Expanded Polystyrene", "Polistirena (EPS)"),
    ("Polyurethane", "Poliuretana (PU)"),
    ("Insulation", "Insulasi"),
    ("Asphalt", "Aspal"),
    ("Bitumen", "Bitumen"),
    ("Plasterboard", "Papan Gipsum"),
    ("Gypsum", "Gipsum"),
    ("Plastic", "Plastik"),
    ("Copper", "Tembaga"),
    ("Ceramic Tiles", "Ubin Keramik"),
    ("Granite", "Batu Granit"),
    ("Limestone", "Batu Kapur")
]

def to_id_name(en_name):
    res = str(en_name).strip()
    for en_t, id_t in TERMS_ID:
        if en_t.lower() in res.lower() and id_t.lower() not in res.lower():
            res = re.sub(re.escape(en_t), id_t, res, flags=re.IGNORECASE)
    return res.strip()

def find_green_alternative(df_ice, mat_name, cur_fe, lang_mode):
    if cur_fe <= 0:
        return None
    mcol = (
        "Nama Material (ID)" if "Indonesia" in lang_mode
        else ("Nama Material (Bilingual)" if "Bilingual" in lang_mode else "Nama Material (EN)")
    )
    match = df_ice[
        (df_ice["Nama Material (ID)"] == mat_name) |
        (df_ice["Nama Material (EN)"] == mat_name) |
        (df_ice["Nama Material (Bilingual)"] == mat_name)
    ]
    if not match.empty:
        cat_en = match.iloc[0]["Kategori (EN)"]
        cands = df_ice[
            (df_ice["Kategori (EN)"] == cat_en) &
            (df_ice["Faktor Emisi (kg CO2e/kg)"] < cur_fe * 0.85)
        ].sort_values("Faktor Emisi (kg CO2e/kg)")
        if not cands.empty:
            best = cands.iloc[len(cands) // 2 if len(cands) > 3 else 0]
            alt_fe = float(best["Faktor Emisi (kg CO2e/kg)"])
            return {
                "alt_name": best[mcol],
                "alt_factor": alt_fe,
                "saving_pct": ((cur_fe - alt_fe) / cur_fe) * 100,
                "tech_note": "Substitusi terverifikasi dalam kategori yang sama di ICE Database.",
                "is_ice": True
            }
    low = str(mat_name).lower()
    rules = [
        (
            ("beton", "concrete"), 0.10, 0.65, 35.0,
            "Beton Ramah Lingkungan (Fly Ash 40% / GGBFS)",
            "Low-Carbon Concrete (40% Fly Ash / GGBFS)",
            "Mengganti 35–40% semen OPC dengan Fly Ash / slag menurunkan panas hidrasi & emisi ~35%."
        ),
        (
            ("baja", "steel", "rebar", "wf", "hollow"), 1.20, 0.45, 55.0,
            "Baja Daur Ulang EAF (Recycled Steel)",
            "Recycled Steel (Electric Arc Furnace)",
            "Produksi baja jalur Electric Arc Furnace (EAF) menekan emisi hingga >50% dibanding Blast Furnace."
        ),
        (
            ("bata", "brick", "batako"), 0.18, 0.60, 40.0,
            "Bata Ringan AAC / Blok Geopolimer Rendah Karbon",
            "Autoclaved Aerated Concrete (AAC) / Low-Carbon Block",
            "Mengurangi beban mati struktur sekaligus memangkas emisi pembakaran tanah liat."
        ),
        (
            ("aluminium",), 4.00, 0.30, 70.0,
            "Aluminium Daur Ulang (Recycled Aluminium)",
            "Recycled Aluminium Profile",
            "Daur ulang aluminium hanya membutuhkan ~5% energi peleburan bijih bauksit primer."
        ),
        (
            ("semen", "cement"), 0.50, 0.62, 38.0,
            "Semen Komposit Pozzolan / PCC (SNI 7064)",
            "Portland Composite Cement (PCC)",
            "Rasio klinker lebih rendah sesuai SNI 7064 dengan kuat tekan akhir setara."
        ),
        (
            ("aspal", "asphalt", "hotmix"), 0.05, 0.72, 28.0,
            "Warm Mix Asphalt (WMA) + 25% Reclaimed Asphalt (RAP)",
            "Warm Mix Asphalt (WMA) + 25% RAP",
            "Suhu pencampuran 30°C lebih rendah menghemat BBM burner AMP dan memanfaatkan aspal daur ulang."
        ),
        (
            ("kaca", "glass"), 1.15, 0.78, 22.0,
            "Kaca Low-E Daur Ulang (Recycled Cullet Glass)",
            "Low-E Recycled Cullet Glass",
            "Menurunkan konsumsi energi peleburan sekaligus meningkatkan efisiensi termal fasad."
        )
    ]
    for keys, thresh, mult, pct, lbl_id, lbl_en, note in rules:
        if any(k in low for k in keys) and cur_fe > thresh:
            return {
                "alt_name": lbl_id if "Indonesia" in lang_mode else lbl_en,
                "alt_factor": round(cur_fe * mult, 4),
                "saving_pct": pct,
                "tech_note": note,
                "is_ice": False
            }
    return None

def smart_read_rab(fobj, fname):
    df_raw = pd.read_csv(fobj, header=None) if fname.endswith(".csv") else pd.read_excel(fobj, header=None)
    h_idx = None
    for idx, row in df_raw.iterrows():
        s = " ".join(str(v).lower() for v in row.values if pd.notna(v))
        if any(k in s for k in ["material", "nama", "bahan", "uraian"]) and any(k in s for k in ["jumlah", "volume", "qty"]):
            h_idx = idx
            break
    fobj.seek(0)
    if h_idx is not None:
        return pd.read_csv(fobj, header=h_idx) if fname.endswith(".csv") else pd.read_excel(fobj, header=h_idx)
    return pd.read_csv(fobj) if fname.endswith(".csv") else pd.read_excel(fobj)

def get_col_map(cols):
    cmap = {}
    for c in [str(x).strip() for x in cols]:
        cl = c.lower()
        if "Material" not in cmap and any(k in cl for k in ["material", "nama", "bahan", "uraian"]):
            cmap["Material"] = c
        elif "Jumlah" not in cmap and "total" not in cl and any(k in cl for k in ["jumlah", "volume", "qty"]):
            cmap["Jumlah"] = c
        elif "Satuan" not in cmap and ("satuan" in cl or "unit" in cl) and "harga" not in cl:
            cmap["Satuan"] = c
        elif "Faktor Emisi" not in cmap and "total" not in cl and any(k in cl for k in ["faktor", "fe", "emisi", "co2"]):
            cmap["Faktor Emisi"] = c
        elif "Harga Satuan" not in cmap and "total" not in cl and ("harga" in cl or "price" in cl or "hsp" in cl):
            cmap["Harga Satuan"] = c
    return cmap

@st.cache_data
def load_ice_db():
    xfile = get_existing_image([
        os.path.join("ICE-Educational-V5.0-d2jkasdljwq2k", "ICE DB Educational V5.0 - Jun 2026.xlsx"),
        "ICE DB Educational V5.0 - Jun 2026.xlsx",
        "ICE DB Educational V5.0.xlsx",
        "ICE_Database.xlsx"
    ])
    ver = "Educational (V5.0) - Jun 2026"
    df_out = None
    if xfile and os.path.exists(xfile):
        try:
            xl = pd.ExcelFile(xfile)
            df_raw = xl.parse("ICE Summary" if "ICE Summary" in xl.sheet_names else xl.sheet_names[0])
            mats, cur_cat = [], "General Construction Material"
            for idx in range(16, len(df_raw)):
                row = df_raw.iloc[idx]
                vals = [x for x in row.values if pd.notna(x)]
                if not vals:
                    continue
                fval = str(vals[0]).strip()
                if len(vals) == 1 and not fval.startswith(("http", "Module", "Note")):
                    cur_cat = fval
                    continue
                fname = str(row.iloc[19]).strip() if len(row) > 19 and pd.notna(row.iloc[19]) else (
                    str(row.iloc[5]).strip() if len(row) > 5 and pd.notna(row.iloc[5]) else None
                )
                cval = float(row.iloc[6]) if len(row) > 6 and isinstance(row.iloc[6], (int, float)) and pd.notna(row.iloc[6]) else next(
                    (float(v) for v in vals if isinstance(v, (int, float)) and 0.0001 <= v <= 100.0), None
                )
                if fname and cval is not None and not fname.startswith(("Name Exactly", "Materials", "Introduction")):
                    mats.append({
                        "Kategori": cur_cat,
                        "Nama Material": fname,
                        "Faktor Emisi (kg CO2e/kg)": round(cval, 6),
                        "Satuan": "kg"
                    })
            if mats:
                df_out = pd.DataFrame(mats).drop_duplicates(subset=["Nama Material"])
        except Exception:
            df_out = None

    if df_out is None or df_out.empty:
        df_out = pd.DataFrame([
            {"Kategori": "Concrete", "Nama Material": "Concrete Ready Mix K-225 (Conventional)", "Faktor Emisi (kg CO2e/kg)": 0.118, "Satuan": "kg"},
            {"Kategori": "Concrete", "Nama Material": "Concrete Ready Mix K-300 (Conventional)", "Faktor Emisi (kg CO2e/kg)": 0.134, "Satuan": "kg"},
            {"Kategori": "Concrete", "Nama Material": "Concrete Ready Mix K-350 (Conventional)", "Faktor Emisi (kg CO2e/kg)": 0.155, "Satuan": "kg"},
            {"Kategori": "Concrete", "Nama Material": "Concrete Ready Mix K-450 (High Strength)", "Faktor Emisi (kg CO2e/kg)": 0.182, "Satuan": "kg"},
            {"Kategori": "Concrete", "Nama Material": "Concrete 30% Fly Ash Replacement", "Faktor Emisi (kg CO2e/kg)": 0.096, "Satuan": "kg"},
            {"Kategori": "Concrete", "Nama Material": "Concrete 40% Fly Ash Replacement", "Faktor Emisi (kg CO2e/kg)": 0.085, "Satuan": "kg"},
            {"Kategori": "Concrete", "Nama Material": "Concrete 50% GGBFS Slag Replacement", "Faktor Emisi (kg CO2e/kg)": 0.072, "Satuan": "kg"},
            {"Kategori": "Concrete", "Nama Material": "Precast Concrete Panel / Girder", "Faktor Emisi (kg CO2e/kg)": 0.168, "Satuan": "kg"},
            {"Kategori": "Cement", "Nama Material": "Portland Cement CEM I (OPC)", "Faktor Emisi (kg CO2e/kg)": 0.912, "Satuan": "kg"},
            {"Kategori": "Cement", "Nama Material": "Portland Composite Cement (PCC)", "Faktor Emisi (kg CO2e/kg)": 0.640, "Satuan": "kg"},
            {"Kategori": "Steel", "Nama Material": "Steel Rebar (Virgin BOF Route)", "Faktor Emisi (kg CO2e/kg)": 1.990, "Satuan": "kg"},
            {"Kategori": "Steel", "Nama Material": "Structural Steel WF / H-Beam Section", "Faktor Emisi (kg CO2e/kg)": 1.820, "Satuan": "kg"},
            {"Kategori": "Steel", "Nama Material": "Galvanised Steel Sheet / Decking", "Faktor Emisi (kg CO2e/kg)": 2.410, "Satuan": "kg"},
            {"Kategori": "Steel", "Nama Material": "Stainless Steel 304", "Faktor Emisi (kg CO2e/kg)": 4.400, "Satuan": "kg"},
            {"Kategori": "Steel", "Nama Material": "Recycled Steel Rebar (EAF 100% Scrap)", "Faktor Emisi (kg CO2e/kg)": 0.760, "Satuan": "kg"},
            {"Kategori": "Steel", "Nama Material": "Recycled Steel Section (EAF)", "Faktor Emisi (kg CO2e/kg)": 0.890, "Satuan": "kg"},
            {"Kategori": "Timber", "Nama Material": "Sawn Softwood Timber (Bekisting)", "Faktor Emisi (kg CO2e/kg)": 0.263, "Satuan": "kg"},
            {"Kategori": "Timber", "Nama Material": "Sawn Hardwood Timber (Struktural)", "Faktor Emisi (kg CO2e/kg)": 0.310, "Satuan": "kg"},
            {"Kategori": "Timber", "Nama Material": "Engineered Timber / Glulam", "Faktor Emisi (kg CO2e/kg)": 0.300, "Satuan": "kg"},
            {"Kategori": "Timber", "Nama Material": "Plywood / Formwork Board", "Faktor Emisi (kg CO2e/kg)": 0.681, "Satuan": "kg"},
            {"Kategori": "Clay Bricks", "Nama Material": "Clay Bricks (Pressed Conventional)", "Faktor Emisi (kg CO2e/kg)": 0.240, "Satuan": "kg"},
            {"Kategori": "Bricks", "Nama Material": "Aerated Concrete Block (Hebel AAC)", "Faktor Emisi (kg CO2e/kg)": 0.145, "Satuan": "kg"},
            {"Kategori": "Bricks", "Nama Material": "Concrete Masonry Block (Batako)", "Faktor Emisi (kg CO2e/kg)": 0.112, "Satuan": "kg"},
            {"Kategori": "Mortar", "Nama Material": "Cement Mortar 1:4", "Faktor Emisi (kg CO2e/kg)": 0.208, "Satuan": "kg"},
            {"Kategori": "Aggregates", "Nama Material": "Crushed Rock Aggregate (Batu Split)", "Faktor Emisi (kg CO2e/kg)": 0.0052, "Satuan": "kg"},
            {"Kategori": "Aggregates", "Nama Material": "Natural River Sand (Pasir Pasang)", "Faktor Emisi (kg CO2e/kg)": 0.0048, "Satuan": "kg"},
            {"Kategori": "Aggregates", "Nama Material": "Recycled Concrete Aggregate (RCA)", "Faktor Emisi (kg CO2e/kg)": 0.0029, "Satuan": "kg"},
            {"Kategori": "Glass", "Nama Material": "Float Glass (Clear Architectural)", "Faktor Emisi (kg CO2e/kg)": 1.440, "Satuan": "kg"},
            {"Kategori": "Glass", "Nama Material": "Toughened Tempered Glass", "Faktor Emisi (kg CO2e/kg)": 1.670, "Satuan": "kg"},
            {"Kategori": "Glass", "Nama Material": "Double Glazed Low-E Unit", "Faktor Emisi (kg CO2e/kg)": 1.320, "Satuan": "kg"},
            {"Kategori": "Aluminium", "Nama Material": "Aluminium Extruded Profile (Virgin)", "Faktor Emisi (kg CO2e/kg)": 8.240, "Satuan": "kg"},
            {"Kategori": "Aluminium", "Nama Material": "Recycled Aluminium Extruded Profile", "Faktor Emisi (kg CO2e/kg)": 2.150, "Satuan": "kg"},
            {"Kategori": "Asphalt", "Nama Material": "Hot Mix Asphalt (AC-WC / AC-BC)", "Faktor Emisi (kg CO2e/kg)": 0.075, "Satuan": "kg"},
            {"Kategori": "Asphalt", "Nama Material": "Warm Mix Asphalt (WMA + 25% RAP)", "Faktor Emisi (kg CO2e/kg)": 0.052, "Satuan": "kg"},
            {"Kategori": "Plastics", "Nama Material": "PVC Pipe (Pipa Air Bersih/Limbah)", "Faktor Emisi (kg CO2e/kg)": 3.100, "Satuan": "kg"},
            {"Kategori": "Plastics", "Nama Material": "HDPE Pipe / Geomembrane", "Faktor Emisi (kg CO2e/kg)": 2.520, "Satuan": "kg"},
            {"Kategori": "Insulation", "Nama Material": "Mineral Wool / Rockwool Insulation", "Faktor Emisi (kg CO2e/kg)": 1.280, "Satuan": "kg"},
            {"Kategori": "Plaster", "Nama Material": "Gypsum Plasterboard", "Faktor Emisi (kg CO2e/kg)": 0.390, "Satuan": "kg"},
            {"Kategori": "Tiles", "Nama Material": "Ceramic Tiles (Lantai & Dinding)", "Faktor Emisi (kg CO2e/kg)": 0.780, "Satuan": "kg"}
        ])

    df_out["Kategori (EN)"] = df_out["Kategori"]
    df_out["Kategori (ID)"] = df_out["Kategori (EN)"].map(lambda x: TRANS_CAT.get(x, x))
    df_out["Kategori (Bilingual)"] = df_out.apply(
        lambda r: f"{r['Kategori (ID)']} ({r['Kategori (EN)']})" if r["Kategori (ID)"].lower() != r["Kategori (EN)"].lower() else r["Kategori (EN)"],
        axis=1
    )
    df_out["Nama Material (EN)"] = df_out["Nama Material"]
    df_out["Nama Material (ID)"] = df_out["Nama Material (EN)"].apply(to_id_name)
    df_out["Nama Material (Bilingual)"] = df_out.apply(
        lambda r: f"{r['Nama Material (ID)']} ({r['Nama Material (EN)']})" if r["Nama Material (ID)"].lower() != r["Nama Material (EN)"].lower() else r["Nama Material (EN)"],
        axis=1
    )
    return ver, df_out

ice_version, df_ice_materials = load_ice_db()

# ==========================================
# INISIALISASI SESSION STATE
# ==========================================
defaults = {
    "calc_num_items": 3,
    "dist_km": 25.0,
    "fuel_liter": 100.0,
    "app_lang": "🇮🇩 Bahasa Indonesia",
    "nav_menu": "🏠 Beranda",
    "proj_name": "Proyek Pembangunan Gedung Hijau",
    "proj_loc": "Indonesia",
    "proj_eng": "Tim Teknik Sipil",
    "proj_area": 500.0
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def get_mat_opts(df_ice, lang):
    if lang == "🇬🇧 English":
        return df_ice["Nama Material (EN)"].tolist()
    if "Bilingual" in lang:
        return df_ice["Nama Material (Bilingual)"].tolist()
    return df_ice["Nama Material (ID)"].tolist()

# ==========================================
# GENERATOR LAPORAN PDF & EXCEL MULTI-SHEET
# ==========================================
def make_pdf(df_res, tot_ton, tot_cost, c_ton, tr_kg, eq_kg, ver, meta):
    if not HAS_REPORTLAB:
        return b""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#064e3b'), spaceAfter=6)
    sub_style = ParagraphStyle('CustomSub', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#475569'), spaceAfter=12)

    story = [
        Paragraph("<b>EcoBuild Pro v2.1 - Laporan Audit Emisi Karbon & Biaya Proyek</b>", title_style),
        Paragraph(
            f"Proyek: <b>{meta['name']}</b> | Lokasi: {meta['loc']} | Estimator: {meta['eng']}<br/>"
            f"Referensi Database: ICE {ver} | Tanggal Cetak: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
            sub_style
        ),
        Spacer(1, 6)
    ]

    intensity = (tot_ton * 1000.0 / meta['area']) if meta['area'] > 0 else 0.0
    t1 = Table([
        ["Indikator Kinerja (KPI)", "Hasil Perhitungan"],
        ["Total Emisi Karbon Proyek (A1 - A5)", f"{tot_ton:,.3f} Ton CO2e ({tot_ton*1000:,.1f} kg CO2e)"],
        ["Total Estimasi Biaya Pengadaan Material", f"Rp {tot_cost:,.0f}"],
        ["Intensitas Karbon per Luas Lantai", f"{intensity:,.2f} kg CO2e / m2 (Luas: {meta['area']:,.0f} m2)"],
        ["Rasio Biaya terhadap Emisi Karbon", f"Rp {c_ton:,.0f} / Ton CO2e"],
        ["Emisi Logistik Pengangkutan (Modul A4)", f"{tr_kg/1000:,.3f} Ton CO2e ({tr_kg:,.1f} kg CO2e)"],
        ["Emisi BBM Alat Berat Lapangan (Modul A5)", f"{eq_kg/1000:,.3f} Ton CO2e ({eq_kg:,.1f} kg CO2e)"]
    ], colWidths=[240, 290])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#064e3b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 6)
    ]))
    story.extend([t1, Spacer(1, 16)])

    if not df_res.empty:
        story.append(Paragraph("<b>Rincian Material, Faktor Emisi & Biaya (Modul A1 - A3)</b>", styles['Heading3']))
        story.append(Spacer(1, 6))
        tdata = [["No", "Nama Material", "Volume", "Sat", "FE", "Emisi (kg)", "Biaya (Rp)"]] + [
            [
                str(idx + 1),
                str(r['Material'])[:36],
                f"{r['Jumlah']:,.1f}",
                str(r['Satuan']),
                f"{r['Faktor Emisi']:,.4f}",
                f"{r['Emisi (kg CO2e)']:,.1f}",
                f"Rp {r['Biaya (Rp)']:,.0f}"
            ]
            for idx, r in df_res.iterrows()
        ]
        t2 = Table(tdata, colWidths=[24, 175, 55, 32, 48, 86, 110])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#047857')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0, 0), (-1, -1), 5)
        ]))
        story.append(t2)

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "<i>Catatan Akademik: Perhitungan mengacu pada standar BS EN 15978 & Inventory of Carbon and Energy (ICE). "
        "Dosen Pengampu: Dr. Ir. Dedy Firmansyah, S.Pd., M.T. • EcoBuild Pro CV Kingsman IDN.</i>",
        sub_style
    ))
    doc.build(story)
    return buf.getvalue()

def make_excel(df_res, tot_ton, tot_cost, c_ton, tr_kg, eq_kg, ver, meta):
    if not HAS_OPENPYXL:
        return b""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ringkasan & Rincian RAB"

    hdr_fill = PatternFill("solid", fgColor="064E3B")
    sub_fill = PatternFill("solid", fgColor="ECFDF5")
    zebra_fill = PatternFill("solid", fgColor="F8FAFC")
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    ws['A1'] = "ECOBUILD PRO v2.1 - LAPORAN ANALISIS EMISI KARBON & BIAYA KONSTRUKSI"
    ws['A1'].font = Font(size=14, bold=True, color="064E3B")
    ws['A2'] = f"Proyek: {meta['name']} | Lokasi: {meta['loc']} | Estimator: {meta['eng']} | DB: ICE {ver}"
    ws['A2'].font = Font(size=10, italic=True, color="475569")

    intensity = (tot_ton * 1000.0 / meta['area']) if meta['area'] > 0 else 0.0
    kpis = [
        ("Total Emisi Proyek (Ton CO2e)", tot_ton, "0.000"),
        ("Total Estimasi Biaya Material (Rp)", tot_cost, "#,##0"),
        ("Intensitas Karbon Bangunan (kg CO2e/m2)", intensity, "0.00"),
        ("Rasio Biaya per Emisi (Rp / Ton CO2e)", c_ton, "#,##0"),
        ("Emisi Logistik Pengangkutan A4 (Ton CO2e)", tr_kg / 1000.0, "0.000"),
        ("Emisi BBM Alat Berat A5 (Ton CO2e)", eq_kg / 1000.0, "0.000")
    ]
    for idx, (label, val, num_fmt) in enumerate(kpis, start=4):
        c1 = ws.cell(idx, 1, label)
        c2 = ws.cell(idx, 2, float(val))
        c1.font = Font(bold=True, color="0F172A")
        c1.fill = sub_fill
        c2.number_format = num_fmt
        c1.border = thin_border
        c2.border = thin_border

    headers = ["No", "Nama Material", "Volume", "Satuan", "Faktor Emisi (kg CO2e/unit)", "Total Emisi (kg CO2e)", "Harga Satuan (Rp)", "Total Biaya (Rp)"]
    start_row = 12
    for col_idx, h in enumerate(headers, start=1):
        cell = ws.cell(start_row, col_idx, h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = hdr_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    for idx, r in df_res.iterrows():
        rr = start_row + 1 + idx
        vals = [
            idx + 1,
            str(r['Material']),
            float(r['Jumlah']),
            str(r['Satuan']),
            float(r['Faktor Emisi']),
            float(r['Emisi (kg CO2e)']),
            float(r['Harga Satuan']),
            float(r['Biaya (Rp)'])
        ]
        for c_idx, v in enumerate(vals, start=1):
            cell = ws.cell(rr, c_idx, v)
            if idx % 2 == 1:
                cell.fill = zebra_fill
            cell.border = thin_border
            if c_idx in (3, 6):
                cell.number_format = "#,##0.00"
            elif c_idx == 5:
                cell.number_format = "0.0000"
            elif c_idx in (7, 8):
                cell.number_format = "#,##0"

    for col in ws.columns:
        max_len = max((len(str(cell.value or "")) for cell in col), default=10)
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_len + 5, 48)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ==========================================
# SIDEBAR NAVIGASI & IDENTITAS AKADEMIK
# ==========================================
def go_page(p):
    st.session_state["nav_menu"] = p

logo_b64 = get_image_base64(get_existing_image(["logo_kingsman.png", "logo_kingsman.jpg", "logo.png", "logo.jpg"]))
with st.sidebar:
    l_html = (
        f'<img src="{logo_b64}" style="max-width:125px;margin:0 auto 10px;display:block;border-radius:10px;" />'
        if logo_b64 else '<div style="font-size:2.3rem;margin-bottom:4px;">🏗️</div>'
    )
    st.markdown(
        f'<div class="sb-card">{l_html}'
        f'<div style="font-size:1.35rem;font-weight:800;letter-spacing:-0.3px;">EcoBuild Pro</div>'
        f'<div style="font-size:0.76rem;color:#34d399;font-weight:700;">● v2.1 Smart Eco-Swap Edition</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.selectbox(
        "🌐 Bahasa Database Material:",
        ["🇮🇩 Bahasa Indonesia", "🇬🇧 English", "🇮🇩🇬🇧 Dwi-Bahasa (Bilingual)"],
        key="app_lang"
    )

    menu = st.radio(
        "🧭 Navigasi Modul:",
        [
            "🏠 Beranda",
            "🧮 Kalkulator & Analisis Proyek",
            "📊 Database Material ICE (Otomatis)",
            "⚖️ Simulasi Komparasi Desain",
            "📚 Siklus Hidup Emisi & Solusi"
        ],
        key="nav_menu"
    )

    st.markdown("---")
    st.info(
        f"⚡ **ICE DB:** {len(df_ice_materials):,} Material Aktif\n\n"
        f"📘 **Standar:** BS EN 15978 (A1–D)\n\n"
        f"🎓 **Dosen Pengampu:**\nDr. Ir. Dedy Firmansyah, S.Pd., M.T."
    )

# ==========================================
# MENU 1: BERANDA (EXECUTIVE LANDING PAGE)
# ==========================================
if menu == "🏠 Beranda":
    st.markdown(f"""
    <div class="hero-box">
        <div class="hero-badge">🌿 Green Building & Civil Engineering Carbon Intelligence</div>
        <div class="hero-title">EcoBuild Pro Simulator v2.1</div>
        <div class="hero-sub">
            Platform rekayasa sipil terpadu untuk menghitung jejak emisi karbon (Embodied & Construction Carbon A1–A5),
            mengoptimalkan Rencana Anggaran Biaya (RAB), serta merekomendasikan substitusi material hijau secara otomatis dalam 1 klik.
        </div>
        <div class="hero-pills">
            <div class="hero-pill-item">📦 {len(df_ice_materials):,}+ Material ICE V5.0</div>
            <div class="hero-pill-item">⚡ 1-Klik Smart Eco-Swap</div>
            <div class="hero-pill-item">📐 Standar BS EN 15978 & Greenship</div>
            <div class="hero-pill-item">📊 Ekspor Audit PDF & Excel</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">📦 Integrasi ICE V5.0</div>
            <div class="feature-desc">Pembacaan otomatis faktor emisi (kg CO2e/kg) dari Inventory of Carbon & Energy dengan dukungan 3 mode bahasa.</div>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">⚡ Smart Eco-Swap AI</div>
            <div class="feature-desc">Mendeteksi material beremisi tinggi (beton OPC, baja virgin, aluminium) dan menyarankan substitusi rendah karbon 1-klik.</div>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">💰 Carbon-Cost Matrix</div>
            <div class="feature-desc">Menghitung intensitas karbon per m², biaya per Ton CO2e, dan kebutuhan pohon kompensasi (Carbon Offset) secara real-time.</div>
        </div>
        """, unsafe_allow_html=True)
    with f4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">📥 Impor RAB & Ekspor Audit</div>
            <div class="feature-desc">Unggah file RAB Excel/CSV yang sudah ada, simpan sesi proyek JSON, dan unduh laporan resmi siap sidang/tender.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.15, 0.85])
    with c1:
        st.subheader("🌐 Urgensi Dekarbonisasi Sektor Konstruksi")
        st.write(
            "Industri konstruksi dan bangunan menyumbang **~37–40% emisi karbon global**, dengan porsi signifikan berasal dari "
            "**Embodied Carbon** pada produksi semen/beton, peleburan baja, dan transportasi material berat ke lokasi proyek."
        )
        st.write(
            "Melalui **EcoBuild Pro**, perencana struktur dan quantity surveyor dapat langsung mengevaluasi konsekuensi karbon dari "
            "setiap pilihan spesifikasi teknis sebelum tahap pelaksanaan dimulai."
        )
        ig = get_existing_image(["gas_emisi.jpg", "gas_emisi.jpeg"])
        if ig:
            st.image(ig, caption="Ilustrasi Emisi Industri & Konstruksi Global", use_container_width=True)
    with c2:
        st.warning(
            "🔥 **Refleksi Urgensi Iklim:** Peningkatan suhu global dan bencana ekologis (seperti Karhutla dan cuaca ekstrem) "
            "menuntut insinyur sipil beralih dari desain konvensional menuju konstruksi rendah karbon (*Net-Zero Ready Construction*)."
        )
        ik = get_existing_image(["karhutla.jpg", "karhutla.jfif"])
        if ik:
            st.image(ik, caption="Dampak Krisis Iklim & Pentingnya Mitigasi Emisi Karbon", use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🚀 Mulai Analisis Sekarang")
    b1, b2, b3, b4 = st.columns(4)
    b1.button("🧮 Buka Kalkulator & Eco-Swap ➔", use_container_width=True, on_click=go_page, args=("🧮 Kalkulator & Analisis Proyek",))
    b2.button("📊 Jelajahi Database ICE ➔", use_container_width=True, on_click=go_page, args=("📊 Database Material ICE (Otomatis)",))
    b3.button("⚖️ Simulasi Komparasi A vs B ➔", use_container_width=True, on_click=go_page, args=("⚖️ Simulasi Komparasi Desain",))
    b4.button("📚 Panduan LCA (A1–D) ➔", use_container_width=True, on_click=go_page, args=("📚 Siklus Hidup Emisi & Solusi",))

# ==========================================
# MENU 2: KALKULATOR & ANALISIS PROYEK
# ==========================================
elif menu == "🧮 Kalkulator & Analisis Proyek":
    st.title("🧮 Kalkulator Emisi Karbon & Biaya Proyek")

    with st.expander("🏗️ Identitas Proyek & Parameter Luas Bangunan (Untuk Intensitas kg CO2e/m²)", expanded=False):
        ip1, ip2, ip3, ip4 = st.columns([1.4, 1, 1, 0.9])
        st.session_state["proj_name"] = ip1.text_input("Nama Proyek:", value=st.session_state["proj_name"])
        st.session_state["proj_loc"] = ip2.text_input("Lokasi Proyek:", value=st.session_state["proj_loc"])
        st.session_state["proj_eng"] = ip3.text_input("Nama Estimator / Engineer:", value=st.session_state["proj_eng"])
        st.session_state["proj_area"] = ip4.number_input("Luas Lantai (m²):", min_value=1.0, value=float(st.session_state["proj_area"]), step=25.0)

    with st.expander("📥 Impor File RAB (.xlsx / .csv) & Simpan/Muat Sesi Proyek (.json)", expanded=False):
        tab_imp1, tab_imp2 = st.tabs(["📊 Impor RAB Excel / CSV", "💾 Backup & Muat Sesi JSON"])
        with tab_imp1:
            sample_rab = pd.DataFrame([
                {"Material": "Beton Ready Mix K-300", "Jumlah": 50000, "Satuan": "kg", "Faktor Emisi": 0.134, "Harga Satuan": 1250},
                {"Material": "Baja Tulangan Ulir", "Jumlah": 6500, "Satuan": "kg", "Faktor Emisi": 1.990, "Harga Satuan": 14800},
                {"Material": "Bata Ringan Hebel AAC", "Jumlah": 12000, "Satuan": "kg", "Faktor Emisi": 0.145, "Harga Satuan": 1100}
            ])
            st.download_button(
                "📄 Unduh Contoh Template RAB (.csv)",
                sample_rab.to_csv(index=False).encode("utf-8"),
                "Template_RAB_EcoBuild.csv",
                "text/csv"
            )
            up = st.file_uploader("Unggah file RAB Excel atau CSV:", type=["xlsx", "csv"], key="rab_up")
            if up is not None:
                fid = f"{up.name}_{up.size}"
                if st.session_state.get("last_rab_id") != fid:
                    try:
                        df_rab = smart_read_rab(up, up.name)
                        cmap = get_col_map(df_rab.columns)
                        if "Material" in cmap and "Jumlah" in cmap:
                            nr = min(30, len(df_rab))
                            st.session_state["calc_num_items"] = nr
                            st.session_state["input_num_items"] = nr
                            lookup = {
                                str(r[c]).strip().lower(): float(r["Faktor Emisi (kg CO2e/kg)"])
                                for _, r in df_ice_materials.iterrows()
                                for c in ["Nama Material (EN)", "Nama Material (ID)", "Nama Material (Bilingual)"]
                            }
                            for idx, row in df_rab.iloc[:nr].iterrows():
                                mv = str(row[cmap["Material"]]).strip()
                                qv = float(pd.to_numeric(row[cmap["Jumlah"]], errors='coerce') or 0)
                                sv = str(row[cmap["Satuan"]]).strip() if "Satuan" in cmap and pd.notna(row[cmap["Satuan"]]) else "kg"
                                fv = (
                                    float(pd.to_numeric(row[cmap["Faktor Emisi"]], errors='coerce') or 1.0)
                                    if "Faktor Emisi" in cmap and pd.notna(row[cmap["Faktor Emisi"]])
                                    else lookup.get(mv.lower(), 1.0)
                                )
                                pv = (
                                    float(pd.to_numeric(row[cmap["Harga Satuan"]], errors='coerce') or 10000.0)
                                    if "Harga Satuan" in cmap and pd.notna(row[cmap["Harga Satuan"]])
                                    else 12000.0
                                )
                                st.session_state[f"calc_sel_{idx}"] = "➕ Material Kustom (Isi Sendiri)"
                                st.session_state[f"c_name_{idx}"] = mv
                                st.session_state[f"c_unit_{idx}"] = sv
                                st.session_state[f"c_fact_{idx}"] = fv
                                st.session_state[f"c_price_{idx}"] = pv
                                st.session_state[f"c_qty_{idx}"] = qv
                            st.session_state["last_rab_id"] = fid
                            st.success(f"✅ Berhasil memuat {nr} item material dari file RAB!")
                            st.rerun()
                        else:
                            st.error("Kolom 'Material' dan 'Jumlah/Volume' tidak terdeteksi di dalam file.")
                    except Exception as e:
                        st.error(f"Gagal memproses file RAB: {e}")

        with tab_imp2:
            cur_n = int(st.session_state.get("calc_num_items", 3))
            state_dump = {
                "proj_name": st.session_state["proj_name"],
                "proj_loc": st.session_state["proj_loc"],
                "proj_eng": st.session_state["proj_eng"],
                "proj_area": st.session_state["proj_area"],
                "dist_km": st.session_state["dist_km"],
                "fuel_liter": st.session_state["fuel_liter"],
                "num_items": cur_n,
                "items": []
            }
            for idx in range(cur_n):
                state_dump["items"].append({
                    "sel": st.session_state.get(f"calc_sel_{idx}", "➕ Material Kustom (Isi Sendiri)"),
                    "c_name": st.session_state.get(f"c_name_{idx}", f"Material {idx+1}"),
                    "c_unit": st.session_state.get(f"c_unit_{idx}", "kg"),
                    "c_fact": st.session_state.get(f"c_fact_{idx}", 1.0),
                    "c_price": st.session_state.get(f"c_price_{idx}", 10000.0),
                    "c_qty": st.session_state.get(f"c_qty_{idx}", 0.0),
                    "p_val": st.session_state.get(f"p_val_{idx}", 15000.0),
                    "q_val": st.session_state.get(f"q_val_{idx}", 0.0)
                })
            st.download_button(
                "💾 Unduh File Sesi Proyek (.json)",
                json.dumps(state_dump, indent=2).encode("utf-8"),
                "Sesi_EcoBuild_Pro.json",
                "application/json"
            )
            up_json = st.file_uploader("Muat Kembali File Sesi (.json):", type=["json"], key="json_up")
            if up_json is not None:
                jid = f"{up_json.name}_{up_json.size}"
                if st.session_state.get("last_json_id") != jid:
                    try:
                        loaded = json.load(up_json)
                        st.session_state["proj_name"] = loaded.get("proj_name", st.session_state["proj_name"])
                        st.session_state["proj_loc"] = loaded.get("proj_loc", st.session_state["proj_loc"])
                        st.session_state["proj_eng"] = loaded.get("proj_eng", st.session_state["proj_eng"])
                        st.session_state["proj_area"] = float(loaded.get("proj_area", 500.0))
                        st.session_state["dist_km"] = float(loaded.get("dist_km", 25.0))
                        st.session_state["calc_dist_km"] = st.session_state["dist_km"]
                        st.session_state["fuel_liter"] = float(loaded.get("fuel_liter", 100.0))
                        st.session_state["calc_fuel_liter"] = st.session_state["fuel_liter"]
                        items_j = loaded.get("items", [])
                        if items_j:
                            st.session_state["calc_num_items"] = len(items_j)
                            st.session_state["input_num_items"] = len(items_j)
                            for idx, it in enumerate(items_j):
                                st.session_state[f"calc_sel_{idx}"] = it.get("sel", "➕ Material Kustom (Isi Sendiri)")
                                st.session_state[f"c_name_{idx}"] = it.get("c_name", f"Material {idx+1}")
                                st.session_state[f"c_unit_{idx}"] = it.get("c_unit", "kg")
                                st.session_state[f"c_fact_{idx}"] = float(it.get("c_fact", 1.0))
                                st.session_state[f"c_price_{idx}"] = float(it.get("c_price", 10000.0))
                                st.session_state[f"c_qty_{idx}"] = float(it.get("c_qty", 0.0))
                                st.session_state[f"p_val_{idx}"] = float(it.get("p_val", 15000.0))
                                st.session_state[f"q_val_{idx}"] = float(it.get("q_val", 0.0))
                        st.session_state["last_json_id"] = jid
                        st.success("✅ Sesi proyek berhasil dipulihkan!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"File JSON tidak valid: {e}")

    def apply_tpl(tpl):
        presets = {
            "rumah": (
                "Rumah Tinggal 2 Lantai (Tipe 120)", 120.0,
                [
                    ("Beton Ready Mix K-250 (Konvensional)", "kg", 0.130, 1150.0, 36000.0),
                    ("Baja Tulangan Polos & Ulir", "kg", 1.990, 14500.0, 4800.0),
                    ("Bata Merah Konvensional", "kg", 0.240, 950.0, 15000.0),
                    ("Kayu Bekisting Meranti", "kg", 0.310, 3200.0, 2100.0)
                ], 15.0, 85.0
            ),
            "gedung": (
                "Gedung Kantor 5 Lantai (Struktur Komposit)", 2400.0,
                [
                    ("Beton Ready Mix K-350 (Konvensional)", "kg", 0.155, 1350.0, 220000.0),
                    ("Baja Tulangan Ulir BJTS 420B", "kg", 1.990, 14800.0, 34000.0),
                    ("Profil Baja Struktur WF", "kg", 1.820, 17500.0, 19500.0),
                    ("Kaca Fasad Tempered", "kg", 1.670, 22000.0, 5200.0),
                    ("Profil Aluminium Kusen", "kg", 8.240, 48000.0, 2600.0)
                ], 45.0, 540.0
            ),
            "jalan": (
                "Pekerjaan Perkerasan Jalan Aspal Hotmix 1 km", 7000.0,
                [
                    ("Aspal Hotmix AC-WC & AC-BC", "kg", 0.075, 1650.0, 260000.0),
                    ("Agregat Kelas A (Base Course)", "kg", 0.0052, 320.0, 450000.0),
                    ("Beton Pracetak Kanstin K-300", "kg", 0.168, 1400.0, 38000.0)
                ], 30.0, 680.0
            ),
            "jembatan": (
                "Jembatan Gelagar Beton Prategang (Bentang 30 m)", 360.0,
                [
                    ("Beton Mutu Tinggi K-450 (Girder & Pier)", "kg", 0.182, 1650.0, 145000.0),
                    ("Baja Tulangan & Strand Prategang", "kg", 1.990, 16200.0, 26000.0),
                    ("Baja Diafragma & Sandaran Galvanis", "kg", 2.410, 19500.0, 6800.0)
                ], 60.0, 420.0
            )
        }
        pname, parea, items, km, fuel = presets[tpl]
        st.session_state["proj_name"] = pname
        st.session_state["proj_area"] = parea
        st.session_state["input_num_items"] = len(items)
        st.session_state["calc_num_items"] = len(items)
        st.session_state["dist_km"] = km
        st.session_state["calc_dist_km"] = km
        st.session_state["fuel_liter"] = fuel
        st.session_state["calc_fuel_liter"] = fuel
        for idx, (mn, mu, mf, mp, mq) in enumerate(items):
            st.session_state[f"calc_sel_{idx}"] = "➕ Material Kustom (Isi Sendiri)"
            st.session_state[f"c_name_{idx}"] = mn
            st.session_state[f"c_unit_{idx}"] = mu
            st.session_state[f"c_fact_{idx}"] = mf
            st.session_state[f"c_price_{idx}"] = mp
            st.session_state[f"c_qty_{idx}"] = mq

    st.markdown("#### 📑 Template Proyek Cepat (1-Klik Muat RAB Standar)")
    t1, t2, t3, t4 = st.columns(4)
    t1.button("🏠 Rumah Tinggal 2 Lantai", use_container_width=True, on_click=apply_tpl, args=("rumah",))
    t2.button("🏢 Gedung Kantor 5 Lantai", use_container_width=True, on_click=apply_tpl, args=("gedung",))
    t3.button("🛣️ Jalan Aspal 1 km", use_container_width=True, on_click=apply_tpl, args=("jalan",))
    t4.button("🌉 Jembatan Girder 30 m", use_container_width=True, on_click=apply_tpl, args=("jembatan",))
    st.markdown("---")

    if "input_num_items" not in st.session_state:
        st.session_state["input_num_items"] = int(st.session_state.get("calc_num_items", 3))

    def mod_rows(delta):
        nxt = min(30, max(1, int(st.session_state.get("input_num_items", 3)) + delta))
        st.session_state["input_num_items"] = nxt
        st.session_state["calc_num_items"] = nxt

    def apply_swap(idx, alt, u_str, p_val, q_val):
        if alt["is_ice"]:
            st.session_state[f"calc_sel_{idx}"] = alt["alt_name"]
            st.session_state[f"p_val_{idx}"] = float(p_val)
            st.session_state[f"q_val_{idx}"] = float(q_val)
        else:
            st.session_state[f"calc_sel_{idx}"] = "➕ Material Kustom (Isi Sendiri)"
            st.session_state[f"c_name_{idx}"] = alt["alt_name"]
            st.session_state[f"c_unit_{idx}"] = u_str
            st.session_state[f"c_fact_{idx}"] = float(alt["alt_factor"])
            st.session_state[f"c_price_{idx}"] = float(p_val)
            st.session_state[f"c_qty_{idx}"] = float(q_val)

    c_n1, c_n2, c_n3 = st.columns([2, 1, 1])
    with c_n1:
        num_items = st.number_input("🔢 Jumlah Jenis Material dalam RAB:", min_value=1, max_value=30, step=1, key="input_num_items")
        st.session_state["calc_num_items"] = num_items
    with c_n2:
        st.write("")
        st.write("")
        st.button("➕ Tambah Baris Material", use_container_width=True, on_click=mod_rows, args=(1,))
    with c_n3:
        st.write("")
        st.write("")
        st.button("➖ Kurangi Baris Material", use_container_width=True, on_click=mod_rows, args=(-1,))

    all_opts = ["➕ Material Kustom (Isi Sendiri)"] + get_mat_opts(df_ice_materials, st.session_state["app_lang"])
    results, tot_mat_kg, tot_mat_rp = [], 0.0, 0.0
    green_swaps_available = []
    potential_green_kg = 0.0

    for i in range(num_items):
        def_i = (i + 1) if (i + 1) < len(all_opts) else 0
        cur_s = st.session_state.get(f"calc_sel_{i}", all_opts[def_i])
        is_cust = (cur_s == "➕ Material Kustom (Isi Sendiri)")
        header_lbl = st.session_state.get(f"c_name_{i}", "Material Kustom") if is_cust else str(cur_s)[:60]
        st.markdown(
            f'<div class="mat-bar">'
            f'<div><span class="mat-pill">ITEM #{i+1}</span> <b>{header_lbl}</b></div>'
            f'<span class="mat-badge-src">{"🛠️ INPUT KUSTOM" if is_cust else "📦 DATABASE ICE"}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        sel_m = st.selectbox(
            f"Pilih Material #{i+1}:",
            options=all_opts,
            index=all_opts.index(cur_s) if cur_s in all_opts else def_i,
            key=f"calc_sel_{i}"
        )
        if sel_m != "➕ Material Kustom (Isi Sendiri)":
            m_row = df_ice_materials[
                (df_ice_materials["Nama Material (ID)"] == sel_m) |
                (df_ice_materials["Nama Material (EN)"] == sel_m) |
                (df_ice_materials["Nama Material (Bilingual)"] == sel_m)
            ]
            info = m_row.iloc[0] if not m_row.empty else {"Satuan": "kg", "Faktor Emisi (kg CO2e/kg)": 0.134}
            mat_name, u_str, f_val = sel_m, info["Satuan"], float(info["Faktor Emisi (kg CO2e/kg)"])
            cm1, cm2, cm3 = st.columns([1.2, 1, 1])
            cm1.info(f"**FE ICE:** `{f_val:.6f}` kg CO2e/{u_str}")
            p_val = cm2.number_input(f"Harga Satuan (Rp/{u_str}) #{i+1}:", min_value=0.0, value=float(st.session_state.get(f"p_val_{i}", 15000.0)), step=1000.0, key=f"p_val_{i}")
            q_val = cm3.number_input(f"Volume Kebutuhan ({u_str}) #{i+1}:", min_value=0.0, value=float(st.session_state.get(f"q_val_{i}", 0.0)), step=50.0, key=f"q_val_{i}")
        else:
            cc1, cc2 = st.columns([2.6, 1])
            mat_name = cc1.text_input(f"Nama Material #{i+1}:", value=st.session_state.get(f"c_name_{i}", f"Material Kustom {i+1}"), key=f"c_name_{i}")
            u_str = cc2.text_input(f"Satuan #{i+1}:", value=st.session_state.get(f"c_unit_{i}", "kg"), key=f"c_unit_{i}")
            cc3, cc4, cc5 = st.columns(3)
            f_val = cc3.number_input(f"Faktor Emisi (kg CO2e/{u_str}):", min_value=0.0, value=float(st.session_state.get(f"c_fact_{i}", 1.0)), step=0.05, format="%.4f", key=f"c_fact_{i}")
            p_val = cc4.number_input(f"Harga Satuan (Rp/{u_str}):", min_value=0.0, value=float(st.session_state.get(f"c_price_{i}", 10000.0)), step=1000.0, key=f"c_price_{i}")
            q_val = cc5.number_input(f"Volume Kebutuhan ({u_str}):", min_value=0.0, value=float(st.session_state.get(f"c_qty_{i}", 0.0)), step=10.0, key=f"c_qty_{i}")

        e_kg, c_rp = q_val * f_val, q_val * p_val
        eco = find_green_alternative(df_ice_materials, mat_name, f_val, st.session_state["app_lang"])
        has_valid_eco = bool(eco and eco["alt_name"].lower() != mat_name.lower())

        if q_val > 0:
            results.append({
                "Material": mat_name,
                "Jumlah": q_val,
                "Satuan": u_str,
                "Faktor Emisi": f_val,
                "Emisi (kg CO2e)": e_kg,
                "Harga Satuan": p_val,
                "Biaya (Rp)": c_rp
            })
            tot_mat_kg += e_kg
            tot_mat_rp += c_rp
            if has_valid_eco:
                potential_green_kg += q_val * float(eco["alt_factor"])
            else:
                potential_green_kg += e_kg

        st.markdown(
            f'<div class="sub-pill">'
            f'<span>🌿 <b>Subtotal Emisi (A1–A3):</b> {e_kg:,.2f} kg CO2e ({e_kg/1000:,.3f} Ton)</span>'
            f'<span>💰 <b>Subtotal Biaya RAB:</b> Rp {c_rp:,.0f}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        if has_valid_eco:
            green_swaps_available.append((i, eco, u_str, p_val, q_val))
            ce1, ce2 = st.columns([3.3, 1.1])
            ce1.markdown(
                f'<div class="eco-box">💡 <b>Rekomendasi Hijau:</b> Substitusi ke <b>{eco["alt_name"]}</b> '
                f'(FE: <code>{eco["alt_factor"]:.4f}</code>) → pangkas emisi <b>{eco["saving_pct"]:.0f}%</b>! '
                f'<br><span style="font-size:0.77rem;opacity:0.86;">ℹ️ {eco["tech_note"]}</span></div>',
                unsafe_allow_html=True
            )
            ce2.write("")
            ce2.button("⚡ Ganti ke Hijau", key=f"swap_{i}", use_container_width=True, on_click=apply_swap, args=(i, eco, u_str, p_val, q_val))

    if green_swaps_available:
        def apply_all_swaps():
            for idx, alt_obj, u_s, p_v, q_v in green_swaps_available:
                apply_swap(idx, alt_obj, u_s, p_v, q_v)
        st.markdown("<br>", unsafe_allow_html=True)
        st.button(
            f"🌿 Terapkan Semua ({len(green_swaps_available)}) Rekomendasi Material Hijau Sekaligus",
            use_container_width=True,
            on_click=apply_all_swaps
        )

    st.markdown("---")
    st.subheader("🚚 Logistik Pengangkutan & BBM Alat Berat (Modul A4 - A5)")
    def set_km(v):
        st.session_state["dist_km"] = v
        st.session_state["calc_dist_km"] = v
    z1, z2, z3 = st.columns(3)
    z1.button("🟢 Zona Lokal Quarry/Batching Plant (15 km)", use_container_width=True, on_click=set_km, args=(15.0,))
    z2.button("🟡 Zona Regional Antar Kota (75 km)", use_container_width=True, on_click=set_km, args=(75.0,))
    z3.button("🔴 Zona Logistik Antar Pulau (400 km)", use_container_width=True, on_click=set_km, args=(400.0,))

    ct1, ct2, ct3 = st.columns([1.2, 1.2, 1])
    st.session_state["dist_km"] = ct1.number_input("Jarak Pengangkutan Rata-rata (km):", min_value=0.0, value=float(st.session_state["dist_km"]), step=5.0, key="calc_dist_km")
    st.session_state["fuel_liter"] = ct2.number_input("Konsumsi BBM Alat Berat (Liter):", min_value=0.0, value=float(st.session_state["fuel_liter"]), step=50.0, key="calc_fuel_liter")
    fuel_type = ct3.selectbox("Jenis Bahan Bakar (A5):", ["Solar Industri / B35 (2.68 kg/L)", "Biodiesel B40 (2.41 kg/L)", "Alat Berat Listrik / PLN (0.85 kg/kWh)"])
    fuel_factor = 2.68 if "B35" in fuel_type else (2.41 if "B40" in fuel_type else 0.85)

    tr_kg = st.session_state["dist_km"] * 2.5
    eq_kg = st.session_state["fuel_liter"] * fuel_factor
    tot_kg = tot_mat_kg + tr_kg + eq_kg
    tot_ton = tot_kg / 1000.0
    c_per_ton = (tot_mat_rp / tot_ton) if tot_ton > 0 else 0.0
    carbon_intensity = (tot_kg / st.session_state["proj_area"]) if st.session_state["proj_area"] > 0 else 0.0

    st.markdown("---")
    st.subheader("📊 Executive Carbon & Cost Scorecard")
    s1, s2, s3, s4 = st.columns(4)
    cls = "m-opt" if tot_ton < 15 else ("m-mod" if tot_ton < 60 else "m-crit")
    status_lbl = "RENDAH KARBON" if tot_ton < 15 else ("MODERAT" if tot_ton < 60 else "TINGGI KARBON")
    s1.markdown(
        f'<div class="metric-card {cls}">'
        f'<div class="m-lbl">🌍 TOTAL EMISI PROYEK ({status_lbl})</div>'
        f'<div class="m-val">{tot_ton:,.2f} Ton</div>'
        f'<div class="m-sub">{tot_kg:,.0f} kg CO2e (Modul A1–A5)</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    s2.markdown(
        f'<div class="metric-card m-fin">'
        f'<div class="m-lbl">💰 TOTAL ESTIMASI BIAYA RAB</div>'
        f'<div class="m-val">Rp {tot_mat_rp:,.0f}</div>'
        f'<div class="m-sub">Pengadaan {len(results)} jenis material</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    s3.markdown(
        f'<div class="metric-card m-int">'
        f'<div class="m-lbl">📐 INTENSITAS KARBON / M²</div>'
        f'<div class="m-val">{carbon_intensity:,.1f} kg/m²</div>'
        f'<div class="m-sub">Luas lantai: {st.session_state["proj_area"]:,.0f} m²</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    s4.markdown(
        f'<div class="metric-card m-eff">'
        f'<div class="m-lbl">⚖️ RASIO BIAYA / EMISI</div>'
        f'<div class="m-val">Rp {c_per_ton:,.0f}</div>'
        f'<div class="m-sub">Biaya konstruksi per Ton CO2e</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    o1, o2, o3 = st.columns(3)
    o1.success(f"🌳 **Carbon Offset Trembesi (10 Thn):**\n**{math.ceil(tot_kg/285) if tot_kg>0 else 0:,} Batang Pohon**")
    o2.success(f"🌲 **Carbon Offset Mahoni (10 Thn):**\n**{math.ceil(tot_kg/140) if tot_kg>0 else 0:,} Batang Pohon**")
    o3.info(f"🚗 **Setara Emisi Kendaraan Bensin:**\n**{tot_kg/0.192 if tot_kg>0 else 0:,.0f} km** jarak tempuh mobil")

    if results:
        df = pd.DataFrame(results)
        ta, tb, tc = st.tabs(["📊 Grafik Analisis Emisi & Biaya", "🌿 Simulasi Potensi Eco-Swap", "📄 Tabel Rincian & Ekspor Audit"])
        with ta:
            cg1, cg2 = st.columns(2)
            fig_pie = px.pie(df, names="Material", values="Emisi (kg CO2e)", title="Kontribusi Emisi Karbon per Material (A1–A3)", hole=0.45)
            cg1.plotly_chart(fig_pie, use_container_width=True)
            src_df = pd.DataFrame([
                {"Tahap": "Produksi Material (A1–A3)", "Ton CO2e": tot_mat_kg / 1000.0},
                {"Tahap": "Logistik Transport (A4)", "Ton CO2e": tr_kg / 1000.0},
                {"Tahap": "Alat Berat Lapangan (A5)", "Ton CO2e": eq_kg / 1000.0}
            ])
            cg2.plotly_chart(px.bar(src_df, x="Tahap", y="Ton CO2e", color="Tahap", title="Distribusi Emisi per Tahapan Konstruksi (Ton CO2e)"), use_container_width=True)

            fig_sc = px.scatter(
                df, x="Biaya (Rp)", y="Emisi (kg CO2e)", size="Jumlah", color="Material",
                title="Matriks Hotspot: Biaya Pengadaan (Rp) vs Emisi Karbon (kg CO2e)"
            )
            st.plotly_chart(fig_sc, use_container_width=True)

        with tb:
            pot_tot_kg = potential_green_kg + tr_kg + eq_kg
            saved_kg = max(0.0, tot_kg - pot_tot_kg)
            saved_pct = (saved_kg / tot_kg * 100.0) if tot_kg > 0 else 0.0
            gs1, gs2, gs3 = st.columns(3)
            gs1.metric("Emisi Desain Saat Ini", f"{tot_ton:,.2f} Ton CO2e")
            gs2.metric("Potensi Setelah Eco-Swap", f"{pot_tot_kg/1000:,.2f} Ton CO2e", f"-{saved_pct:.1f}%")
            gs3.metric("Total Karbon Tereduksi", f"{saved_kg/1000:,.2f} Ton CO2e")
            comp_eco_df = pd.DataFrame([
                {"Kondisi": "RAB Saat Ini (Baseline)", "Emisi (Ton CO2e)": tot_ton},
                {"Kondisi": "RAB Teroptimasi Eco-Swap", "Emisi (Ton CO2e)": pot_tot_kg / 1000.0}
            ])
            st.plotly_chart(
                px.bar(comp_eco_df, x="Kondisi", y="Emisi (Ton CO2e)", color="Kondisi", title="Proyeksi Penurunan Emisi Jika Seluruh Rekomendasi Hijau Diterapkan"),
                use_container_width=True
            )

        with tc:
            st.dataframe(df, use_container_width=True, hide_index=True)
            meta_dict = {
                "name": st.session_state["proj_name"],
                "loc": st.session_state["proj_loc"],
                "eng": st.session_state["proj_eng"],
                "area": float(st.session_state["proj_area"])
            }
            d1, d2, d3 = st.columns(3)
            d1.download_button(
                "📥 Download Data CSV",
                df.to_csv(index=False).encode('utf-8'),
                "Laporan_EcoBuild_Pro.csv",
                "text/csv",
                use_container_width=True
            )
            if HAS_OPENPYXL:
                d2.download_button(
                    "📊 Download Excel Terformat (.xlsx)",
                    make_excel(df, tot_ton, tot_mat_rp, c_per_ton, tr_kg, eq_kg, ice_version, meta_dict),
                    "Laporan_EcoBuild_Pro.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            if HAS_REPORTLAB:
                d3.download_button(
                    "📄 Download Laporan Resmi (.pdf)",
                    make_pdf(df, tot_ton, tot_mat_rp, c_per_ton, tr_kg, eq_kg, ice_version, meta_dict),
                    "Laporan_EcoBuild_Pro.pdf",
                    "application/pdf",
                    use_container_width=True
                )
    else:
        st.info("💡 Pilih salah satu **Template Proyek Cepat** di atas atau masukkan volume material untuk menampilkan grafik analisis dan ekspor laporan.")


# ==========================================
# MENU 3: DATABASE MATERIAL ICE (OTOMATIS)
# ==========================================
elif menu == "📊 Database Material ICE (Otomatis)":
    st.title("📊 Master Database Material ICE (Inventory of Carbon & Energy)")
    lang = st.session_state["app_lang"]
    ccol = "Kategori (ID)" if "Indonesia" in lang else ("Kategori (Bilingual)" if "Bilingual" in lang else "Kategori (EN)")
    mcol = "Nama Material (ID)" if "Indonesia" in lang else ("Nama Material (Bilingual)" if "Bilingual" in lang else "Nama Material (EN)")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Material ICE", f"{len(df_ice_materials):,} Item")
    k2.metric("Jumlah Kategori", f"{df_ice_materials[ccol].nunique()} Kategori")
    k3.metric("Rata-rata Faktor Emisi", f"{df_ice_materials['Faktor Emisi (kg CO2e/kg)'].mean():.3f} kg/kg")
    k4.metric("Versi Referensi", ice_version.split("-")[0].strip())

    f1, f2, f3 = st.columns([1.2, 1.8, 1])
    csel = f1.selectbox("Filter Kategori Konstruksi:", ["Semua Kategori"] + sorted(df_ice_materials[ccol].unique().tolist()))
    q = f2.text_input("Cari Nama Material (ID / EN):", placeholder="Contoh: Beton, Concrete, Baja, Steel, Aluminium, Timber...")
    max_fe_val = float(df_ice_materials["Faktor Emisi (kg CO2e/kg)"].max())
    fe_limit = f3.slider("Batas Maksimal FE (kg CO2e/kg):", min_value=0.01, max_value=max(10.0, round(max_fe_val + 0.5, 1)), value=max(10.0, round(max_fe_val + 0.5, 1)))

    vdf = df_ice_materials[df_ice_materials["Faktor Emisi (kg CO2e/kg)"] <= fe_limit].copy()
    if csel != "Semua Kategori":
        vdf = vdf[vdf[ccol] == csel]
    if q:
        vdf = vdf[
            vdf["Nama Material (ID)"].str.contains(q, case=False, na=False) |
            vdf["Nama Material (EN)"].str.contains(q, case=False, na=False)
        ]

    st.caption(f"Menampilkan **{len(vdf):,}** dari **{len(df_ice_materials):,}** material konstruksi.")
    st.dataframe(
        vdf[[ccol, mcol, "Faktor Emisi (kg CO2e/kg)", "Satuan"]].sort_values("Faktor Emisi (kg CO2e/kg)", ascending=True),
        use_container_width=True,
        hide_index=True
    )

    if not vdf.empty:
        top_df = vdf.sort_values("Faktor Emisi (kg CO2e/kg)", ascending=False).head(12)
        fig_db = px.bar(
            top_df,
            x="Faktor Emisi (kg CO2e/kg)",
            y=mcol,
            orientation="h",
            color="Faktor Emisi (kg CO2e/kg)",
            color_continuous_scale="Tealgrn",
            title=f"Top {len(top_df)} Material dengan Faktor Emisi Tertinggi pada Filter Aktif"
        )
        fig_db.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_db, use_container_width=True)

        st.download_button(
            "📥 Unduh Database ICE Terfilter (.csv)",
            vdf[[ccol, mcol, "Faktor Emisi (kg CO2e/kg)", "Satuan"]].to_csv(index=False).encode("utf-8"),
            "Database_Material_ICE_Filtered.csv",
            "text/csv"
        )

# ==========================================
# MENU 4: SIMULASI KOMPARASI DESAIN
# ==========================================
elif menu == "⚖️ Simulasi Komparasi Desain":
    st.title("⚖️ Simulasi Komparasi Desain: Skenario A vs Skenario B")
    st.write("Bandingkan performa emisi karbon dan kelayakan biaya antara desain konvensional (Baseline) dan alternatif desain hijau.")

    opts = get_mat_opts(df_ice_materials, st.session_state["app_lang"])
    c1, c2 = st.columns(2)
    with c1:
        st.error("🔴 **Skenario A — Desain Konvensional (Baseline)**")
        ma = st.selectbox("Pilih Material Skenario A:", opts, index=0, key="sa_m")
        va = st.number_input("Volume Material A (kg):", min_value=0.0, value=10000.0, step=500.0, key="sa_v")
        pa = st.number_input("Harga Satuan A (Rp/kg):", min_value=0.0, value=14500.0, step=500.0, key="sa_p")
        da = st.number_input("Jarak Logistik A (km):", min_value=0.0, value=60.0, step=10.0, key="sa_d")
        fa = float(df_ice_materials[
            (df_ice_materials["Nama Material (ID)"] == ma) |
            (df_ice_materials["Nama Material (EN)"] == ma) |
            (df_ice_materials["Nama Material (Bilingual)"] == ma)
        ].iloc[0]["Faktor Emisi (kg CO2e/kg)"])
        st.caption(f"Faktor Emisi A: `{fa:.4f}` kg CO2e/kg")

    with c2:
        st.success("🟢 **Skenario B — Desain Alternatif Hijau (Green Option)**")
        mb = st.selectbox("Pilih Material Skenario B:", opts, index=min(1, len(opts) - 1), key="sb_m")
        vb = st.number_input("Volume Material B (kg):", min_value=0.0, value=10000.0, step=500.0, key="sb_v")
        pb = st.number_input("Harga Satuan B (Rp/kg):", min_value=0.0, value=15200.0, step=500.0, key="sb_p")
        db = st.number_input("Jarak Logistik B (km):", min_value=0.0, value=20.0, step=10.0, key="sb_d")
        fb = float(df_ice_materials[
            (df_ice_materials["Nama Material (ID)"] == mb) |
            (df_ice_materials["Nama Material (EN)"] == mb) |
            (df_ice_materials["Nama Material (Bilingual)"] == mb)
        ].iloc[0]["Faktor Emisi (kg CO2e/kg)"])
        st.caption(f"Faktor Emisi B: `{fb:.4f}` kg CO2e/kg")

    ea_tot = ((va * fa) + (da * 2.5)) / 1000.0
    eb_tot = ((vb * fb) + (db * 2.5)) / 1000.0
    ca_tot = va * pa
    cb_tot = vb * pb
    diff_e = ea_tot - eb_tot
    diff_c = cb_tot - ca_tot
    pct_e = (diff_e / ea_tot * 100.0) if ea_tot > 0 else 0.0
    abatement_cost = (diff_c / diff_e) if diff_e > 0 else 0.0

    st.markdown("---")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Emisi Skenario A", f"{ea_tot:,.3f} Ton CO2e")
    k2.metric("Total Emisi Skenario B", f"{eb_tot:,.3f} Ton CO2e", f"{-pct_e:.1f}% vs A")
    k3.metric("Selisih Biaya (B - A)", f"Rp {diff_c:,.0f}")
    k4.metric("Carbon Abatement Cost", f"Rp {abatement_cost:,.0f} / Ton")

    if diff_e > 0 and diff_c <= 0:
        st.success(f"🏆 **Win-Win Solution:** Skenario B memangkas emisi sebesar **{diff_e:,.3f} Ton CO2e ({pct_e:.1f}%)** SEKALIGUS menghemat biaya **Rp {abs(diff_c):,.0f}**!")
    elif diff_e > 0:
        st.info(f"✅ **Layak Teknis-Lingkungan:** Skenario B menurunkan emisi sebesar **{diff_e:,.3f} Ton CO2e ({pct_e:.1f}%)** dengan biaya marjinal **Rp {abatement_cost:,.0f} per Ton CO2e**.")
    else:
        st.warning("⚠️ Skenario B saat ini memiliki emisi lebih tinggi atau sama dengan Skenario A. Pilih material dengan Faktor Emisi lebih rendah.")

    g1, g2 = st.columns(2)
    g1.plotly_chart(
        px.bar(
            pd.DataFrame([{"Skenario": "Skenario A (Baseline)", "Emisi (Ton CO2e)": ea_tot}, {"Skenario": "Skenario B (Hijau)", "Emisi (Ton CO2e)": eb_tot}]),
            x="Skenario", y="Emisi (Ton CO2e)", color="Skenario", title="Perbandingan Total Emisi Karbon (Ton CO2e)"
        ),
        use_container_width=True
    )
    g2.plotly_chart(
        px.bar(
            pd.DataFrame([{"Skenario": "Skenario A (Baseline)", "Biaya (Rp)": ca_tot}, {"Skenario": "Skenario B (Hijau)", "Biaya (Rp)": cb_tot}]),
            x="Skenario", y="Biaya (Rp)", color="Skenario", title="Perbandingan Biaya Pengadaan Material (Rp)"
        ),
        use_container_width=True
    )

# ==========================================
# MENU 5: SIKLUS HIDUP EMISI & SOLUSI (LCA)
# ==========================================
elif menu == "📚 Siklus Hidup Emisi & Solusi":
    st.title("📚 Siklus Hidup Karbon Bangunan (Standar BS EN 15978)")
    st.write("Kerangka penilaian daur hidup bangunan (*Whole-Life Carbon Assessment*) membagi emisi konstruksi ke dalam 4 modul utama dari ekstraksi bahan baku hingga daur ulang.")

    c1, c2 = st.columns([1.05, 0.95])
    with c1:
        lca_df = pd.DataFrame([
            {"Modul LCA": "A1–A3: Tahap Produk & Manufaktur Material", "Kontribusi (%)": 28},
            {"Modul LCA": "A4: Transportasi Material ke Proyek", "Kontribusi (%)": 4},
            {"Modul LCA": "A5: Proses Konstruksi & Alat Berat", "Kontribusi (%)": 5},
            {"Modul LCA": "B1–B7: Tahap Operasional Gedung (50 Tahun)", "Kontribusi (%)": 60},
            {"Modul LCA": "C1–C4: Pembongkaran & Akhir Masa Layan", "Kontribusi (%)": 3}
        ])
        st.plotly_chart(
            px.pie(lca_df, names="Modul LCA", values="Kontribusi (%)", hole=0.45, title="Proporsi Siklus Hidup Karbon Bangunan Tipikal (50 Tahun)"),
            use_container_width=True
        )

    with c2:
        st.markdown("""
        <div class="lca-card">
            <b>🏭 Modul A1–A3 (Product Stage — Embodied Carbon Utama)</b><br/>
            Ekstraksi bahan mentah, transportasi ke pabrik, dan proses manufaktur (kalsinasi klinker semen, peleburan baja).
            <i>Solusi: Gunakan beton Fly Ash/GGBFS & baja daur ulang EAF.</i>
        </div>
        <div class="lca-card">
            <b>🚚 Modul A4–A5 (Construction Process Stage)</b><br/>
            Pengangkutan material dari pabrik/quarry ke lokasi proyek serta konsumsi solar alat berat & bekisting.
            <i>Solusi: Pengadaan material lokal (&lt;100 km) & sistem pracetak modular.</i>
        </div>
        <div class="lca-card">
            <b>🏢 Modul B1–B7 (Use Stage — Operational Carbon)</b><br/>
            Konsumsi listrik HVAC, pencahayaan, air bersih, dan penggantian komponen selama masa layan bangunan.
            <i>Solusi: Desain selubung termal pasif, kaca Low-E, dan PLTS atap.</i>
        </div>
        <div class="lca-card">
            <b>♻️ Modul C1–D (End-of-Life & Circular Economy)</b><br/>
            Pembongkaran selektif, pemilahan limbah beton/baja, dan kredit daur ulang di luar batas sistem proyek.
            <i>Solusi: Terapkan prinsip Design for Deconstruction (DfD).</i>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🏅 Benchmark Intensitas Embodied Carbon & Sertifikasi Greenship GBCI")
    bench_df = pd.DataFrame([
        {"Tipologi Bangunan": "Rumah Tinggal Tapak (1–2 Lantai)", "Konvensional (kg CO2e/m²)": "320 – 450", "Target Hijau (kg CO2e/m²)": "< 240", "Strategi Utama": "Bata ringan AAC, kayu bersertifikat, semen PCC"},
        {"Tipologi Bangunan": "Gedung Kantor / Kampus (4–8 Lantai)", "Konvensional (kg CO2e/m²)": "480 – 650", "Target Hijau (kg CO2e/m²)": "< 350", "Strategi Utama": "Beton 40% Fly Ash/GGBFS, tulangan EAF, fasad Low-E"},
        {"Tipologi Bangunan": "Bangunan Tinggi / High-Rise (>15 Lantai)", "Konvensional (kg CO2e/m²)": "620 – 850", "Target Hijau (kg CO2e/m²)": "< 460", "Strategi Utama": "Optimasi pelat post-tension, beton mutu tinggi rendah klinker"},
        {"Tipologi Bangunan": "Gudang / Bangunan Industri Bentang Lebar", "Konvensional (kg CO2e/m²)": "290 – 420", "Target Hijau (kg CO2e/m²)": "< 210", "Strategi Utama": "Profil baja daur ulang EAF, pelat lantai serat baja"}
    ])
    st.dataframe(bench_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#94a3b8;font-size:0.85rem;'>"
    "EcoBuild Pro v2.1 • Civil Carbon & Cost Intelligence Platform • CV Kingsman IDN • "
    "Dosen Pembimbing: Dr. Ir. Dedy Firmansyah, S.Pd., M.T."
    "</p>",
    unsafe_allow_html=True
)
