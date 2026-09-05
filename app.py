import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. ضبط إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="سَبْر | SABR Forensic Platform",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. حقن أنماط CSS لتحقيق مظهر Glassmorphism النيوني البنفسجي
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* خلفية المنصة الأساسية */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #150f28 0%, #090710 90%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #E2E8F0 !important;
    }

    /* الشريط الجانبي الزجاجي */
    [data-testid="stSidebar"] {
        background: rgba(18, 14, 33, 0.65) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(139, 92, 246, 0.15) !important;
    }

    /* كروت Glassmorphism التفاعلية */
    .glass-card {
        background: linear-gradient(135deg, rgba(30, 24, 54, 0.65) 0%, rgba(18, 14, 35, 0.45) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(168, 85, 247, 0.18);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 10px 35px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 20px;
    }
    .glass-card:hover {
        border-color: rgba(168, 85, 247, 0.45);
        box-shadow: 0 15px 40px -10px rgba(139, 92, 246, 0.25);
        transform: translateY(-2px);
    }

    /* بطاقات المؤشرات المصغرة (Metrics) */
    .metric-badge {
        display: inline-flex;
        padding: 6px 12px;
        border-radius: 9999px;
        background: rgba(168, 85, 247, 0.15);
        border: 1px solid rgba(168, 85, 247, 0.3);
        color: #C084FC;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FFFFFF 0%, #D8B4FE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 8px 0 4px 0;
    }
    .metric-label {
        color: #94A3B8;
        font-size: 0.85rem;
        font-weight: 500;
    }

    /* الأزرار النيونية البنفسجية */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4) !important;
        transition: all 0.25s ease !important;
    }
    .stButton>button:hover {
        opacity: 0.9 !important;
        box-shadow: 0 6px 25px rgba(139, 92, 246, 0.6) !important;
        transform: scale(1.01);
    }

    /* نافذة رفع الملفات */
    [data-testid="stFileUploader"] {
        background: rgba(22, 17, 40, 0.45) !important;
        border: 1.5px dashed rgba(168, 85, 247, 0.35) !important;
        border-radius: 18px !important;
        padding: 18px !important;
        backdrop-filter: blur(10px) !important;
    }

    /* إخفاء الزوائد الافتراضية لمنح الشاشة مساحة إضافية */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px;
    }
