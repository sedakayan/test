"""
app.py
Bu modül, uygulamanın Streamlit tabanlı kullanıcı arayüzünü (Frontend) 
ve API entegrasyonlarını barındıran ana program dosyasıdır.
"""
import streamlit as st
import requests
from datetime import datetime
import json

# Diğer modüllerden fonksiyonları ve sınıfları çağırıyoruz (Modüler Yapı)
from models import Gorev, Not
import database

# Uygulama başladığında veritabanını otomatik hazırla
database.veritabanini_hazirla()

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Kişisel Dijital Asistan", page_icon="🤖", layout="wide")

# --- API ENTEGRASYONU ---
def motivasyon_sozu_getir():
    """API üzerinden her açılışta rastgele bir motivasyon sözü çeker."""
    try:
        # İnternet olmasa bile programın çökmesi engellenir
        response = requests.get("https://api.quotable.io/random?tags=inspirational", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return f'"{data["content"]}" — *{data["author"]}*'
    except:
        pass
    return '"Bugün harika bir gün, planlarını gerçekleştirmek için harika bir fırsat!"'

# --- YAN MENÜ (SIDEBAR) ---
st.sidebar.title("🤖 Dijital Asistan")
st.sidebar.write("Zamanınızı ve notlarınızı düzenleyin.")
menu = st.sidebar.radio("Gitmek İstediğiniz Bölüm:", ["📅 Günlük Planım", "✅ Görev Yönetimi", "📝 Notlarım"])

# --- MENÜ İÇERİKLERİ ---

# 1. SEKME: GÜNLÜK PLANIM (ANA SAYFA)
if menu == "📅 Günlük Planım":
    st.title("📅 Günlük Planım & Genel Durum")
    st.info(motivasyon_sozu_getir())
    
    bugun = datetime.now().strftime("%Y-%m-%d")
    st.subheader(f"Bugünün Tarihi: {bugun}")
    
    tum_gorevler = database.gorevleri_getir()
    bugunun_gorevleri = [g for g in tum_gorevler if g.tarih == bugun]
    
    if not bugunun_gorevleri:
        st.write("🎉 Bugün için planlanmış bir göreviniz görünmüyor!")
    else:
        for g in bugunun_gorevleri:
            durum_emoji = "✅" if g.durum == "Tamamlandı" else "⏳"
            st.write(f"{durum_emoji} **{g.baslik}** - {g.aciklama}")

# 2. SEKME: GÖREV YÖNETİMİ
elif menu == "✅ Görev Yönetimi":
    st.title("✅ Görev Yönetimi")
    st.subheader("➕ Yeni Görev Ekle")
    
    with st.form("yeni_gorev_formu", clear_on_submit=True):
        baslik = st.text_input("Görev Başlığı (*)")
        aciklama = st.text_area("Görev Açıklaması")
        tarih = st.date_input("Planlanan Tarih", value=datetime.now())
        gonder = st.form_submit_with_button("Görev Kaydet")
        
        if gonder:
            if not baslik.strip():
                st.error("Hata: Görev başlığı boş bırakılamaz!")
            else:
                yeni_gorev = Gorev(baslik=baslik, aciklama=aciklama, tarih=str(tarih))
                if database.gorev_ekle(yeni_gorev):
                    st.success("Görev başarıyla veritabanına kaydedildi!")
                    st.rerun()

    st.markdown("---")
    st.subheader("📋 Mevcut Görevleriniz")
    gorevler = database.gorevleri_getir()
    
    if not gorevler:
        st.info("Henüz hiç görev eklememişsiniz.")
    else:
        for g in gorevler:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{g.baslik}** ({g.tarih}) — *{g.aciklama}*")
                st.caption(f"Mevcut Durum: {g.durum}")
            with col2:
                if g.durum == "Tamamlanmadı":
                    if st.button("Tamamla", key=f"comp_{g.id}"):
                        database.gorev_durum_guncelle(g.id, "Tamamlandı")
                        st.rerun()
                else:
                    if st.button("Geri Al", key=f"uncomp_{g.id}"):
                        database.gorev_durum_guncelle(g.id, "Tamamlanmadı")
                        st.rerun()
            with col3:
                if st.button("❌ Sil", key=f"del_{g.id}"):
                    database.gorev_sil(g.id)
                    st.rerun()

# 3. SEKME: NOTLARIM
elif menu == "📝 Notlarım":
    st.title("📝 Notlarım")
    col_sol, col_sag = st.columns([2, 3])
    
    with col_sol:
        st.subheader("➕ Yeni Not Yaz")
        not_baslik = st.text_input("Not Başlığı (*)")
        not_icerik = st.text_area("Not İçeriği")
        if st.button("Notu Kaydet"):
            if not not_baslik.strip():
                st.error("Hata: Not başlığı boş olamaz!")
            else:
                su_an = datetime.now().strftime("%Y-%m-%d %H:%M")
                yeni_not = Not(baslik=not_baslik, icerik=not_icerik, olusturma_tarihi=su_an)
                if database.not_ekle(yeni_not):
                    st.success("Notunuz başarıyla kaydedildi!")
                    st.rerun()
    
    with col_sag:
        st.subheader("📚 Kayıtlı Notlar")
        notlar = database.notlari_getir()
        
        if not notlar:
            st.info("Kayıtlı not bulunmuyor.")
        else:
            # JSON Olarak Dışa Aktarma
            not_sozlukleri = [{"baslik": n.baslik, "icerik": n.icerik, "tarih": n.olusturma_tarihi} for n in notlar]
            json_string = json.dumps(not_sozlukleri, ensure_ascii=False, indent=4)
            
            st.download_button(
                label="📥 Tüm Notları JSON Olarak İndir",
                data=json_string,
                file_name="notlarim_yedek.json",
                mime="application/json"
            )
            st.markdown("---")
            for n in notlar:
                with st.expander(f"📌 {n.baslik} ({n.olusturma_tarihi})"):
                    st.write(n.icerik)