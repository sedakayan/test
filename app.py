import streamlit as st
import pandas as pd
import time
from datetime import date, datetime
import logging

from database import DatabaseManager
from models import Task, Note
from services import TaskService, NoteService

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for plyer to send native OS desktop notifications
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

# Set Page Config
st.set_page_config(
    page_title="Kişisel Dijital Asistan & Üretkenlik Paneli",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database and Services
@st.cache_resource
def get_services():
    db_manager = DatabaseManager()
    task_service = TaskService(db_manager)
    note_service = NoteService(db_manager)
    return task_service, note_service

try:
    task_service, note_service = get_services()
except Exception as e:
    st.error(f"Servisler yüklenirken hata oluştu: {e}")
    logger.error(f"Initialization error: {e}")

# Desktop notification helper
def send_desktop_notification(title, message):
    if PLYER_AVAILABLE:
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Kişisel Dijital Asistan",
                timeout=7
            )
            return True
        except Exception as e:
            logger.error(f"Desktop notification failed: {e}")
            return False
    return False

# Inject Custom CSS for Premium Visual Design (Light Mode, Mint & Baby Blue tones)
st.markdown("""
<style>
    /* Google Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Global Body and Container Styling */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f0f4f2 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #2c3e50;
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.03);
        border-right: 1px solid #e1e9e5;
    }
    
    /* Top Banner Gradient styling */
    .pda-banner {
        background: linear-gradient(135deg, #a8e6cf 0%, #dcedc1 50%, #a8dadc 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 8px 24px rgba(168, 230, 207, 0.2);
    }
    .pda-banner h1 {
        color: #1e5631 !important;
        font-weight: 800 !important;
        margin-bottom: 5px !important;
        font-size: 2.6rem !important;
        text-shadow: 0 2px 4px rgba(255,255,255,0.4);
    }
    .pda-banner p {
        color: #2d6a4f !important;
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        margin-bottom: 0px !important;
    }
    
    /* Metrics Customization */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e3eae7 !important;
        border-radius: 16px !important;
        padding: 18px 24px !important;
        box-shadow: 0 6px 18px rgba(168, 230, 207, 0.12) !important;
        text-align: center !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 28px rgba(168, 230, 207, 0.22) !important;
        border-color: #a8e6cf !important;
    }
    div[data-testid="stMetricValue"] {
        color: #2ecc71 !important;
        font-weight: 700 !important;
        font-size: 2.4rem !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #7f8c8d !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Target the default progress bar color */
    div[role="progressbar"] > div {
        background-image: linear-gradient(to right, #a8e6cf, #2ecc71, #85C1E9) !important;
        height: 12px !important;
        border-radius: 6px !important;
    }

    /* Custom styled Premium Card containers */
    .pda-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.015);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(168, 230, 207, 0.1);
    }
    .pda-card:hover {
        transform: translateY(-5px) scale(1.005);
        box-shadow: 0 14px 32px rgba(0, 0, 0, 0.05);
    }

    /* Color stripes for card left border */
    .task-card-dusuk {
        border-left: 6px solid #a8e6cf !important; /* Mint green */
    }
    .task-card-orta {
        border-left: 6px solid #3498db !important; /* Baby blue */
    }
    .task-card-yuksek {
        border-left: 6px solid #ff8b94 !important; /* Soft red/pink */
    }
    .task-card-completed {
        border-left: 6px solid #bdc3c7 !important; /* Light grey */
        opacity: 0.75;
    }
    .note-card {
        border-left: 6px solid #a8dadc !important; /* Soft baby blue/teal */
    }

    /* Badges styling */
    .pda-badge {
        display: inline-block;
        padding: 4px 12px;
        font-size: 0.72rem;
        font-weight: 700;
        border-radius: 30px;
        margin-right: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-dusuk { background-color: #e8f8f5; color: #2ecc71; }
    .badge-orta { background-color: #ebf5fb; color: #3498db; }
    .badge-yuksek { background-color: #fdf2f2; color: #e74c3c; }
    .badge-completed { background-color: #f2f4f4; color: #7f8c8d; }
    .badge-pending { background-color: #fef9e7; color: #f39c12; }

    /* Custom headers and text */
    .card-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 8px;
        color: #2c3e50;
    }
    .card-desc {
        font-size: 0.98rem;
        color: #5d6d7e;
        margin-bottom: 16px;
        line-height: 1.6;
    }
    .card-meta {
        font-size: 0.82rem;
        color: #95a5a6;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid #f2f6f4;
        padding-top: 12px;
    }

    /* Custom styled tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff !important;
        border: 1px solid #e2eae7 !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        color: #7f8c8d !important;
        transition: all 0.25s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #a8e6cf !important;
        color: #1e8449 !important;
        border-color: #a8e6cf !important;
        box-shadow: 0 6px 15px rgba(168, 230, 207, 0.3) !important;
    }

    /* Pomodoro timer display */
    .pomodoro-container {
        background: #ffffff;
        border-radius: 24px;
        padding: 45px;
        text-align: center;
        box-shadow: 0 12px 30px rgba(168, 230, 207, 0.18);
        border: 2px dashed #a8e6cf;
        max-width: 480px;
        margin: 25px auto;
    }
    .pomodoro-time {
        font-size: 4.8rem;
        font-weight: 700;
        color: #2c3e50;
        font-family: monospace;
        margin: 22px 0;
        letter-spacing: 3px;
    }
    
    /* Input styling */
    div[data-baseweb="input"] {
        border-radius: 8px !important;
    }
    
    /* Styled widgets */
    .stButton>button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton>button:hover {
        background-color: #a8e6cf !important;
        color: #1e8449 !important;
        border-color: #a8e6cf !important;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# App Title & Branding (Premium Banner)
st.markdown("""
<div class="pda-banner">
    <h1>🎯 Kişisel Dijital Asistan</h1>
    <p>Yapay Zeka Destekli Modüler Çalışma ve Üretkenlik Portalı</p>
</div>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE FOR POMODORO & NOTIFICATIONS -----------------
if "timer_seconds" not in st.session_state:
    st.session_state.timer_seconds = 25 * 60
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "timer_paused" not in st.session_state:
    st.session_state.timer_paused = False
if "timer_total_duration" not in st.session_state:
    st.session_state.timer_total_duration = 25 * 60
if "notification_sent" not in st.session_state:
    st.session_state.notification_sent = False

# Fetch current counts for Dashboard Metrics & Progress Bar
try:
    all_tasks = task_service.get_all_tasks()
    total_tasks = len(all_tasks)
    pending_tasks = len(task_service.get_pending_tasks())
    completed_tasks = len(task_service.get_completed_tasks())
except Exception as e:
    total_tasks, pending_tasks, completed_tasks = 0, 0, 0
    all_tasks = []
    st.error(f"Veriler okunurken hata oluştu: {e}")

# 1. AKILLI DASHBOARD METRİKLERİ & İLERLEME ÇUBUĞU
st.markdown("### 📊 Genel Bakış Paneli")
m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric(label="Toplam Görev", value=total_tasks)
m_col2.metric(label="Bekleyen Görev", value=pending_tasks)
m_col3.metric(label="Tamamlanan Görev", value=completed_tasks)

# Canlı İlerleme Çubuğu (Progress Bar)
progress_pct = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
st.write("")
st.markdown(f"**Canlı İlerleme Durumu: %{progress_pct}**")
st.progress(progress_pct / 100)
st.write("")

# 2. AKILLI UYARI SİSTEMİ & MASAÜSTÜ BİLDİRİMİ (DEADLINE ALERT)
try:
    today_urgent_tasks = task_service.get_tasks_due_today()
    tomorrow_urgent_tasks = task_service.get_tasks_due_tomorrow()
    
    has_urgent = bool(today_urgent_tasks or tomorrow_urgent_tasks)
    
    if today_urgent_tasks:
        st.error(f"🚨 **BUGÜN TESLİM EDİLECEK GÖREVLER:** Bugün teslim etmeniz gereken **{len(today_urgent_tasks)}** acil göreviniz bulunmaktadır! Lütfen geciktirmeden tamamlayın.")
        
    if tomorrow_urgent_tasks:
        st.warning(f"⚠️ **YARIN TESLİM EDİLECEK GÖREVLER:** Yarın teslim tarihi olan **{len(tomorrow_urgent_tasks)}** göreviniz bulunuyor. Ön hazırlık yapmayı unutmayın!")
        
    if has_urgent:
        # Trigger automatic desktop notification once per session
        if not st.session_state.notification_sent:
            notif_msg = ""
            if today_urgent_tasks:
                today_titles = ", ".join([t.title for t in today_urgent_tasks[:2]])
                notif_msg += f"Bugün ({len(today_urgent_tasks)}): {today_titles}. "
            if tomorrow_urgent_tasks:
                tomorrow_titles = ", ".join([t.title for t in tomorrow_urgent_tasks[:2]])
                notif_msg += f"Yarın ({len(tomorrow_urgent_tasks)}): {tomorrow_titles}."
                
            if PLYER_AVAILABLE:
                send_desktop_notification(
                    "📅 Yaklaşan Görev Hatırlatıcısı!",
                    notif_msg
                )
                st.session_state.notification_sent = True
        
        # Action button to trigger manual notification demo
        col_notif1, col_notif2 = st.columns([3, 7])
        with col_notif1:
            if PLYER_AVAILABLE:
                if st.button("🔔 Masaüstü Bildirimi Gönder (Demo)", use_container_width=True):
                    notif_msg = ""
                    if today_urgent_tasks:
                        today_titles = ", ".join([t.title for t in today_urgent_tasks[:2]])
                        notif_msg += f"Bugün ({len(today_urgent_tasks)}): {today_titles}. "
                    if tomorrow_urgent_tasks:
                        tomorrow_titles = ", ".join([t.title for t in tomorrow_urgent_tasks[:2]])
                        notif_msg += f"Yarın ({len(tomorrow_urgent_tasks)}): {tomorrow_titles}."
                    
                    send_desktop_notification(
                        "📅 Yaklaşan Görev Hatırlatıcısı!",
                        notif_msg
                    )
                    st.success("Bildirim gönderildi!")
            else:
                st.info("💡 Masaüstü bildirimi almak için cmd ekranına `pip install plyer` yazabilirsiniz.")
except Exception as e:
    logger.error(f"Error checking deadlines or sending notifications: {e}")

# ----------------- TABS SYSTEM -----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Görev Yönetimi", 
    "📓 Kişisel Notlar", 
    "📊 Performans Analizi", 
    "⏱️ Pomodoro Sayacı"
])

