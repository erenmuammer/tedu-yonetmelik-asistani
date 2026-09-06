"""belgeler/ klasöründeki metinleri parçalar, embedding'lerini çıkarır ve SQLite'a yazar.

Kullanım: python indeksle.py
Belgeler değişince tekrar çalıştırmak yeterli, tablo baştan yazılıyor.
"""
import time

from asistan import ayarlar, gomme, veritabani
from asistan.parcalama import tum_belgeleri_parcala


def main():
    baslangic = time.time()
    parcalar = tum_belgeleri_parcala()
    print(f"{len(parcalar)} parça bulundu, embedding'ler çıkarılıyor...")
    # parçanın başına belge adı ve madde başlığını da ekliyorum; 16 soruluk
    # testte top-1 isabeti 9'dan 12'ye çıkardı (belge adı soruda geçince eşleşiyor)
    vektorler = gomme.metinleri_gom([f"{p.etiket()}: {p.metin}" for p in parcalar])
    baglanti = veritabani.baglan()
    veritabani.sifirla(baglanti)
    veritabani.ekle(baglanti, parcalar, vektorler)
    print(f"{veritabani.sayi(baglanti)} parça {ayarlar.VERITABANI.name} dosyasına yazıldı "
          f"({time.time() - baslangic:.1f} sn).")


if __name__ == "__main__":
    main()
