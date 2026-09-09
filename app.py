import streamlit as st
import numpy as np
import pandas as pd
import tempfile
import os
import subprocess
import datetime

from enf_core import extract_enf, find_best_match, detect_jump
import db

st.set_page_config(page_title="سَبْر | Sabr", page_icon="🔎", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Tajawal:wght@400;500;700;800&display=swap');

    :root{
        --bg-0:#050a16; --panel:#0c1a33; --panel-2:#10213f;
        --blue:#1f5fc4; --blue-bright:#4d8dff; --blue-soft:#2a3f66;
        --purple:#7c5cff; --purple-soft:#9b7bff;
        --text:#eef2fa; --text-dim:#8ea0c2;
        --border:rgba(255,255,255,0.09);
        --glow: 0 0 40px rgba(124,92,255,0.18);
    }

    html, body, [class*="css"] { font-family: 'Tajawal', 'Inter', sans-serif; }

    .stApp{
        background:
            radial-gradient(ellipse 60% 40% at 20% 0%, rgba(124,92,255,0.18), transparent 60%),
            radial-gradient(ellipse 50% 40% at 85% 15%, rgba(77,141,255,0.16), transparent 55%),
            radial-gradient(ellipse 70% 50% at 50% 100%, rgba(31,95,196,0.10), transparent 60%),
            var(--bg-0);
    }

    .block-container{ max-width: 1180px; padding-top: 1.2rem; padding-left: 2.2rem; padding-right: 2.2rem; }

    h1, h2, h3, p, label, .stMarkdown, span { color: var(--text) !important; }

    /* hero title */
    .sabr-hero{ text-align:center; padding: 22px 0 10px; position:relative; }
    .sabr-hero h1{
        font-size: 56px; font-weight:800; margin:0; letter-spacing:0.5px;
        background: linear-gradient(90deg, #ffffff 8%, var(--blue-bright) 50%, var(--purple-soft) 100%);
        -webkit-background-clip: text; background-clip: text; color: transparent !important;
        filter: drop-shadow(0 0 24px rgba(124,92,255,0.25));
    }
    .sabr-hero p{ color: var(--text-dim) !important; font-size:15px; margin-top:8px; }
    .sabr-hero .tag{
        display:inline-block; margin-top:12px; font-size:11.5px; color:var(--purple-soft);
        border:1px solid rgba(124,92,255,0.35); background:rgba(124,92,255,0.08);
        padding:5px 14px; border-radius:999px; letter-spacing:0.5px;
    }

    /* card-style bordered containers */
    div[data-testid="stVerticalBlockBorderWrapper"]{
        background: linear-gradient(165deg, rgba(255,255,255,0.045), rgba(255,255,255,0.015));
        border: 1px solid var(--border) !important;
        border-radius: 20px !important;
        padding: 18px 18px !important;
        box-shadow: 0 14px 34px rgba(0,0,0,0.30), inset 0 1px 0 rgba(255,255,255,0.04);
        backdrop-filter: blur(10px);
        margin-bottom: 14px !important;
    }
    /* tighten default Streamlit gaps between stacked elements */
    div[data-testid="stVerticalBlock"]{ gap: 0.6rem !important; }
    div[data-testid="element-container"]{ margin-bottom: 0 !important; }

    /* stat / metric cards */
    div[data-testid="stMetric"]{
        background: linear-gradient(165deg, rgba(124,92,255,0.10), rgba(77,141,255,0.04));
        border: 1px solid rgba(124,92,255,0.22);
        border-radius: 16px;
        padding: 12px 16px !important;
        min-height: unset !important;
    }
    div[data-testid="stMetricLabel"]{ color: var(--text-dim) !important; font-size: 12.5px !important; line-height:1.3 !important; }
    div[data-testid="stMetricValue"]{
        color: var(--text) !important; font-weight:800 !important; line-height:1.3 !important;
        background: linear-gradient(90deg, var(--blue-bright), var(--purple-soft));
        -webkit-background-clip: text; background-clip: text; color: transparent !important;
    }
    div[data-testid="stMetricDelta"]{ display:none !important; }

    /* alerts — unify to match dark theme instead of default bright colors */
    div[data-testid="stAlert"]{
        border-radius: 14px !important; backdrop-filter: blur(6px);
        background: rgba(255,255,255,0.045) !important;
        border: 1px solid var(--border) !important;
    }
    div[data-testid="stAlert"] p{ color: var(--text) !important; }
    div[data-testid="stAlert"] svg{ display:none; }

    /* section headers with accent bar */
    h3{ position:relative; padding-right:14px !important; font-size:19px !important; }
    h3::before{
        content:''; position:absolute; right:0; top:4px; bottom:4px; width:4px;
        border-radius:4px; background: linear-gradient(180deg, var(--blue-bright), var(--purple));
    }

    /* buttons */
    .stButton>button{
        background: linear-gradient(90deg, var(--blue), var(--purple));
        color: #fff; border: none; border-radius: 12px;
        padding: 0.6rem 1.5rem; font-weight:700; letter-spacing:0.2px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        box-shadow: 0 6px 18px rgba(124,92,255,0.30);
    }
    .stButton>button:hover{ transform: translateY(-2px); box-shadow: 0 10px 26px rgba(124,92,255,0.42); }
    .stButton>button:active{ transform: translateY(0px); }
    .stButton>button:disabled{ background:#2a3f66; box-shadow:none; opacity:0.6; }

    /* file uploader */
    [data-testid="stFileUploaderDropzone"]{
        background: rgba(255,255,255,0.025) !important;
        border: 1.5px dashed var(--blue-soft) !important;
        border-radius: 16px !important;
    }
    [data-testid="stFileUploaderDropzone"]:hover{ border-color: var(--purple-soft) !important; }

    /* inputs */
    input, .stDateInput input, .stTimeInput input{
        background: rgba(255,255,255,0.045) !important;
        border-radius: 10px !important; color: var(--text) !important;
        border: 1px solid var(--border) !important;
    }

    hr{ border-color: var(--border) !important; }

    ::-webkit-scrollbar{ width:8px; }
    ::-webkit-scrollbar-thumb{ background: var(--blue-soft); border-radius:8px; }

    /* responsive tweaks */
    @media (max-width: 640px){
        .block-container{ padding-left: 0.9rem; padding-right: 0.9rem; }
        .sabr-hero h1{ font-size: 36px; }
        .sabr-hero p{ font-size: 13px; }
        div[data-testid="stMetricValue"]{ font-size: 22px !important; }
    }

    /* force column stacking on narrow/tablet screens — independent of
       Streamlit's own internal breakpoint, so it works reliably on
       iPad and phones alike */
    @media (max-width: 900px){
        div[data-testid="stHorizontalBlock"]{
            flex-direction: column !important;
            gap: 10px !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]{
            width: 100% !important;
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }
    }
    /* sidebar styling to match the dark glass theme */
    section[data-testid="stSidebar"]{
        background: linear-gradient(180deg, #071022, #050a16) !important;
        border-left: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] .sabr-side-logo{
        font-size: 34px; font-weight:800; text-align:center; margin-top:6px;
        background: linear-gradient(90deg, #ffffff 10%, var(--blue-bright) 55%, var(--purple-soft) 100%);
        -webkit-background-clip: text; background-clip: text; color: transparent !important;
    }
    section[data-testid="stSidebar"] .sabr-side-tag{
        text-align:center; font-size:12px; color:var(--text-dim) !important; margin-bottom:18px;
    }
    /* tabs styled like a segmented nav */
    button[data-baseweb="tab"]{
        color: var(--text-dim) !important; font-weight:600 !important; font-size:15px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"]{ color: var(--text) !important; }
    div[data-baseweb="tab-highlight"]{ background: linear-gradient(90deg, var(--blue-bright), var(--purple)) !important; }
    div[data-baseweb="tab-border"]{ background: var(--border) !important; }

    /* overview accent hero card */
    .sabr-accent-card{
        border-radius: 20px; padding: 22px 26px;
        background: linear-gradient(120deg, var(--blue) 0%, var(--purple) 100%);
        box-shadow: 0 16px 34px rgba(124,92,255,0.28);
        margin-bottom: 14px;
    }
    .sabr-accent-card h4{ margin:0 0 6px; font-size:18px; color:#fff !important; font-weight:800; }
    .sabr-accent-card p{ margin:0; color:rgba(255,255,255,0.88) !important; font-size:13.5px; line-height:1.8; }

    /* recent log table */
    div[data-testid="stDataFrame"]{ border-radius: 14px; overflow:hidden; border:1px solid var(--border); }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        """
        <div class="sabr-side-logo">سَبْر</div>
        <div class="sabr-side-tag">ENF · التحقق من الأدلة الرقمية</div>
        """,
        unsafe_allow_html=True,
    )
    total_points = db.archive_count()
    oldest, newest = db.archive_time_range()
    st.metric("نقاط الأرشيف المحفوظة", f"{total_points:,}")
    if total_points > 0:
        span_label = f"{oldest.strftime('%m-%d %H:%M')} → {newest.strftime('%m-%d %H:%M')}"
    else:
        span_label = "لا يوجد بعد"
    st.metric("النطاق الزمني المغطّى", span_label)
    if total_points == 0:
        st.warning("الأرشيف فارغ — ابدئي بتبويب الأرشيف المرجعي.")
    st.divider()
    st.caption("نموذج أولي يثبت المبدأ العلمي — وليس نظامًا معتمدًا رسميًا للاستخدام القضائي الفعلي بعد.")

db_ready = True

tab0, tab1, tab2 = st.tabs(["نظرة عامة", "١. الأرشيف المرجعي", "٢. التحقق من تسجيل"])

# ---------- Tab 0: Overview dashboard ----------
with tab0:
    st.markdown(
        """
        <div class="sabr-accent-card">
            <h4>سَبْر — التحقق من صحة الأدلة الرقمية</h4>
            <p>منصة تبني أرشيفًا مرجعيًا لبصمة الشبكة الكهربائية السعودية، وتقارن به أي تسجيل صوتي
            أو مرئي مشكوك فيه لتحديد أصالته أو كشف أي تلاعب فيه بدقة زمنية.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    v_count = db.verification_count()
    recent = db.get_recent_verifications(1)
    last_result = recent[0][2] if recent else "لا يوجد بعد"

    ov1, ov2, ov3, ov4 = st.columns(4)
    with ov1:
        st.metric("نقاط الأرشيف", f"{total_points:,}")
    with ov2:
        st.metric("النطاق الزمني", span_label if total_points > 0 else "لا يوجد بعد")
    with ov3:
        st.metric("عدد عمليات التحقق", f"{v_count:,}")
    with ov4:
        st.metric("آخر نتيجة", last_result)

    col_chart, col_log = st.columns([3, 2])
    with col_chart:
        with st.container(border=True):
            st.subheader("معاينة الأرشيف")
            if total_points > 0:
                _, preview_freqs = db.load_reference_archive()
                st.line_chart(pd.DataFrame({"التردد (هرتز)": preview_freqs}))
            else:
                st.info("لا توجد بيانات أرشيف بعد — أضيفي تسجيلًا مرجعيًا من التبويب المجاور.")

    with col_log:
        with st.container(border=True):
            st.subheader("آخر عمليات التحقق")
            log_rows = db.get_recent_verifications(6)
            if log_rows:
                log_df = pd.DataFrame(
                    log_rows, columns=["الوقت", "الملف", "النتيجة", "الثقة", "التفاصيل"]
                )
                log_df["الوقت"] = pd.to_datetime(log_df["الوقت"]).dt.strftime("%m-%d %H:%M")
                log_df["الثقة"] = log_df["الثقة"].apply(lambda c: f"{c:.0%}" if pd.notna(c) else "—")
                st.dataframe(
                    log_df[["الوقت", "الملف", "النتيجة", "الثقة"]],
                    hide_index=True, use_container_width=True,
                )
            else:
                st.info("لا توجد عمليات تحقق مسجّلة بعد.")

# ---------- Step 1: reference archive ----------
with tab1:
    with st.container(border=True):
        st.subheader("١. إضافة تسجيل مرجعي جديد للأرشيف")
        st.write("ارفعي مقطع صوت من جهاز التسجيل المستمر، وحدّدي وقت بداية هذا المقطع فعليًا.")

        col1, col2 = st.columns(2)
        with col1:
            ref_date = st.date_input("تاريخ بداية التسجيل", value=datetime.date.today())
        with col2:
            ref_time = st.time_input("وقت بداية التسجيل", value=datetime.time(0, 0))

        ref_file = st.file_uploader("ملف الأرشيف المرجعي (wav/mp3/m4a)", type=["wav", "mp3", "m4a"], key="ref")

        if ref_file is not None and st.button("استخراج وحفظ بالأرشيف الدائم", disabled=not db_ready):
            start_dt = datetime.datetime.combine(ref_date, ref_time)
            raw_suffix = "." + ref_file.name.split(".")[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=raw_suffix) as tmp:
                tmp.write(ref_file.read())
                raw_ref_path = tmp.name

            ref_path = raw_ref_path + "_converted.wav"
            convert_result = subprocess.run(
                ["ffmpeg", "-y", "-i", raw_ref_path, "-ar", "16000", "-ac", "1", ref_path],
                capture_output=True,
            )
            if convert_result.returncode != 0 or not os.path.exists(ref_path):
                st.error(
                    "تعذّر تحويل الملف الصوتي. تأكدي أن الملف سليم وغير تالف، "
                    "وجربي تصدير التسجيل بصيغة WAV مباشرة إن أمكن."
                )
                with st.expander("تفاصيل الخطأ التقنية"):
                    st.code(convert_result.stderr.decode(errors="ignore")[-1500:])
            else:
                with st.spinner("جاري استخراج بصمة ENF وحفظها بقاعدة البيانات الدائمة..."):
                    t, f = extract_enf(ref_path)
                    saved_count = db.save_reference_points(start_dt, t, f)
                st.success(f"تم حفظ {saved_count} نقطة بشكل دائم بقاعدة البيانات — لن تُفقد حتى لو أُعيد تشغيل التطبيق.")
                st.line_chart(pd.DataFrame({"التردد (هرتز)": f}))

            os.unlink(raw_ref_path)
            if os.path.exists(ref_path):
                os.unlink(ref_path)

# ---------- Step 2: video/audio to verify ----------
with tab2:
    with st.container(border=True):
        st.subheader("٢. التسجيل المطلوب التحقق منه")
        suspect_file = st.file_uploader("فيديو أو ملف صوتي للتحقق (mp4/wav/mp3)", type=["mp4", "wav", "mp3", "m4a"], key="suspect")

        if suspect_file is not None and st.button("تحليل والتحقق من الأرشيف الدائم", disabled=not db_ready):
            archive_times, archive_freqs = db.load_reference_archive()

            if len(archive_freqs) == 0:
                st.error("الأرشيف المرجعي فارغ — أضيفي تسجيلًا مرجعيًا أولًا بالخطوة ١.")
            else:
                suffix = "." + suspect_file.name.split(".")[-1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(suspect_file.read())
                    raw_path = tmp.name

                audio_path = raw_path + "_converted.wav"
                convert_result = subprocess.run(
                    ["ffmpeg", "-y", "-i", raw_path, "-ar", "16000", "-ac", "1", "-vn", audio_path],
                    capture_output=True,
                )

                if convert_result.returncode != 0 or not os.path.exists(audio_path):
                    st.error(
                        "تعذّر تحويل الملف المرفوع. تأكدي أن الملف سليم وغير تالف."
                    )
                    with st.expander("تفاصيل الخطأ التقنية"):
                        st.code(convert_result.stderr.decode(errors="ignore")[-1500:])
                    os.unlink(raw_path)
                    st.stop()

                with st.spinner("جاري استخراج بصمة ENF ومقارنتها بالأرشيف الدائم..."):
                    q_times, q_freqs = extract_enf(audio_path)

                st.line_chart(pd.DataFrame({"التردد (هرتز)": q_freqs}))

                jump_idx = detect_jump(q_freqs)

                if jump_idx is None:
                    best_i, confidence = find_best_match(archive_times, archive_freqs, q_freqs)
                    if best_i is not None and confidence > 0.3:
                        matched_start = archive_times[best_i]
                        matched_end = archive_times[min(best_i + len(q_freqs) - 1, len(archive_times) - 1)]
                        st.success(
                            f"✅ التسجيل يبدو أصليًا — درجة الثقة: {confidence:.0%}\n\n"
                            f"الوقت المطابق بالأرشيف: من **{matched_start.strftime('%Y-%m-%d %H:%M:%S')}** "
                            f"إلى **{matched_end.strftime('%Y-%m-%d %H:%M:%S')}**"
                        )
                        db.log_verification(
                            suspect_file.name, "أصلي", confidence,
                            f"{matched_start.strftime('%Y-%m-%d %H:%M:%S')} → {matched_end.strftime('%H:%M:%S')}",
                        )
                    else:
                        st.warning(
                            "لم يُعثر على تطابق قوي بالأرشيف الحالي — "
                            "قد يكون التسجيل من فترة غير مغطاة بالأرشيف بعد، أو بعيدًا عن مصدر كهرباء."
                        )
                        db.log_verification(suspect_file.name, "غير محدد", confidence, "لا يوجد تطابق قوي")
                else:
                    part1 = q_freqs[:jump_idx]
                    part2 = q_freqs[jump_idx:]
                    i1, c1 = find_best_match(archive_times, archive_freqs, part1)
                    i2, c2 = find_best_match(archive_times, archive_freqs, part2)

                    msg = f"⚠️ تم اكتشاف تلاعب محتمل عند النقطة {jump_idx} من التسجيل.\n\n"
                    if i1 is not None:
                        t1_start = archive_times[i1]
                        t1_end = archive_times[min(i1 + len(part1) - 1, len(archive_times) - 1)]
                        msg += f"الجزء الأول يطابق: **{t1_start.strftime('%Y-%m-%d %H:%M:%S')} → {t1_end.strftime('%H:%M:%S')}** (ثقة {c1:.0%})\n\n"
                    if i2 is not None:
                        t2_start = archive_times[i2]
                        msg += f"الجزء الثاني يطابق: بدايةً من **{t2_start.strftime('%Y-%m-%d %H:%M:%S')}** (ثقة {c2:.0%})\n\n"
                    if i1 is not None and i2 is not None:
                        gap = (t2_start - t1_end)
                        msg += f"**الفترة المفقودة (المحذوفة/المدموجة): {gap}**"

                    st.error(msg)
                    avg_conf = np.mean([c for c in [c1, c2] if c is not None]) if (i1 is not None or i2 is not None) else 0.0
                    db.log_verification(suspect_file.name, "متلاعب فيه", float(avg_conf), msg[:200])

                os.unlink(raw_path)
                if audio_path != raw_path:
                    os.unlink(audio_path)