# ================= TAB 1: GÖREV YÖNETİMİ =================
with tab1:
    st.markdown("### 📅 Yeni Görev Ekle")
    
    with st.form("task_form", clear_on_submit=True):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            task_title = st.text_input("Görev Başlığı *", placeholder="Örn: Diferansiyel Denklemler Ödevi")
            task_desc = st.text_area("Açıklama", placeholder="Görevin detayları...")
        with col_t2:
            task_category = st.selectbox("Kategori", ["Ders", "Proje", "Kişisel", "Spor", "İş", "Genel"])
            task_priority = st.selectbox("Öncelik Derecesi", ["Düşük", "Orta", "Yüksek"], index=1)
            task_due_date = st.date_input("Son Teslim Tarihi", value=date.today())
            
        submitted_task = st.form_submit_button("➕ Görevi Ekle")
        if submitted_task:
            if not task_title.strip():
                st.error("Görev başlığı boş bırakılamaz.")
            else:
                try:
                    new_task = Task(
                        title=task_title,
                        description=task_desc,
                        category=task_category,
                        due_date=task_due_date,
                        priority=task_priority,
                        status="Bekliyor"
                    )
                    if task_service.add_task(new_task):
                        st.success(f"'{task_title}' başarıyla eklendi!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Görev eklenirken veritabanı hatası oluştu.")
                except Exception as e:
                    st.error(f"Hata: {e}")

    st.markdown("---")
    st.markdown("### 📋 Görev Listesi")
    
    # Filter options
    filter_status = st.radio("Gösterilecek Görevler:", ["Hepsi", "Sadece Bekleyenler", "Sadece Tamamlananlar"], horizontal=True)
    
    # Filter data based on radio choice
    filtered_tasks = []
    if filter_status == "Hepsi":
        filtered_tasks = all_tasks
    elif filter_status == "Sadece Bekleyenler":
        filtered_tasks = [t for t in all_tasks if t.status == "Bekliyor"]
    else:
        filtered_tasks = [t for t in all_tasks if t.status == "Tamamlandı"]

    if not filtered_tasks:
        st.info("Gösterilecek görev bulunamadı.")
    else:
        for task in filtered_tasks:
            # Color code priority and status
            priority_cls = f"task-card-{task.priority.lower()}"
            if task.status == "Tamamlandı":
                priority_cls = "task-card-completed"
            
            # Formulate Card HTML
            card_html = f"""
            <div class="pda-card {priority_cls}">
                <div class="card-meta" style="border-top: none; padding-top: 0; padding-bottom: 8px; border-bottom: 1px solid #f2f6f4; margin-bottom: 10px;">
                    <span class="pda-badge badge-{task.priority.lower()}">{task.priority} Öncelik</span>
                    <span class="pda-badge badge-{'completed' if task.status == 'Tamamlandı' else 'pending'}">{task.status}</span>
                </div>
                <div class="card-title">{task.title}</div>
                <p class="card-desc">{task.description if task.description else 'Açıklama belirtilmedi.'}</p>
                <div class="card-meta">
                    <span>📂 Kategori: <b>{task.category}</b></span>
                    <span>📅 Son Teslim: <b>{task.due_date if task.due_date else 'Belirtilmedi'}</b></span>
                </div>
            </div>
            """
            
            col_card, col_actions = st.columns([8, 2])
            with col_card:
                st.markdown(card_html, unsafe_allow_html=True)
            with col_actions:
                st.write("")  # alignment spacing
                st.write("")
                if task.status == "Bekliyor":
                    if st.button("✅ Tamamla", key=f"comp_{task.id}", use_container_width=True):
                        try:
                            if task_service.complete_task(task.id):
                                st.success("Tamamlandı!")
                                time.sleep(0.5)
                                st.rerun()
                        except Exception as e:
                            st.error(f"Hata: {e}")
                            
                if st.button("🗑️ Sil", key=f"del_task_{task.id}", use_container_width=True):
                    try:
                        if task_service.delete_task(task.id):
                            st.warning("Silindi!")
                            time.sleep(0.5)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Hata: {e}")

