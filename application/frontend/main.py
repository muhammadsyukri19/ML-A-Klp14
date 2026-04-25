import streamlit as st
import requests
import time

st.set_page_config(page_title="AgroPredict — Plant Growth System", page_icon="🌱", layout="wide")

# ─── Inline CSS (Digabungkan dari style.css) ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700;800&display=swap');

/* Global Reset */
* { font-family: 'Outfit', sans-serif; }
h1, h2, h3, h4, h5, h6 { 
    font-family: 'Space Grotesk', sans-serif !important; 
    font-weight: 700 !important; 
    color: #064e3b !important; 
}

/* Animated Mesh Gradient Background */
[data-testid="stAppViewContainer"] {
    background-color: #ecfdf5 !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(16, 185, 129, 0.15) 0, transparent 50%), 
        radial-gradient(at 100% 0%, rgba(5, 150, 105, 0.15) 0, transparent 50%),
        radial-gradient(at 50% 100%, rgba(52, 211, 153, 0.15) 0, transparent 50%);
    background-attachment: fixed;
}

/* Hide default streamlit header for cleaner look */
header[data-testid="stHeader"] { background: transparent !important; }

/* Sidebar Glassmorphism */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.7) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255, 255, 255, 0.5) !important;
}

/* Hero Section */
.hero-section {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 32px;
    padding: 4.5rem 3rem;
    text-align: center;
    box-shadow: 0 10px 40px rgba(16, 185, 129, 0.08);
    margin-bottom: 3.5rem;
    position: relative;
    overflow: hidden;
    animation: fadeIn 1s ease-out forwards;
}

.hero-section::before {
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.1) 100%);
    z-index: -1;
}

.hero-section h1 {
    font-size: 3.8rem !important;
    background: linear-gradient(135deg, #064e3b 0%, #059669 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1.2rem;
    letter-spacing: -0.03em;
}

.hero-section p {
    color: #475569 !important;
    font-size: 1.2rem;
    max-width: 750px;
    margin: 0 auto;
    line-height: 1.7;
}

/* Glassmorphism Feature Groups (Bento Grid Style) */
.feature-group {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-radius: 28px;
    padding: 2.5rem;
    margin-bottom: 2.5rem;
    box-shadow: 0 8px 32px 0 rgba(5, 150, 105, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.9);
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.feature-group:hover {
    transform: translateY(-6px);
    box-shadow: 0 15px 45px 0 rgba(5, 150, 105, 0.1);
    background: rgba(255, 255, 255, 0.75);
}

.feature-group-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #0f172a;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
}

.feature-group-desc {
    color: #64748b;
    font-size: 1.05rem;
    margin-bottom: 2.5rem;
    line-height: 1.6;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid rgba(16, 185, 129, 0.15);
}

/* Stat Cards - Diperbarui agar teks tidak terpotong */
.stat-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 1.5rem;
    display: flex;
    flex-direction: column; /* Ubah ke column agar konten menumpuk rapi ke bawah */
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: 0.5rem;
    border: 1px solid rgba(255, 255, 255, 0.9);
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    transition: transform 0.3s ease;
}
.stat-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.06); }
.stat-icon { font-size: 2.2rem; background: #ecfdf5; padding: 0.8rem; border-radius: 16px; margin-bottom: -0.2rem; }
.stat-value { font-size: 2rem; font-family: 'Space Grotesk', sans-serif; font-weight: 800; color: #064e3b; display: block; line-height: 1; }
.stat-label { font-size: 0.85rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; white-space: normal; line-height: 1.3; }

/* Form Controls */
[data-testid="stSlider"] > div > div > div > div {
    background-color: #10b981 !important;
}
.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.8) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(16, 185, 129, 0.2) !important;
    min-height: 3rem !important;
    display: flex !important;
    align-items: center !important;
}
.stSelectbox > div > div:focus-within {
    border-color: #10b981 !important;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2) !important;
}

