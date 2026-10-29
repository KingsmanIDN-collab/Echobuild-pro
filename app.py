import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import base64

# ==========================================
# 1. KONFIGURASI HALAMAN & ADAPTIVE CSS
# ==========================================
st.set_page_config(
    page_title="EcoBuild Pro - Civil Carbon & Cost Intelligence",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper Function untuk Encode Gambar ke Base64 (Untuk CSS Adaptif)
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

# Cari File Gambar Background Green Building
bg_file = get_existing_image([
    "bg_green_building.avif", 
    "bg_green_building.jpg", 
    "bg_green_building.jpeg", 
    "bg_green_building.png"
])

bg_base64_url = get_image_base64(bg_file)
if not bg_base64_url:
    bg_base64_url = "https://images.unsplash.com/photo-1541888946425-d0fbb186a5b3?q=80&w=1200"

# Custom CSS Styling (Adaptif Light & Dark Mode)
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    
    /* Hero Banner Background Styling */
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

    /* Sidebar Adaptif Tema (Light & Dark Mode) */
    section[data-testid="stSidebar"] {{
        border-right: 1px solid rgba(128, 128, 128, 0.2);
    }}

    /* Kartu & Box Mengikuti Tema */
    .custom-card {{
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATABASE MATERIAL, BIAYA, & EMISI
# (Acuan: ICE Database Bath Univ, Permen PUPR 21/2021)
# ==========================================
CARBON_FACTORS = {
    "Beton K-300 (Konvensional)": {"factor": 320, "unit": "m³", "cost": 1100000},
    "Beton K-400 (High Strength)": {"factor": 380, "unit": "m³", "cost": 1350000},
    "Beton Ramah Lingkungan (Fly Ash 30%)": {"factor": 220, "unit": "m³", "cost": 1050000},
    "Baja Tulangan (Konvensional)": {"factor": 1.99, "unit": "kg", "cost": 15000},
    "Baja Daur Ulang (Recycled Steel)": {"factor": 0.85, "unit": "kg", "cost": 16500},
    "Kayu Ols / Engineered Timber": {"factor": 300, "unit": "m³", "cost": 4500000},
    "Bata Merah Press": {"factor": 0.24, "unit": "buah", "cost": 1000},
    "Semen Portland (OPC)": {"factor": 0.82, "unit": "kg", "cost": 1500},
    "Kaca Lembaran": {"factor": 0.85, "unit": "kg", "cost": 35000},
    "Keramik Lantai": {"factor": 12.0, "unit": "m²", "cost": 85000},
    "Aspal Hotmix": {"factor": 60.0, "unit": "ton", "cost": 1300000},
}

# ==========================================
# 3. SIDEBAR NAVIGASI & LOGO SWITCHER FIX
# ==========================================
def navigate_to(page_name):
    st.session_state["nav_menu"] = page_name

if "nav_menu" not in st.session_state:
    st.session_state["nav_menu"] = "🏠 Beranda"

# Deteksi File Logo Light dan Dark
logo_light_path = get_existing_image(["logo_light.png", "logo_light.jpg", "logo_light.jpeg", "logo_light.avif"])
logo_dark_path = get_existing_image(["logo_dark.png", "logo_dark.jpg", "logo_dark.jpeg", "logo_dark.avif"])

logo_light_b64 = get_image_base64(logo_light_path)
logo_dark_b64 = get_image_base64(logo_dark_path)

if logo_light_b64 and logo_dark_b64:
    st.sidebar.markdown(f"""
        <style>
        .sidebar-logo-wrapper {{
            text-align: left;
            margin-bottom: 15px;
        }}
        .logo-img-light {{
            display: block;
            width: 170px;
            height: auto;
            border-radius: 10px;
        }}
        .logo-img-dark {{
            display: none;
            width: 170px;
            height: auto;
            border-radius: 10px;
        }}

        /* Switcher Otomatis saat Streamlit Mengaktifkan Dark Mode */
        [data-theme="dark"] .logo-img-light,
        .stApp[data-theme="dark"] .logo-img-light {{
            display: none !important;
        }}
        [data-theme="dark"] .logo-img-dark,
        .stApp[data-theme="dark"] .logo-img-dark {{
            display: block !important;
        }}
        </style>

        <div class="sidebar-logo-wrapper">
            <img src="{logo_light_b64}" class="logo-img-light" alt="Logo Kingsman Light" />
            <img src="{logo_dark_b64}" class="logo-img-dark" alt="Logo Kingsman Dark" />
        </div>
    """, unsafe_allow_html=True)
elif logo_light_path:
    st.sidebar.image(logo_light_path, width=170)
elif logo_dark_path:
    st.sidebar.image(logo_dark_path, width=170)

st.sidebar.title("EcoBuild Pro v2.0")
st.sidebar.caption("Civil Carbon & Cost Intelligence Platform")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Pilih Menu Utama:",
    ["🏠 Beranda", "🧮 Kalkulator & Analisis Proyek", "⚖️ Simulasi Komparasi Desain", "📚 Siklus Hidup Emisi & Solusi"],
    key="nav_menu"
)

# --- BLOK DOSEN PENGAMPU (SUPPORT DUAL THEME) ---
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
    # Hero Section
    st.markdown("""
        <div class="hero-container">
            <div class="hero-badge">Green Building & Civil Engineering Intelligence</div>
            <div class="hero-title">EcoBuild Pro Simulator</div>
            <div class="hero-subtitle">Platform analisis kuantitatif jejak emisi karbon (Embodied & Construction Carbon) serta optimasi biaya untuk proyek konstruksi teknik sipil yang berkelanjutan.</div>
        </div>
    """, unsafe_allow_html=True)

    # Section Latar Belakang & Urgensi Iklim (Layout 2 Kolom)
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

        # Gambar Asap Industri / Gas Rumah Kaca
        img_gas = get_existing_image(["gas_emisi.jpg", "gas_emisi.jpeg", "gas-rumah-kaca.jpg"])
        if img_gas:
            st.image(img_gas, caption="Emisi Gas Rumah Kaca Sektor Industri & Pabrikasi Material", use_container_width=True)

    with col_bg2:
        st.warning("""
        🔥 **Pengingat Urgensi Iklim & Tanggung Jawab Profesi:**
        Bencana Kebakaran Hutan dan Lahan (Karhutla) di Indonesia menjadi bukti nyata masifnya pelepasan emisi karbon ke atmosfer yang memperparah pemanasan global. 
        
        Apabila para pelaku di industri **konstruksi dan teknik sipil acuh** terhadap jejak karbon dari material serta pelaksanaan proyek yang mereka bangun, maka akumulasi emisi akan semakin tidak terkendali. Sektor teknik sipil harus mengambil peran aktif dalam memitigasi emisi sejak tahap perencanaan, bukan justru memperberat krisis lingkungan yang ada.
        """)

        # Gambar Refleksi Karhutla
        img_karhutla = get_existing_image(["karhutla.jpg", "karhutla.jfif", "karhutla.jpg.jfif"])
        if img_karhutla:
            st.image(img_karhutla, caption="Refleksi Urgensi Bencana Karhutla & Dampak Emisi Karbon", use_container_width=True)

    st.markdown("---")

    # Sumber Acuan Data
    st.markdown("""
    **📚 Sumber Acuan Data Emisi Karbon:**  
    Koefisien emisi karbon material pada *software* ini disusun berdasarkan standar internasional **ICE Database (Inventory of Carbon and Energy)** dari University of Bath, **Permen PUPR No. 21/2021** tentang Penilaian Kinerja Bangunan Gedung Hijau, serta rujukan dokumen **EPD (Environmental Product Declaration)** pabrikan material.
    """)

    st.markdown("<br>", unsafe_allow_html=True)

    # Grid Card Fitur Interaktif dengan Tombol Navigasi
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
    st.write("Masukkan volume material, jarak angkut logistik, dan konsumsi alat berat proyek kamu.")

    # Sidebar Inputs
    st.sidebar.markdown("---")
    st.sidebar.subheader("1. Input Material Standar")
    
    results = []
    total_mat_emission_kg = 0
    total_mat_cost = 0

    for material, data in CARBON_FACTORS.items():
        qty = st.sidebar.number_input(f"{material} ({data['unit']}):", min_value=0.0, value=0.0, step=10.0)
        if qty > 0:
            emission = qty * data["factor"]
            cost = qty * data["cost"]
            results.append({
                "Material": material,
                "Jumlah": qty,
                "Satuan": data["unit"],
                "Emisi (kg CO2e)": emission,
                "Biaya (Rp)": cost
            })
            total_mat_emission_kg += emission
            total_mat_cost += cost

    # Input Material Kustom Tambahan
    st.sidebar.markdown("---")
    st.sidebar.subheader("➕ Tambah Material Kustom")
    c_name = st.sidebar.text_input("Nama Material Kustom:")
    c_unit = st.sidebar.text_input("Satuan (m³, kg, unit, dll):", value="unit")
    c_qty = st.sidebar.number_input("Jumlah Volume Kustom:", min_value=0.0, value=0.0)
    c_factor = st.sidebar.number_input("Faktor Emisi (kg CO2e/unit):", min_value=0.0, value=0.0)
    c_price = st.sidebar.number_input("Harga Satuan (Rp):", min_value=0.0, value=0.0)

    if c_name and c_qty > 0:
        c_emission = c_qty * c_factor
        c_cost = c_qty * c_price
        results.append({
            "Material": f"{c_name} (Custom)",
            "Jumlah": c_qty,
            "Satuan": c_unit,
            "Emisi (kg CO2e)": c_emission,
            "Biaya (Rp)": c_cost
        })
        total_mat_emission_kg += c_emission
        total_mat_cost += c_cost

    st.sidebar.markdown("---")
    st.sidebar.subheader("2. Logistik & Alat Berat")
    dist_km = st.sidebar.number_input("Rata-rata Jarak Pengangkutan (km):", min_value=0.0, value=25.0, step=5.0)
    fuel_liter = st.sidebar.number_input("Estimasi Solar Alat Berat (Liter):", min_value=0.0, value=100.0, step=50.0)

    # Perhitungan Emisi Logistik & Alat Berat
    transport_emission_kg = dist_km * 0.25 * 10
    equipment_emission_kg = fuel_liter * 2.68
    
    total_project_emission_kg = total_mat_emission_kg + transport_emission_kg + equipment_emission_kg
    total_project_emission_ton = total_project_emission_kg / 1000

    # Main Display
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
        tab_a, tab_b = st.tabs(["📊 Breakdown Emisi", "📄 Tabel Data & Ekspor"])
        
        df = pd.DataFrame(results)

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
            
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Laporan Hasil Perhitungan (CSV)",
                data=csv_data,
                file_name="Laporan_Emisi_EcoBuild.csv",
                mime="text/csv"
            )
    else:
        st.info("👈 Masukkan volume material pada menu sidebar di sebelah kiri untuk menampilkan analisis.")

# ==========================================
# MENU 3: SIMULASI KOMPARASI DESAIN
# ==========================================
elif menu == "⚖️ Simulasi Komparasi Desain":
    st.title("⚖️ Simulasi Komparasi: Skenario A vs Skenario B")
    st.write("Bandingkan dua opsi desain dengan menentukan jumlah jenis material yang ingin dibandingkan.")

    # Expander Tabel Acuan
    with st.expander("📖 Lihat Daftar Acuan & Faktor Emisi Standar (ICE Database / PUPR)"):
        ref_list = []
        for mat_name, d_val in CARBON_FACTORS.items():
            ref_list.append({
                "Nama Material": mat_name,
                "Faktor Emisi (kg CO2e/satuan)": d_val["factor"],
                "Satuan": d_val["unit"],
                "Estimasi Harga Satuan": f"Rp {d_val['cost']:,}"
            })
        st.dataframe(pd.DataFrame(ref_list), use_container_width=True)

    options_list = list(CARBON_FACTORS.keys()) + ["➕ Material Kustom"]

    num_items = st.number_input(
        "🔢 Jumlah Jenis Material yang Ingin Dibandingkan per Skenario:", 
        min_value=1, 
        max_value=10, 
        value=2, 
        step=1
    )

    st.markdown("---")
    col_s1, col_s2 = st.columns(2)

    # --- SKENARIO A ---
    emisi_a = 0
    biaya_a = 0
    with col_s1:
        st.subheader("🔴 Skenario A (Desain 1)")
        for i in range(int(num_items)):
            st.markdown(f"**Material {i+1} (A)**")
            
            default_idx_a = i if i < len(options_list) - 1 else 0
            mat_a = st.selectbox(f"Pilih Material {i+1} (A):", options_list, index=default_idx_a, key=f"sa_m_{i}")
            
            if mat_a == "➕ Material Kustom":
                unit_a = st.text_input(f"Satuan Mat {i+1} A:", value="unit", key=f"c_ua_{i}")
                c_fa = st.number_input(f"Faktor Emisi Mat {i+1} A (kg CO2e):", min_value=0.0, value=1.0, key=f"c_fa_{i}")
                c_ca = st.number_input(f"Harga Satuan Mat {i+1} A (Rp):", min_value=0.0, value=1000.0, key=f"c_ca_{i}")
            else:
                c_fa = CARBON_FACTORS[mat_a]["factor"]
                c_ca = CARBON_FACTORS[mat_a]["cost"]
                unit_a = CARBON_FACTORS[mat_a]["unit"]
                
            vol_a = st.number_input(
                f"Volume / Jumlah Material {i+1} A ({unit_a}):", 
                min_value=0.0, 
                value=100.0 if i==0 else 0.0, 
                key=f"v_a_{i}"
            )
            
            emisi_a += (vol_a * c_fa)
            biaya_a += (vol_a * c_ca)
            if i < int(num_items) - 1:
                st.markdown("---")

    # --- SKENARIO B ---
    emisi_b = 0
    biaya_b = 0
    with col_s2:
        st.subheader("🟢 Skenario B (Desain 2)")
        for i in range(int(num_items)):
            st.markdown(f"**Material {i+1} (B)**")
            
            default_idx_b = (i + 2) if (i + 2) < len(options_list) - 1 else 0
            mat_b = st.selectbox(f"Pilih Material {i+1} (B):", options_list, index=default_idx_b, key=f"sb_m_{i}")
            
            if mat_b == "➕ Material Kustom":
                unit_b = st.text_input(f"Satuan Mat {i+1} B:", value="unit", key=f"c_ub_{i}")
                c_fb = st.number_input(f"Faktor Emisi Mat {i+1} B (kg CO2e):", min_value=0.0, value=1.0, key=f"c_fb_{i}")
                c_cb = st.number_input(f"Harga Satuan Mat {i+1} B (Rp):", min_value=0.0, value=1000.0, key=f"c_cb_{i}")
            else:
                c_fb = CARBON_FACTORS[mat_b]["factor"]
                c_cb = CARBON_FACTORS[mat_b]["cost"]
                unit_b = CARBON_FACTORS[mat_b]["unit"]
                
            vol_b = st.number_input(
                f"Volume / Jumlah Material {i+1} B ({unit_b}):", 
                min_value=0.0, 
                value=100.0 if i==0 else 0.0, 
                key=f"v_b_{i}"
            )
            
            emisi_b += (vol_b * c_fb)
            biaya_b += (vol_b * c_cb)
            if i < int(num_items) - 1:
                st.markdown("---")

    st.markdown("---")
    st.subheader("📈 Hasil Perbandingan Komparasi")

    emisi_a_ton = emisi_a / 1000
    emisi_b_ton = emisi_b / 1000
    hemat_emisi_pct = ((emisi_a - emisi_b) / emisi_a * 100) if emisi_a > 0 else 0
    selisih_biaya = biaya_b - biaya_a

    res_c1, res_c2, res_c3 = st.columns(3)
    with res_c1:
        st.metric("Total Emisi Skenario A", f"{emisi_a_ton:,.2f} Ton CO2e")
    with res_c2:
        st.metric("Total Emisi Skenario B", f"{emisi_b_ton:,.2f} Ton CO2e", delta=f"-{hemat_emisi_pct:.1f}% Reduksi Emisi", delta_color="normal")
    with res_c3:
        st.metric("Selisih Biaya (B - A)", f"Rp {selisih_biaya:,.0f}", delta=f"Rp {selisih_biaya:,.0f}", delta_color="inverse")

    comp_df = pd.DataFrame([
        {"Skenario": "Skenario A", "Emisi (Ton CO2e)": emisi_a_ton, "Biaya (Juta Rp)": biaya_a / 1e6},
        {"Skenario": "Skenario B", "Emisi (Ton CO2e)": emisi_b_ton, "Biaya (Juta Rp)": biaya_b / 1e6},
    ])

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(x=comp_df["Skenario"], y=comp_df["Emisi (Ton CO2e)"], name="Emisi (Ton CO2e)", marker_color='#ef5350'))
    fig_comp.add_trace(go.Bar(x=comp_df["Skenario"], y=comp_df["Biaya (Juta Rp)"], name="Biaya (Juta Rp)", marker_color='#26a69a'))
    fig_comp.update_layout(barmode='group', title="Grafik Komparasi Emisi Karbon dan Estimasi Biaya")
    st.plotly_chart(fig_comp, use_container_width=True)