# ================= TAB 2: KİŞİSEL NOTLAR =================
with tab2:
    st.markdown("### 📓 Yeni Not Ekle")
    
    with st.form("note_form", clear_on_submit=True):
        note_title = st.text_input("Not Başlığı *", placeholder="Örn: Proje Sunum Fikirleri")
        note_content = st.text_area("İçerik", placeholder="Notunuzu buraya yazın...")
        note_category = st.selectbox("Not Kategorisi", ["Ders", "Proje", "Kişisel", "İş", "Genel"], key="note_cat")
        
        submitted_note = st.form_submit_button("💾 Notu Kaydet")
        if submitted_note:
            if not note_title.strip():
                st.error("Not başlığı boş bırakılamaz.")
            else:
                try:
                    new_note = Note(
                        title=note_title,
                        content=note_content,
                        category=note_category
                    )
                    if note_service.add_note(new_note):
                        st.success("Not kaydedildi!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Not kaydedilirken veritabanı hatası oluştu.")
                except Exception as e:
                    st.error(f"Hata: {e}")

    st.markdown("---")
    st.markdown("### 🗒️ Kayıtlı Notlarım")
    
    try:
        all_notes = note_service.get_all_notes()
    except Exception as e:
        all_notes = []
        st.error(f"Notlar alınırken hata oluştu: {e}")
        
    if not all_notes:
        st.info("Kayıtlı notunuz bulunmamaktadır.")
    else:
        for note in all_notes:
            note_html = f"""
            <div class="pda-card note-card">
                <div class="card-meta" style="border-top: none; padding-top: 0; padding-bottom: 8px; border-bottom: 1px solid #f2f6f4; margin-bottom: 10px;">
                    <span class="pda-badge badge-orta">{note.category}</span>
                    <span>🕒 {note.created_at}</span>
                </div>
                <div class="card-title">{note.title}</div>
                <p class="card-desc" style="white-space: pre-line;">{note.content}</p>
            </div>
            """
            
            col_note_card, col_note_actions = st.columns([8, 2])
            with col_note_card:
                st.markdown(note_html, unsafe_allow_html=True)
            with col_note_actions:
                st.write("")
                st.write("")
                if st.button("🗑️ Sil", key=f"del_note_{note.id}", use_container_width=True):
                    try:
                        if note_service.delete_note(note.id):
                            st.warning("Silindi!")
                            time.sleep(0.5)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Hata: {e}")

