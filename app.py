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

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ==========================================
# 1. KONFIGURASI HALAMAN & ADAPTIVE CSS
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
        
    with open(fname, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{data}"

def get_existing_image(filename_list):
    for fname in filename_list:
        if os.path.exists(fname):
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
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    
    .hero-container {{
        position: relative;
        background: linear-gradient(135deg, rgba(15, 32, 39, 0.88), rgba(32, 58, 67, 0.85)), 
                    url('{bg_base64_url}');
        background-size: cover;
        background-position: center;
        padding: 50px 30px;
        border-radius: 20px;
        color: #ffffff !important;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }}
    .hero-badge {{
        background-color: rgba(46, 125, 50, 0.9);
        color: #ffffff !important;
        padding: 6px 18px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 14px;
    }}
    .hero-title {{
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 12px;
        letter-spacing: -0.5px;
        color: #ffffff !important;
    }}
    .hero-subtitle {{
        font-size: 1.05rem;
        opacity: 0.92;
        max-width: 850px;
        margin: 0 auto;
        font-weight: 400;
        line-height: 1.6;
        color: #ffffff !important;
    }}

    section[data-testid="stSidebar"] {{
        border-right: 1px solid rgba(128, 128, 128, 0.2);
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DYNAMIC EXCEL ICE DATABASE PARSER
# ==========================================
@st.cache_data
def load_ice_excel_database():
    excel_file = get_existing_image([
        "ICE DB Educational V5.0 - Jun 2026.xlsx",
        "ICE DB Educational V5.0.xlsx",
        "ICE_Database.xlsx"
    ])
    
    if not excel_file or not os.path.exists(excel_file):
        default_ver = "Educational (V5.0) - Standar Default"
        default_df = pd.DataFrame([
            {"Kategori": "Concrete", "Nama Material": "Beton K-300 (Konvensional)", "Faktor Emisi (kg CO2e/kg)": 0.134, "Satuan": "kg"},
            {"Kategori": "Steel", "Nama Material": "Baja Tulangan (Konvensional)", "Faktor Emisi (kg CO2e/kg)": 1.990, "Satuan": "kg"},
            {"Kategori": "Timber", "Nama Material": "Kayu Ols / Engineered Timber", "Faktor Emisi (kg CO2e/kg)": 0.300, "Satuan": "kg"},
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
                if "Educational" in val or "V5." in val or "V4." in val or "Jun 20" in val or "2026" in val:
                    if "ICE DB Version:" not in val and len(val) < 60:
                        version_str = val
                        break
        
        materials_list = []
        current_cat = "General Material"
        
        for idx in range(18, len(df_raw)):
            row = df_raw.iloc[idx]
            valid_vals = [x for x in row.values if pd.notna(x)]
            if not valid_vals:
                continue
                
            first_val = str(valid_vals[0]).strip()
            
            if len(valid_vals) == 1 and not first_val.startswith("http") and not first_val.startswith("Module"):
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
                        
            if full_name and carbon_val is not None and not full_name.startswith("Name Exactly") and not full_name.startswith("Materials"):
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
# 4. SIDEBAR NAVIGASI & LOGO
# ==========================================
def navigate_to(page_name):
    st.session_state["nav_menu"] = page_name

if "nav_menu" not in st.session_state:
    st.session_state["nav_menu"] = "🏠 Beranda"

logo_path = get_existing_image(["logo_kingsman.png", "logo_kingsman.jpg", "logo.png", "logo.jpg"])
if logo_path:
    st.sidebar.image(logo_path, width=170)
else:
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4300/4300058.png", width=60)

st.sidebar.title("EcoBuild Pro v2.0")
st.sidebar.caption("Civil Carbon & Cost Intelligence Platform")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Pilih Menu Utama:",
    ["🏠 Beranda", "🧮 Kalkulator & Analisis Proyek", "📊 Database Material ICE (Otomatis)", "⚖️ Simulasi Komparasi Desain", "📚 Siklus Hidup Emisi & Solusi"],
    key="nav_menu"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style="
        background: var(--secondary-background-color);
        padding: 14px 16px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin-top: 10px;
    ">
        <span style="font-size: 0.78rem; font-weight: 700; opacity: 0.8; text-transform: uppercase; letter-spacing: 0.5px;">👨‍🏫 Dosen Pengampu</span><br>
        <span style="font-size: 0.95rem; font-weight: 700; display: inline-block; margin-top: 4px;">Dr. Ir. Dedy Firmansyah, S.Pd., M.T.</span>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# MENU 1: BERANDA
# ==========================================
if menu == "🏠 Beranda":
    st.markdown("""
        <div class="hero-container">
            <div class="hero-badge">Green Building & Civil Engineering Intelligence</div>
            <div class="hero-title">EcoBuild Pro Simulator</div>
            <div class="hero-subtitle">Platform analisis kuantitatif jejak emisi karbon (Embodied & Construction Carbon) serta optimasi biaya untuk proyek konstruksi teknik sipil yang berkelanjutan.</div>
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
# MENU 2: KALKULATOR & ANALISIS PROYEK (MULTI-ITEM DYNAMIC)
# ==========================================
elif menu == "🧮 Kalkulator & Analisis Proyek":
    st.title("🧮 Kalkulator Emisi & Biaya Proyek")
    st.write("Hitung jejak emisi karbon dan estimasi biaya proyek dengan memilih material dari **ICE Database** atau mengisi **Material Kustom** secara fleksibel.")

    with st.expander("💾 Backup / Restorasi Proyek (JSON) & Impor File RAB Excel", expanded=False):
        c_exp1, c_exp2 = st.columns(2)
        
        with c_exp1:
            st.subheader("📥 Impor File RAB (.xlsx / .csv)")
            uploaded_rab = st.file_uploader("Unggah file RAB Excel/CSV (Kolom: Material, Jumlah):", type=["xlsx", "csv"])
            if uploaded_rab is not None:
                try:
                    df_rab = pd.read_csv(uploaded_rab) if uploaded_rab.name.endswith(".csv") else pd.read_excel(uploaded_rab)
                    if "Material" in df_rab.columns and "Jumlah" in df_rab.columns:
                        st.session_state["calc_rab_data"] = df_rab.to_dict('records')
                        st.success("✅ Volume material dari RAB berhasil diimpor!")
                    else:
                        st.error("File RAB wajib memiliki kolom 'Material' dan 'Jumlah'.")
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
                mime="application/json"
            )

    st.markdown("---")
    
    col_cnt1, col_cnt2 = st.columns([1, 2])
    with col_cnt1:
        num_items = st.number_input(
            "🔢 Jumlah Jenis Material yang Ingin Dihitung:",
            min_value=1,
            max_value=30,
            value=int(st.session_state.get("calc_num_items", 3)),
            step=1,
            key="input_num_items"
        )
        st.session_state["calc_num_items"] = num_items

    ice_mat_names = df_ice_materials["Nama Material"].tolist()
    all_mat_options = ["➕ Material Kustom (Isi Sendiri)"] + ice_mat_names

    st.subheader("📦 Input Item Material Proyek")
    
    results = []
    total_mat_emission_kg = 0
    total_mat_cost = 0

    for i in range(num_items):
        st.markdown(f"##### 📌 Item Material #{i+1}")
        c_m1, c_m2, c_m3 = st.columns([2.2, 1.2, 1.2])
        
        with c_m1:
            def_idx = (i + 1) if (i + 1) < len(all_mat_options) else 0
            sel_mat = st.selectbox(
                f"Pilih / Cari Material #{i+1}:",
                options=all_mat_options,
                index=def_idx,
                key=f"calc_sel_{i}"
            )

        if sel_mat == "➕ Material Kustom (Isi Sendiri)":
            c_cust1, c_cust2, c_cust3, c_cust4 = st.columns([1.5, 1, 1, 1])
            with c_cust1:
                mat_name = st.text_input(f"Nama Material Kustom #{i+1}:", value=f"Material Kustom {i+1}", key=f"c_name_{i}")
            with c_cust2:
                unit_str = st.text_input(f"Satuan #{i+1}:", value="kg", key=f"c_unit_{i}")
            with c_cust3:
                factor_val = st.number_input(f"Faktor Emisi (kg CO2e/{unit_str}):", min_value=0.0, value=1.0, step=0.1, key=f"c_fact_{i}")
            with c_cust4:
                price_val = st.number_input(f"Harga Satuan (Rp/{unit_str}):", min_value=0.0, value=10000.0, step=1000.0, key=f"c_price_{i}")
            
            qty_val = st.number_input(f"Jumlah / Volume ({unit_str}) #{i+1}:", min_value=0.0, value=0.0, step=10.0, key=f"c_qty_{i}")
        else:
            mat_info = df_ice_materials[df_ice_materials["Nama Material"] == sel_mat].iloc[0]
            mat_name = sel_mat
            unit_str = mat_info["Satuan"]
            factor_val = float(mat_info["Faktor Emisi (kg CO2e/kg)"])
            
            with c_m2:
                st.info(f"**Satuan:** `{unit_str}`\n\n**Emisi:** `{factor_val:.6f}` kg CO2e/kg")
            
            with c_m3:
                price_val = st.number_input(f"Harga Satuan (Rp/{unit_str}) #{i+1}:", min_value=0.0, value=15000.0, step=1000.0, key=f"p_val_{i}")
            
            qty_val = st.number_input(f"Jumlah / Berat ({unit_str}) #{i+1}:", min_value=0.0, value=0.0, step=100.0, key=f"q_val_{i}")

        if qty_val > 0:
            e_kg = qty_val * factor_val
            c_rp = qty_val * price_val
            results.append({
                "Material": mat_name,
                "Jumlah": qty_val,
                "Satuan": unit_str,
                "Emisi (kg CO2e)": e_kg,
                "Biaya (Rp)": c_rp
            })
            total_mat_emission_kg += e_kg
            total_mat_cost += c_rp

        if i < num_items - 1:
            st.markdown("---")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🚚 Pengangkutan Logistik & Alat Berat")
    st.session_state["dist_km"] = st.sidebar.number_input("Jarak Pengangkutan (km):", min_value=0.0, value=float(st.session_state["dist_km"]), step=5.0)
    st.session_state["fuel_liter"] = st.sidebar.number_input("Solar Alat Berat (Liter):", min_value=0.0, value=float(st.session_state["fuel_liter"]), step=50.0)

    transport_emission_kg = st.session_state["dist_km"] * 0.25 * 10
    equipment_emission_kg = st.session_state["fuel_liter"] * 2.68
    
    total_project_emission_kg = total_mat_emission_kg + transport_emission_kg + equipment_emission_kg
    total_project_emission_ton = total_project_emission_kg / 1000

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Emisi Karbon", f"{total_project_emission_ton:,.2f} Ton CO2e")
    with c2:
        st.metric("Total Estimasi Biaya Material", f"Rp {total_mat_cost:,.0f}")
    with c3:
        cost_per_ton = (total_mat_cost / total_project_emission_ton) if total_project_emission_ton > 0 else 0
        st.metric("Rasio Biaya / Emisi", f"Rp {cost_per_ton:,.0f} / Ton")

    st.markdown("---")

    if results:
        df = pd.DataFrame(results)
        tab_a, tab_b = st.tabs(["📊 Breakdown Emisi & Grafik", "📄 Tabel Data & Ekspor Laporan"])

        with tab_a:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                fig_pie = px.pie(df, names="Material", values="Emisi (kg CO2e)", title="Kontribusi Emisi Antar Material", hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_g2:
                source_df = pd.DataFrame([
                    {"Sumber": "Material Konstruksi", "Emisi (Ton CO2e)": total_mat_emission_kg / 1000},
                    {"Sumber": "Pengangkutan Logistik", "Emisi (Ton CO2e)": transport_emission_kg / 1000},
                    {"Sumber": "BBM Alat Berat", "Emisi (Ton CO2e)": equipment_emission_kg / 1000},
                ])
                fig_bar = px.bar(source_df, x="Sumber", y="Emisi (Ton CO2e)", color="Sumber", title="Sumber Emisi Karbon Proyek (Ton CO2e)")
                st.plotly_chart(fig_bar, use_container_width=True)

        with tab_b:
            st.dataframe(df, use_container_width=True)
            
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
    * **Mekanisme Update:** Data di bawah ini dibaca **langsung dari file Excel**. Jika di kemudian hari terdapat pembaruan data, developer/admin cukup mengganti file `.xlsx` di repository GitHub, dan seluruh data di halaman ini akan berganti secara otomatis.
    """)

    col_search1, col_search2 = st.columns([1, 2])
    with col_search1:
        cat_select = st.selectbox("🔍 Filter Berdasarkan Kategori:", ["Semua Kategori"] + sorted(list(df_ice_materials["Kategori"].unique())))
    with col_search2:
        search_query = st.text_input("🔎 Cari Nama Material Spesifik:", placeholder="Ketik nama material, misal: Concrete, Steel, Aluminium...")

    display_df = df_ice_materials.copy()
    if cat_select != "Semua Kategori":
        display_df = display_df[display_df["Kategori"] == cat_select]
    if search_query:
        display_df = display_df[display_df["Nama Material"].str.contains(search_query, case=False, na=False)]

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
    st.write("Bandingkan dua opsi desain dengan menentukan jenis material dari database ICE.")

    mat_options = df_ice_materials["Nama Material"].tolist()

    col_s1, col_s2 = st.columns(2)

    emisi_a = 0
    with col_s1:
        st.subheader("🔴 Skenario A (Desain 1)")
        mat_a = st.selectbox("Pilih Material (Skenario A):", mat_options, index=0, key="sa_m")
        vol_a = st.number_input("Jumlah Material A (kg):", min_value=0.0, value=1000.0, key="v_a")
        
        f_a = float(df_ice_materials[df_ice_materials["Nama Material"] == mat_a].iloc[0]["Faktor Emisi (kg CO2e/kg)"])
        emisi_a = vol_a * f_a

    emisi_b = 0
    with col_s2:
        st.subheader("🟢 Skenario B (Desain 2)")
        mat_b = st.selectbox("Pilih Material (Skenario B):", mat_options, index=min(1, len(mat_options)-1), key="sb_m")
        vol_b = st.number_input("Jumlah Material B (kg):", min_value=0.0, value=1000.0, key="v_b")
        
        f_b = float(df_ice_materials[df_ice_materials["Nama Material"] == mat_b].iloc[0]["Faktor Emisi (kg CO2e/kg)"])
        emisi_b = vol_b * f_b

    st.markdown("---")
    st.subheader("📈 Hasil Perbandingan Komparasi Emisi")

    emisi_a_ton = emisi_a / 1000
    emisi_b_ton = emisi_b / 1000
    hemat_emisi_pct = ((emisi_a - emisi_b) / emisi_a * 100) if emisi_a > 0 else 0

    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.metric("Total Emisi Skenario A", f"{emisi_a_ton:,.3f} Ton CO2e")
    with res_c2:
        st.metric("Total Emisi Skenario B", f"{emisi_b_ton:,.3f} Ton CO2e", delta=f"-{hemat_emisi_pct:.1f}% Reduksi Emisi", delta_color="normal")

    comp_df = pd.DataFrame([
        {"Skenario": "Skenario A", "Emisi (Ton CO2e)": emisi_a_ton},
        {"Skenario": "Skenario B", "Emisi (Ton CO2e)": emisi_b_ton},
    ])

    fig_comp = px.bar(comp_df, x="Skenario", y="Emisi (Ton CO2e)", color="Skenario", title="Grafik Komparasi Emisi Karbon Material")
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
            * **Kalsinasi Batu Kapur:** Pembakaran $\text{CaCO}_3 \rightarrow \text{CaO} + \text{CO}_2$ pada kiln semen dengan suhu $>1400^\circ\text{C}$.
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
            * **Local Material Sourcing:** Memprioritaskan pembelian material dari produsen dalam radius $< 100\text{ km}$ dari tapak proyek.
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
            * **Emisi Landfill:** Penguraian sisa kayu/organik yang menghasilkan gas metana ($\text{CH}_4$).
            """)
        with col_t5b:
            st.success("""
            **💡 Solusi & Best Practices:**
            * **Design for Deconstruction (DfD):** Merancang sambungan baut (*bolted connections*) agar elemen struktur mudah dibongkar dan dipakai ulang.
            * **Recycled Concrete Aggregate (RCA):** Menghancurkan puing beton lama untuk dijadikan agregat kasar campuran beton baru atau lapis pondasi jalan.
            * **Daur Ulang Baja 100%:** Melakukan peleburan ulang seluruh baja tulangan dan baja profil bekas perubuhan.
            """)

# FOOTER
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #777777; font-size: 0.9rem;'>"
    "Design by <b>CV Kingsman IDN</b>"
    "</p>", 
    unsafe_allow_html=True
)
