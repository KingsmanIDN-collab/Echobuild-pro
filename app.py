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
        border-top: 5px