# ================= TAB 3: PERFORMANS ANALİZİ =================
with tab3:
    st.markdown("### 📊 Grafiksel Performans Analizi")
    
    if total_tasks == 0:
        st.info("Performans analizi için henüz görev eklenmemiş.")
    else:
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("#### 🔄 Görev Tamamlama Oranı")
            status_counts = {"Durum": ["Bekliyor", "Tamamlandı"], "Adet": [pending_tasks, completed_tasks]}
            df_status = pd.DataFrame(status_counts)
            
            st.bar_chart(df_status.set_index("Durum"), color="#a8e6cf")
            
        with col_g2:
            st.markdown("#### 📂 Kategorilere Göre Görev Dağılımı")
            categories = [t.category for t in all_tasks]
            cat_counts = pd.Series(categories).value_counts()
            df_cat = pd.DataFrame({"Kategori": cat_counts.index, "Adet": cat_counts.values})
            
            st.area_chart(df_cat.set_index("Kategori"), color="#85C1E9")

        st.markdown("---")
        col_g3, col_g4 = st.columns(2)
        
        with col_g3:
            st.markdown("#### ⚡ Öncelik Seviyesine Göre Görev Dağılımı")
            priorities = [t.priority for t in all_tasks]
            prio_counts = pd.Series(priorities).value_counts()
            df_prio = pd.DataFrame({"Öncelik": prio_counts.index, "Adet": prio_counts.values})
            st.bar_chart(df_prio.set_index("Öncelik"), color="#ff8b94")
            
        with col_g4:
            st.markdown("#### 💡 Verimlilik Tavsiyeleri")
            if progress_pct == 0:
                st.warning("Henüz hiç görev tamamlamadınız. Küçük bir adımla başlamaya ne dersiniz?")
            elif progress_pct < 50:
                st.info("İlerleme durumunuz iyi yolda ama daha fazlasını yapabilirsiniz. Pomodoro sayacını kullanarak odaklanma sürenizi artırabilirsiniz.")
            elif progress_pct < 80:
                st.success("Harika! Görevlerinizin çoğunu tamamladınız. Bu yüksek disiplinli çalışmanızı tebrik ederiz.")
            else:
                st.balloons()
                st.success("Mükemmel Performans! Görevlerinizin neredeyse tamamını bitirdiniz. Tam bir verimlilik ustasısınız! 🎉")

