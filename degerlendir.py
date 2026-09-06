"""Test sorularını sırayla sorup sonuçları docs/test_sonuclari.md dosyasına yazar.

    python degerlendir.py

Sorular üç türde: belgelerde cevabı olanlar, olmayanlar ve uç durumlar.
"""
import datetime
import time
from pathlib import Path

from asistan import ayarlar
from asistan.arama import Arama
from asistan.cevap import cevapla

SORULAR = [
    ("Zorunlu staj en az kaç iş günü sürer?", "belgede var"),
    ("Stajımı yurt dışında yapabilir miyim?", "belgede var"),
    ("Başarı bursu nasıl kazanılır?", "belgede var"),
    ("Not ortalamam düşükse bursum kesilir mi?", "belgede var"),
    ("Yaz okulunda en fazla kaç ders alabilirim?", "belgede var"),
    ("Yandal programından hangi durumda çıkarılırım?", "belgede var"),
    ("Yatay geçiş başvurusu ne zaman ve nereye yapılır?", "belgede var"),
    ("İngilizce yeterlik sınavından kaç almam gerekiyor?", "belgede var"),
    ("Sınav sonucuna nasıl itiraz ederim?", "belgede var"),
    ("Mezuniyet için genel not ortalaması en az kaç olmalı?", "belgede var"),
    ("Kaç dönem izin alabilirim?", "belgede var"),
    ("Kayıt dondurma en fazla kaç dönem yapılabilir?", "belgede var ama farklı terimle ('izin')"),
    ("Derse devam zorunluluğu yüzde kaç?", "belgede net değil"),
    ("Kampüste yemekhane fiyatları ne kadar?", "belgede yok"),
    ("Python'da bir liste nasıl sıralanır?", "belgede yok"),
    ("Bugün Ankara'da hava nasıl?", "belgede yok"),
    ("Merhaba, nasılsın?", "belgede yok"),
    ("staj", "tek kelime"),
    ("Yönetmelik ne diyor?", "çok genel soru"),
]


def main():
    arama = Arama()
    satirlar = [f"# Test sonuçları\n",
                f"Tarih: {datetime.date.today():%d.%m.%Y} · Model: `{ayarlar.CHAT_MODELI}` · "
                f"Embedding: `{ayarlar.EMBEDDING_MODELI}` · top-k {ayarlar.UST_K} · eşik {ayarlar.BENZERLIK_ESIGI}\n",
                "Bu dosya `python degerlendir.py` ile üretildi; cevaplar elle düzenlenmedi.\n"]
    sureler = []
    for soru, beklenti in SORULAR:
        baslangic = time.time()
        sonuclar = arama.ara(soru)
        cevap = cevapla(soru, sonuclar)
        sure = time.time() - baslangic
        sureler.append(sure)
        kaynaklar = "; ".join(f"{s.parca.etiket()} ({s.benzerlik:.2f})" for s in sonuclar[:3])
        satirlar += [f"\n## {soru}\n", f"*Beklenti:* {beklenti} · *süre:* {sure:.1f} sn  ",
                     f"*En yakın parçalar:* {kaynaklar}\n", "> " + cevap.replace("\n", "\n> ") + "\n"]
        print(f"{sure:5.1f} sn  {soru}")
    satirlar.append(f"\nOrtalama süre: {sum(sureler) / len(sureler):.1f} sn ({len(SORULAR)} soru)\n")
    cikti = Path("docs") / "test_sonuclari.md"
    cikti.parent.mkdir(exist_ok=True)
    cikti.write_text("\n".join(satirlar), encoding="utf-8")
    print(f"{cikti} yazıldı.")


if __name__ == "__main__":
    main()
