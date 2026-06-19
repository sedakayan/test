"""
models.py
Bu modül, uygulamada kullanılacak temel Nesne Yönelimli Programlama (OOP) 
sınıflarını (Gorev ve Not) barındırır.
"""

class Gorev:
    """
    Kullanıcının günlük görevlerini temsil eden sınıf.
    """
    def __init__(self, id=None, baslik="", aciklama="", durum="Tamamlanmadı", tarih=""):
        self.id = id                  # Veritabanındaki benzersiz numara
        self.baslik = baslik          # Görevin adı
        self.aciklama = aciklama      # Görevin detayları
        self.durum = durum            # 'Tamamlandı' veya 'Tamamlanmadı'
        self.tarih = tarih            # Görevin yapılacağı tarih

    def __str__(self):
        return f"Görev: {self.baslik} [{self.durum}] - Tarih: {self.tarih}"


class Not:
    """
    Kullanıcının tuttuğu kişisel notları temsil eden sınıf.
    """
    def __init__(self, id=None, baslik="", icerik="", olusturma_tarihi=""):
        self.id = id                            # Veritabanındaki benzersiz numara
        self.baslik = baslik                    # Notun başlığı
        self.icerik = icerik                    # Notun detaylı içeriği
        self.olusturma_tarihi = olusturma_tarihi  # Notun kaydedildiği an

    def __str__(self):
        return f"Not: {self.baslik} ({self.olusturma_tarihi})"