# ================= TAB 4: POMODORO ODALANMA SAYACI =================
with tab4:
    st.markdown("### ⏱️ Pomodoro Odaklanma Zamanlayıcısı")
    
    # Duration setting
    duration_minutes = st.slider("Odaklanma Süresi (Dakika)", min_value=1, max_value=120, value=25)
    
    p_col1, p_col2, p_col3 = st.columns(3)
    
    # Start button
    if p_col1.button("▶️ Başlat", use_container_width=True):
        if not st.session_state.timer_paused:
            st.session_state.timer_total_duration = duration_minutes * 60
            st.session_state.timer_seconds = duration_minutes * 60
        st.session_state.timer_running = True
        st.session_state.timer_paused = False
        st.rerun()
        
    # Pause button
    if p_col2.button("⏸️ Duraklat", use_container_width=True):
        st.session_state.timer_running = False
        st.session_state.timer_paused = True
        st.rerun()
        
    # Reset button
    if p_col3.button("🔄 Sıfırla", use_container_width=True):
        st.session_state.timer_running = False
        st.session_state.timer_paused = False
        st.session_state.timer_seconds = duration_minutes * 60
        st.rerun()

    # Container to display countdown
    timer_placeholder = st.empty()

    if st.session_state.timer_running and st.session_state.timer_seconds > 0:
        # Loop and sleep to animate countdown
        while st.session_state.timer_seconds > 0 and st.session_state.timer_running:
            mins, secs = divmod(st.session_state.timer_seconds, 60)
            timer_placeholder.markdown(f"""
            <div class="pomodoro-container" style="border-color: #2ecc71;">
                <h3 style="color: #2ecc71;">🎯 Odaklanma Modu Aktif</h3>
                <div class="pomodoro-time">{mins:02d}:{secs:02d}</div>
                <p style="color: #27ae60; font-weight: bold;">Zihnini odakla, süre akıyor...</p>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1)
            st.session_state.timer_seconds -= 1
            
        if st.session_state.timer_seconds == 0:
            st.session_state.timer_running = False
            st.session_state.timer_paused = False
            st.balloons()
            st.success("🎉 Odaklanma Seansı Tamamlandı! Mola Zamanı!")
            timer_placeholder.markdown(f"""
            <div class="pomodoro-container" style="border-color: #2ecc71; background-color: #f4fdf7;">
                <h3 style="color: #27ae60;">⏰ Süre Doldu!</h3>
                <div class="pomodoro-time" style="color: #2ecc71;">00:00</div>
                <p style="color: #27ae60; font-weight: 700;">☕ Mola Zamanı!</p>
            </div>
            """, unsafe_allow_html=True)
            st.rerun()
    else:
        # Idle or Paused state
        mins, secs = divmod(st.session_state.timer_seconds, 60)
        status_txt = "Zamanlayıcı duraklatıldı." if st.session_state.timer_paused else "Odaklanmaya hazır mısın?"
        timer_placeholder.markdown(f"""
        <div class="pomodoro-container">
            <h3>⏰ Zamanlayıcı</h3>
            <div class="pomodoro-time">{mins:02d}:{secs:02d}</div>
            <p style="color: #7f8c8d;">{status_txt}</p>
        </div>
        """, unsafe_allow_html=True)