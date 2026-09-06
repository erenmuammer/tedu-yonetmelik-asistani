"""Projenin tek yerden değiştirilen ayarları."""
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
BELGE_KLASORU = KOK / "belgeler"
VERITABANI = KOK / "yonetmelik.db"

# Foundry Local kataloğundaki model isimleri (alias)
EMBEDDING_MODELI = "qwen3-embedding-0.6b"
CHAT_MODELI = "qwen3-4b"

# Retrieval ayarları
UST_K = 4                 # soru için en fazla kaç parça getirilecek
BENZERLIK_ESIGI = 0.40    # en iyi parça bile bunun altındaysa modele hiç sormuyoruz
MAKS_PARCA_UZUNLUGU = 1200  # karakter; daha uzun maddeler fıkralardan bölünüyor

# Dosya adından okunabilir belge adına
BELGE_ADLARI = {
    "lisans-egitim-ogretim-yonetmeligi": "Lisans Eğitim-Öğretim Yönetmeliği",
    "staj-yonergesi": "Staj Yönergesi",
    "burs-yonergesi": "Burs Yönergesi",
    "yatay-gecis-yonergesi": "Yatay Geçiş Yönergesi",
    "yandal-yonergesi": "Yandal Programı Yönergesi",
    "yaz-ogretimi-yonergesi": "Yaz Öğretimi Yönergesi",
    "ingilizce-dil-okulu-yonergesi": "İngilizce Dil Okulu Yönergesi",
}
