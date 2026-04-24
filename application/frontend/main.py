import streamlit as st
import requests

st.set_page_config(page_title="Plant Growth Prediction", page_icon="🌱", layout="wide")

# CSS adjustments untuk UI/UX yang lebih clean dan modern
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 8px;
        height: 3rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1b5e20;
        border-color: #1b5e20;
        color: white;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2e7d32;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555555;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

DEFAULT_API_URL = "http://127.0.0.1:8000"

# Sidebar Navigation (BONUS)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1892/1892751.png", width=100)
    st.markdown("## 🌿 Navigasi")
    page = st.radio("Pilih Menu:", ["Dashboard Prediksi", "Info Model"])
    
    st.markdown("---")
    st.markdown("### 🔌 Pengaturan Konfigurasi")
    api_base = st.text_input("Base URL API Backend", value=DEFAULT_API_URL).strip().rstrip("/")
    debug_mode = st.toggle("🛠️ Aktifkan Debug Mode", value=False)
    
    st.markdown("---")
    st.caption(" UTS Praktikum Machine Learning 🎓")

def get_model_info():
    """Mengambil informasi schema fitur dari backend API"""
    try:
        response = requests.get(f"{api_base}/model-info", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

if page == "Dashboard Prediksi":
    # 1. 🎯 Landing Section
    st.markdown('<p class="main-header">Sistem Prediksi Pertumbuhan Tanaman</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Prediksi kecocokan dan risiko pertumbuhan tanaman secara instan berdasarkan kondisi lingkungan dan properti tanah Anda.</p>', unsafe_allow_html=True)

    model_info = get_model_info()
    if not model_info:
        st.error("⚠️ Gagal terhubung ke Backend API. Pastikan server FastAPI sudah berjalan (contoh: localhost:8000).")
        st.stop()

    features = model_info.get("features", [])
    
    # Mapping opsi kategori (berdasarkan requirement model dari /backend/main.py)
    categorical_options = {
        "soil_type": ["sandy", "loam", "clay", "peat", "silt"],
        "moisture_regime": ["dry", "normal", "wet"],
        "thermal_regime": ["cool", "moderate", "hot"],
        "nutrient_balance": ["low", "balanced", "high"],
        "plant_category": ["cereal", "vegetable", "fruit", "legume"],
    }

    # Range value masuk akal untuk slider numerik (min, max, default)
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
        "bulk_density": (0.5, 2.0, 1.2)
    }

    st.markdown("### 🧾 Masukkan Parameter Lingkungan")
    
    # Mengembalikan ke Pilihan B (Full 18 Fitur Autentik)
    # 2. 🧾 Input Form (Interactive)
    with st.form("prediction_form", border=True):
        st.write("Silahkan lengkapi data metrik tanah dan kondisi lingkungan di bawah ini:")
        st.markdown("")
        
        cols = st.columns(3)
        user_data = {}
        
        # Render semua fitur yang diminta backend
        for idx, feat in enumerate(features):
            name = feat.get("name")
            ftype = feat.get("type", "numeric")
            
            col = cols[idx % 3]
            label = name.replace("_", " ").title()
            
            with col:
                if ftype == "categorical":
                    opts = categorical_options.get(name, ["unknown"])
                    user_data[name] = st.selectbox(f"🌿 {label}", options=opts)
                else:
                    min_v, max_v, default_v = slider_ranges.get(name, (0.0, 100.0, 10.0))
                    # Fallback jika ada numerik yg float tapi error karena string, kita pastikan parsing
                    user_data[name] = st.slider(f"📊 {label}", min_value=float(min_v), max_value=float(max_v), value=float(default_v), step=0.1)
                    
        st.markdown("<br>", unsafe_allow_html=True)
        # 3. ⚡ Predict Button
        submit_btn = st.form_submit_button("🧪 Prediksi Sekarang", use_container_width=True)

    if submit_btn:
        with st.spinner("⏳ Menganalisis parameter menggunakan Machine Learning..."):
            payload = {"features": user_data}
            try:
                # 6. 🔌 Integrasi API (POST request)
                response = requests.post(f"{api_base}/predict", json=payload, timeout=20)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.divider()
                    st.subheader("📊 Hasil Prediksi")
                    
                    pred_label = result.get("prediction")
                    
                    # 4. 📊 Output Result Section
                    col_result, col_metrics = st.columns([1.5, 1])
                    
                    with col_result:
                        # Asumsi dari context "predict failure_flag" backend: 1 = Failure, 0 = Success
                        if str(pred_label) in ["1", "true", "True", "failure", "yes"]:
                            st.error("### ⚠️ Tidak Mendukung (Risiko Gagal Tinggi)")
                            st.write("Karakteristik lingkungan dan properti tanah ini **KURANG COCOK** untuk perkembangan tanaman secara optimal. Perlu perlakuan khusus!")
                        else:
                            st.success("### 🎉 Sangat Mendukung (Pertumbuhan Ideal)")
                            st.write("Karakteristik lingkungan dan properti tanah ini **COCOK** untuk perkembangan tanaman secara optimal. Terus pertahankan!")
                            
                    with col_metrics:
                        if "failure_probability" in result:
                            # Menampilkan confidence/probability score
                            prob = float(result["failure_probability"])
                            st.metric(label="Tingkat Risiko (Failure Prob)", value=f"{prob * 100:.1f}%")
                            st.progress(min(max(prob, 0.0), 1.0))
                        
                    # 7. 🧪 Debug Mode
                    if debug_mode:
                        st.markdown("")
                        with st.expander("🛠️ Raw JSON Response (Backend)"):
                            st.json(result)
                            
                else:
                    st.error(f"❌ Error dari API ({response.status_code}): {response.text}")
                    if debug_mode:
                        st.json(payload)
                        
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Gagal mengirim data ke API: {e}")

elif page == "Info Model":
    # BONUS: Info tentang model
    st.title("💡 Tentang Model Prediction")
    st.markdown("Sistem ini didukung oleh Machine Learning yang ditraining khusus untuk menganalisis data agro-environmental (Agro Environmental Dataset).")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Backend Stack:** FastAPI (Python)")
        st.info("**Format Input:** JSON API Payload")
        
    with col2:
        st.success("**Frontend Stack:** Streamlit")
        st.success("**Output ML:** Binary Classification (Failure Flag) & Probabilities")
        
    st.markdown("### Arsitektur Data")
    st.write("Aplikasi akan meminta list spesifikasi fitur dari endpoint `/model-info` secara otomatis pada saat di-run, sehingga form akan menyesuaikan diri dengan versi model yang sedang aktif.")