/* Call to Action Button */
.stButton > button, [data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 20px !important;
    padding: 1rem 2rem !important;
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: 0.5px;
    box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3) !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    width: 100%;
}
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-4px) scale(1.01) !important;
    box-shadow: 0 15px 40px rgba(16, 185, 129, 0.4) !important;
}

/* Results Card */
.result-card {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(30px);
    border-radius: 32px;
    padding: 3.5rem 2rem;
    text-align: center;
    box-shadow: 0 25px 60px rgba(0,0,0,0.08);
    border: 1px solid rgba(255,255,255,0.9);
    animation: floatUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.result-success { border-top: 10px solid #10b981; }
.result-fail { border-top: 10px solid #ef4444; }

.result-icon { font-size: 5rem; margin-bottom: 1.5rem; animation: pop 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; opacity: 0; transform: scale(0.5); }
.result-title { font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 800; margin-bottom: 1rem; }
.result-success .result-title { color: #059669; }
.result-fail .result-title { color: #b91c1c; }
.result-desc { color: #475569; font-size: 1.2rem; line-height: 1.7; max-width: 650px; margin: 0 auto; }

/* Progress bar */
[data-testid="stProgress"] > div > div { background-color: #10b981 !important; }

/* Animations */
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes floatUp { from { opacity: 0; transform: translateY(50px); } to { opacity: 1; transform: translateY(0); } }
@keyframes pop { to { opacity: 1; transform: scale(1); } }

/* Footer */
.footer { text-align: center; padding: 2rem 0; color: #94a3b8; font-size: 0.95rem; margin-top: 4rem; }
</style>
""", unsafe_allow_html=True)

DEFAULT_API_URL = "http://127.0.0.1:8000"

# ─── Sidebar ───
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1892/1892751.png", width=80)
    st.markdown("## 🌿 AgroPredict")
    st.markdown("*Smart Plant Analysis*")
    st.markdown("---")
    page = st.radio("📌 Navigasi", ["🏠 Dashboard Prediksi", "ℹ️ Info Model"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("#### ⚙️ Konfigurasi")
    api_base = st.text_input("API URL", value=DEFAULT_API_URL, label_visibility="collapsed", placeholder="http://127.0.0.1:8000").strip().rstrip("/")
    debug_mode = st.toggle("🛠️ Debug Mode", value=False)
    st.markdown("---")
    st.caption("🎓 UTS Praktikum ML — Kelompok 14")


def get_model_info():
    """Mengambil informasi schema fitur dari backend API"""
    try:
        response = requests.get(f"{api_base}/model-info", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


if page == "🏠 Dashboard Prediksi":
    # 1. Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1>Sistem Prediksi Pertumbuhan Tanaman</h1>
        <p>Analisis cerdas berbasis <b>Machine Learning</b> untuk memprediksi tingkat kecocokan dan risiko kegagalan pertumbuhan tanaman berdasarkan kondisi lingkungan dan properti tanah Anda secara instan.</p>
    </div>
    """, unsafe_allow_html=True)

    model_info = get_model_info()
    if not model_info:
        st.error("⚠️ Gagal terhubung ke Backend API. Pastikan server FastAPI sudah berjalan (contoh: localhost:8000).")
        st.stop()

    features = model_info.get("features", [])

    # Mapping opsi kategori
    categorical_options = {
        "soil_type": ["sandy", "loam", "clay", "peat", "silt"],
        "moisture_regime": ["dry", "normal", "wet"],
        "thermal_regime": ["cool", "moderate", "hot"],
        "nutrient_balance": ["low", "balanced", "high"],
        "plant_category": ["cereal", "vegetable", "fruit", "legume"],
    }

    # Range value untuk slider numerik (min, max, default)
    slider_ranges = {
        "suitability_score": (0.0, 100.0, 50.0),
        "stress_level": (0.0, 10.0, 1.0),
        "ph_stress_flag": (0.0, 1.0, 0.0),
        "soil_temp_c": (-10.0, 50.0, 25.0),
        "air_temp_c": (-10.0, 50.0, 27.0),
        "soil_moisture_pct": (0.0, 100.0, 30.0),
        "salinity_ec": (0.0, 20.0, 1.5),
        "soil_ph": (1.0, 14.0, 6.5),
        "organic_matter_pct": (0.0, 100.0, 5.0),
        "moisture_limit_dry": (0.0, 50.0, 10.0),
        "moisture_limit_wet": (0.0, 100.0, 80.0),
        "buffering_capacity": (0.0, 100.0, 20.0),
        "cation_exchange_capacity": (0.0, 50.0, 15.0),
        "bulk_density": (0.5, 2.0, 1.2),
        "light_intensity_par": (0.0, 2000.0, 1000.0),
        "nitrogen_ppm": (0.0, 100.0, 20.0),
        "phosphate_ppm": (0.0, 100.0, 20.0),
        "potassium_ppm": (0.0, 100.0, 20.0),
    }

    # Grouping features
    groups_config = {
        "🌍 Properti Fisik Tanah": ["soil_type", "soil_ph", "bulk_density", "salinity_ec", "soil_temp_c", "soil_moisture_pct"],
        "🌤️ Kondisi Lingkungan": ["air_temp_c", "moisture_regime", "thermal_regime", "light_intensity_par"],
        "🧪 Kimia & Nutrisi": ["organic_matter_pct", "nutrient_balance", "cation_exchange_capacity", "buffering_capacity", "nitrogen_ppm", "phosphate_ppm", "potassium_ppm"],
        "📈 Skor & Kategori": ["plant_category", "suitability_score", "stress_level", "ph_stress_flag", "moisture_limit_dry", "moisture_limit_wet"]
    }

    # Deskripsi Group
    group_descriptions = {
        "🌍 Properti Fisik Tanah": "Karakteristik dasar dan struktur fisik tanah yang menentukan kemampuan retensi air dan sirkulasi udara untuk perakaran tanaman.",
        "🌤️ Kondisi Lingkungan": "Faktor iklim makro dan mikro yang memengaruhi laju transpirasi dan efisiensi fotosintesis tanaman secara langsung.",
        "🧪 Kimia & Nutrisi": "Ketersediaan unsur hara esensial dan tingkat kesuburan tanah yang menjadi sumber makanan utama bagi pertumbuhan tanaman.",
        "📈 Skor & Kategori": "Indikator kalkulasi sistem mengenai tingkat kesesuaian lahan, klasifikasi jenis tanaman, dan potensi stres yang mungkin dialami.",
        "📋 Parameter Lainnya": "Metrik tambahan yang dikalkulasi atau diidentifikasi secara otomatis oleh sistem backend."
    }

    # Process features from backend
    grouped_features = {k: [] for k in groups_config.keys()}
    grouped_features["📋 Parameter Lainnya"] = []

    for feat in features:
        name = feat.get("name")
        assigned = False
        for group_name, group_keys in groups_config.items():
            if name in group_keys:
                grouped_features[group_name].append(feat)
                assigned = True
                break
        if not assigned:
            grouped_features["📋 Parameter Lainnya"].append(feat)

    # Quick stats
    num_count = sum(1 for f in features if f.get("type") != "categorical")
    cat_count = len(features) - num_count
    
    st.markdown("### 📊 Ringkasan Dataset")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-icon">📑</div>
            <div class="stat-value">{len(features)}</div>
            <div class="stat-label">Total Fitur Model</div>
        </div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-icon">🔢</div>
            <div class="stat-value">{num_count}</div>
            <div class="stat-label">Fitur Numerik</div>
        </div>''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-icon">🏷️</div>
            <div class="stat-value">{cat_count}</div>
            <div class="stat-label">Fitur Kategorikal</div>
        </div>''', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 🧾 Parameter Input Lingkungan")

    # 2. Input Form
    with st.form("prediction_form", border=False):
        user_data = {}

        for group_name, group_feats in grouped_features.items():
            if not group_feats:
                continue
            
            desc = group_descriptions.get(group_name, "")
            
            st.markdown(f"""
            <div class="feature-group">
                <div class="feature-group-title">{group_name}</div>
                <div class="feature-group-desc">{desc}</div>
            """, unsafe_allow_html=True)

            cols = st.columns(3)
            for idx, feat in enumerate(group_feats):
                name = feat.get("name")
                ftype = feat.get("type", "numeric")
                col = cols[idx % 3]
                label = name.replace("_", " ").title()

                with col:
                    if ftype == "categorical":
                        opts = categorical_options.get(name, ["unknown"])
                        user_data[name] = st.selectbox(f"📋 {label}", options=opts, key=f"inp_{name}")
                    else:
                        min_v, max_v, default_v = slider_ranges.get(name, (0.0, 100.0, 10.0))
                        user_data[name] = st.slider(f"📊 {label}", min_value=float(min_v), max_value=float(max_v), value=float(default_v), step=0.1, key=f"inp_{name}")
            
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("🧪 Analisis & Prediksi Sekarang", use_container_width=True)

    if submit_btn:
        with st.spinner("⏳ Menganalisis parameter menggunakan model Machine Learning..."):
            time.sleep(0.5)
            payload = {"features": user_data}
            try:
                response = requests.post(f"{api_base}/predict", json=payload, timeout=20)

                if response.status_code == 200:
                    result = response.json()
                    pred_label = result.get("prediction")

                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if str(pred_label) in ["1", "true", "True", "failure", "yes"]:
                        st.markdown("""
                        <div class="result-card result-fail">
                            <div class="result-icon">⚠️</div>
                            <div class="result-title">Risiko Gagal Tinggi</div>
                            <div class="result-desc">Berdasarkan model AI kami, karakteristik lingkungan dan properti tanah ini <strong>KURANG COCOK</strong> untuk perkembangan tanaman secara optimal. Perlu dilakukan perbaikan pada lahan sebelum penanaman.</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="result-card result-success">
                            <div class="result-icon">🌱</div>
                            <div class="result-title">Sangat Mendukung (Ideal)</div>
                            <div class="result-desc">Berdasarkan model AI kami, karakteristik lingkungan dan properti tanah ini <strong>SANGAT COCOK</strong> untuk perkembangan tanaman secara optimal. Terus pertahankan kondisi ini!</div>
                        </div>
                        """, unsafe_allow_html=True)

                    if "failure_probability" in result:
                        prob = float(result["failure_probability"])
                        st.markdown("<br>", unsafe_allow_html=True)
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.metric(label="Tingkat Probabilitas Risiko (Failure Rate)", value=f"{prob * 100:.1f}%")
                            st.progress(min(max(prob, 0.0), 1.0))

                    if debug_mode:
                        st.markdown("<br>", unsafe_allow_html=True)
                        with st.expander("🛠️ Raw JSON Response (Backend)"):
                            st.json(result)

                else:
                    st.error(f"❌ Error dari API ({response.status_code}): {response.text}")
                    if debug_mode:
                        st.json(payload)

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Gagal mengirim data ke API: {e}")

    st.markdown('<div class="footer">Dibuat dengan ❤️ oleh Kelompok 14 — UTS Praktikum Machine Learning</div>', unsafe_allow_html=True)

elif page == "ℹ️ Info Model":
    st.markdown("""
    <div class="hero-section">
        <h1>Tentang AgroPredict</h1>
        <p>Sistem cerdas berbasis Machine Learning untuk melakukan analisis klasifikasi pada data agro-environmental secara otomatis.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('''
        <div class="stat-card" style="padding:2rem 1rem;">
            <div class="stat-icon" style="background: #e0f2fe;">⚡</div>
            <h4 style="margin:0.5rem 0; font-family:'Space Grotesk',sans-serif; color:#0f172a;">Backend API</h4>
            <p style="color:#64748b; font-size:0.9rem; margin:0; line-height:1.5;">FastAPI untuk serve model secara real-time.</p>
        </div>''', unsafe_allow_html=True)
    with c2:
        st.markdown('''
        <div class="stat-card" style="padding:2rem 1rem;">
            <div class="stat-icon" style="background: #fce7f3;">🖥️</div>
            <h4 style="margin:0.5rem 0; font-family:'Space Grotesk',sans-serif; color:#0f172a;">Frontend UI</h4>
            <p style="color:#64748b; font-size:0.9rem; margin:0; line-height:1.5;">Streamlit interaktif berkonsep Glassmorphism.</p>
        </div>''', unsafe_allow_html=True)
    with c3:
        st.markdown('''
        <div class="stat-card" style="padding:2rem 1rem;">
            <div class="stat-icon" style="background: #fef9c3;">🤖</div>
            <h4 style="margin:0.5rem 0; font-family:'Space Grotesk',sans-serif; color:#0f172a;">ML Framework</h4>
            <p style="color:#64748b; font-size:0.9rem; margin:0; line-height:1.5;">Scikit-Learn dengan pre-processing robust.</p>
        </div>''', unsafe_allow_html=True)
    with c4:
        st.markdown('''
        <div class="stat-card" style="padding:2rem 1rem;">
            <div class="stat-icon" style="background: #ffedd5;">📊</div>
            <h4 style="margin:0.5rem 0; font-family:'Space Grotesk',sans-serif; color:#0f172a;">Klasifikasi</h4>
            <p style="color:#64748b; font-size:0.9rem; margin:0; line-height:1.5;">Memprediksi binary label kegagalan panen.</p>
        </div>''', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("### 🏗️ Arsitektur Sistem")
    st.markdown("Alur data dari input pengguna hingga hasil prediksi diproses secara *seamless*:")
    st.markdown("""
    ```
    ┌─────────────┐    JSON Request    ┌─────────────┐    Load & Predict    ┌───────────┐
    │  Streamlit   │ ─────────────────▸ │   FastAPI    │ ──────────────────▸  │ ML Model  │
    │  (Frontend)  │ ◂───────────────── │  (Backend)   │ ◂──────────────────  │  (.pkl)   │
    └─────────────┘   JSON Response    └─────────────┘       Output         └───────────┘
    ```
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🔄 Cara Kerja Pipeline")
    
    st.markdown("""
    <div class="feature-group">
        <p><strong>1. Exploratory Data Analysis (EDA):</strong> Eksplorasi data agro-environmental untuk memahami distribusi dan korelasi fitur.</p>
        <p><strong>2. Data Cleaning & Pre-processing:</strong> Pembersihan missing values, outlier, normalisasi numerik, dan encoding fitur kategorikal.</p>
        <p><strong>3. Model Training:</strong> Pelatihan model Machine Learning dengan evaluasi berbagai metrik (accuracy, precision, recall, F1-score).</p>
        <p><strong>4. Deployment:</strong> Model disimpan dan di-serve melalui endpoint FastAPI, kemudian dikonsumsi oleh aplikasi Streamlit ini.</p>
    </div>
    """, unsafe_allow_html=True)

    model_info = get_model_info()
    if model_info:
        st.markdown("### 📋 Detail Skema Model Aktif")
        st.write("Sistem mendeteksi fitur berikut yang diperlukan oleh backend saat ini:")
        st.json(model_info)

    st.markdown('<div class="footer">Dibuat dengan ❤️ oleh Kelompok 14 — UTS Praktikum Machine Learning</div>', unsafe_allow_html=True)