# ==========================================
# MENU 4: SIKLUS HIDUP EMISI & SOLUSI
# ==========================================
elif menu == "📚 Siklus Hidup Emisi & Solusi":
    st.title("📚 Edukasi: Siklus Hidup Karbon dalam Teknik Sipil")
    st.write("Analisis Komprehensif Penilaian Siklus Hidup (*Life Cycle Assessment / LCA*) pada Struktur Bangunan Gedung dan Infrastruktur.")

    # 1. VISUAL OVERVIEW DISTRIBUSI EMISI BANYAK TAHUN
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

    # 2. DETAIL TAHAPAN DENGAN TAB INTERAKTIF
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
        st.write("""
        Tahap ini mencakup ekstraksi bahan mentah, pengangkutan ke pabrik pemrosesan, dan manufaktur material konstruksi. 
        Semen Portland dan baja struktur menyumbang porsi emisi terbesar pada tahap ini.
        """)
        
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
        st.write("""
        Emisi gas buang dari armada angkutan bahan mentah dari kuari (*quarry*) ke pabrik pengolahan, serta pendistribusian material dari pabrik ke tapak proyek konstruksi.
        """)
        
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
        st.write("""
        Seluruh emisi yang timbul dari aktivitas di lokasi pembangunan proyek sejak pekerjaan tanah (*earthworks*) hingga penyelesaian gedung.
        """)
        
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
        st.write("""
        Emisi yang dihasilkan dari konsumsi energi harian saat gedung dihuni selama puluhan tahun (pencahayaan, pengondisian udara, air, dan perawatan).
        """)
        
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
        st.write("""
        Proses perubuhan struktur gedung saat akhir masa layan, pengangkutan sampah bangunan, serta potensi manfaat daur ulang.
        """)
        
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

# ==========================================
# FOOTER (POSISI DI LUAR / MENTOK KIRI)
# ==========================================
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #777777; font-size: 0.9rem;'>"
    "Design by <b>CV Kingsman IDN</b>"
    "</p>", 
    unsafe_allow_html=True
)