</style>
""", unsafe_allow_html=True)

# 3. القائمة الجانبية (Sidebar)
with st.sidebar:
    st.markdown("""
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:2rem;">
            <div style="width:40px; height:40px; border-radius:12px; background:linear-gradient(135deg, #8B5CF6, #6366F1); display:flex; align-items:center; justify-content:center; box-shadow:0 0 15px rgba(139,92,246,0.6);">
                ⚡
            </div>
            <div>
                <h2 style="margin:0; font-size:1.3rem; font-weight:700; color:#fff;">سَبْر للأدلة</h2>
                <span style="font-size:0.75rem; color:#A78BFA;">محرك تحليل ENF</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    mode = st.radio("القائمة الرئيسية", ["لوحة الفحص", "سجل القضايا", "مقارنة الترددات", "الإعدادات"], index=0)
    
    st.markdown("---")
    st.markdown("<div class='metric-label'>تردد الشبكة المرجعي</div>", unsafe_allow_html=True)
    target_freq = st.selectbox("", ["60 Hz (السعودية / أمريكا)", "50 Hz (الخليج / أوروبا)"])
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="glass-card" style="padding:16px;">
            <div style="font-size:0.8rem; color:#94A3B8;">حالة النظام</div>
            <div style="color:#34D399; font-size:0.9rem; font-weight:600; margin-top:4px;">● محرك المعالجة جاهز</div>
        </div>
    """, unsafe_allow_html=True)

# 4. الرأس العلوي (Header)
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown("""
        <h1 style="margin:0; font-size:2.2rem; font-weight:700; background:linear-gradient(135deg, #fff 40%, #A78BFA 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            منصة سَبْر للتحقيق الجنائي الرقمي
        </h1>
        <p style="color:#94A3B8; margin-top:6px; font-size:0.95rem;">
            استخراج وتحليل البصمة الكهربائية (ENF) للتحقق من سلامة الأدلة الصوتية والمرئية.
        </p>
    """, unsafe_allow_html=True)
with col_head2:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.button("+ فحص ملف جديد")

# 5. بطاقات المؤشرات العلوية (Top KPI Cards)
col1, col2, col3, col4 = st.columns(4)
metrics = [
    ("إجمالي الأدلة", "1,284", "+12% هذا الأسبوع"),
    ("قيد المعالجة", "4", "تحديث فوري"),
    ("عينات تم إثباتها", "98.6%", "مطابقة عالية"),
    ("شبهات تلاعب", "18", "تحتاج مراجعة")
]

for col, (label, val, sub) in zip([col1, col2, col3, col4], metrics):
    with col:
        st.markdown(f"""
            <div class="glass-card">
                <span class="metric-badge">System KPI</span>
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
                <div style="color:#A78BFA; font-size:0.75rem; margin-top:6px;">{sub}</div>
            </div>
        """, unsafe_allow_html=True)

# 6. قسم رفع الملفات والرسم البياني
main_col, side_col = st.columns([2.2, 1])

with main_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin-top:0; font-size:1.1rem; color:#fff;">مخطط تذبذب التردد اللحظي (ENF Live Curve)</h3>', unsafe_allow_html=True)
    
    # رسم بياني لمحاكاة منحنى ENF لوني بنفسجي ناصع
    x = np.linspace(0, 60, 200)
    base_freq = 60.0 if "60" in target_freq else 50.0
    noise = np.sin(x/4) * 0.03 + np.random.normal(0, 0.005, len(x))
    # إحداث هبوط مصطنع لمحاكاة شبهة تلاعب عند الثانية 40
    noise[130:140] -= 0.05
    y = base_freq + noise

    fig = go.Figure()
    # مساحة التوهج النيون
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='lines',
        line=dict(color='#8B5CF6', width=3, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(139, 92, 246, 0.12)'
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=15, b=10),
        height=320,
        xaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', title='الزمن (بالثواني)', tickfont=dict(color='#94A3B8')),
        yaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', title='التردد (Hz)', tickfont=dict(color='#94A3B8')),
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with side_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin-top:0; font-size:1.1rem; color:#fff;">رفع الدليل الرقمي</h3>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["wav", "mp3", "mp4"])
    
    if uploaded_file:
        st.markdown(f"""
            <div style="background:rgba(139,92,246,0.15); border:1px solid #8B5CF6; border-radius:12px; padding:12px; margin:12px 0;">
                <div style="font-size:0.85rem; font-weight:600; color:#fff;">{uploaded_file.name}</div>
                <div style="font-size:0.75rem; color:#C084FC;">جاهز للمعالجة والاستخراج الجنائي</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("بدء فحص البصمة"):
            st.success("تم عزل الإشارة الكهربائية بنجاح!")
    else:
        st.markdown("<div style='font-size:0.8rem; color:#64748B; text-align:center; padding:15px 0;'>اسحب الملف هنا بصيغة WAV أو MP4</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 7. التقرير وسلسلة الحيازة
st.markdown("""
    <div class="glass-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h4 style="margin:0; color:#fff;">سلسلة الحيازة والتقرير الأمني (Chain of Custody)</h4>
                <p style="margin:4px 0 0 0; font-size:0.8rem; color:#94A3B8;">SHA-256: 8f4a2b90c1e8a93e54b67d14238e92fa07b46d5c19208a3d84f932e65</p>
            </div>
            <div class="metric-badge" style="background:rgba(52, 211, 153, 0.15); border-color:#34D399; color:#34D399;">
                دليل سليم وموثّق
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)
