"""Soruya en yakın madde parçalarını bulur.

Bütün vektörler bellekte tek bir matris; soru vektörüyle çarpınca cosine
benzerlikleri çıkıyor (vektörler normalize olduğu için nokta çarpım yetiyor).
"""
import re
from dataclasses import dataclass

import numpy as np

from asistan import ayarlar, gomme, veritabani
from asistan.parcalama import Parca


# Öğrencilerin kullandığı bazı kelimeler yönetmelikte başka türlü geçiyor;
# "kayıt dondurma" diye sorunca embedding "izin" maddesini bulamıyordu.
ES_ANLAMLILAR = {
    r"\bkayıt dondur": "izinli sayılma, izin",
    r"\bdondur": "izin",
    r"\bçap\b": "çift anadal",
    r"\bgno\b": "genel not ortalaması",
    r"\bhazırlık": "İngilizce dil okulu",
    r"\bdevamsızlık": "derse devam",
}


def soruyu_genislet(soru: str) -> str:
    """Soruya yönetmelikteki karşılık kelimeleri parantez içinde ekler."""
    ekler = [v for k, v in ES_ANLAMLILAR.items() if re.search(k, soru.lower())]
    return f"{soru} ({', '.join(ekler)})" if ekler else soru


@dataclass
class Sonuc:
    parca: Parca
    benzerlik: float


def en_yakinlar(matris: np.ndarray, soru_vektoru: np.ndarray, ust_k: int) -> list[tuple[int, float]]:
    """(indeks, benzerlik) listesi, en benzerden başlayarak."""
    benzerlikler = matris @ soru_vektoru
    sira = np.argsort(-benzerlikler)[:ust_k]
    return [(int(i), float(benzerlikler[i])) for i in sira]


def yeterli_mi(sonuclar: list[Sonuc], esik: float = ayarlar.BENZERLIK_ESIGI) -> bool:
    """En iyi parça bile eşiğin altındaysa soru belgelerin dışında demektir."""
    return bool(sonuclar) and sonuclar[0].benzerlik >= esik


class Arama:
    def __init__(self, baglanti=None):
        self.parcalar, self.matris = veritabani.hepsini_oku(baglanti or veritabani.baglan())
        if not self.parcalar:
            raise SystemExit("Veritabanı boş. Önce `python indeksle.py` çalıştırın.")

    def ara(self, soru: str, ust_k: int = ayarlar.UST_K) -> list[Sonuc]:
        vektor = gomme.soruyu_gom(soruyu_genislet(soru))
        return [Sonuc(self.parcalar[i], b) for i, b in en_yakinlar(self.matris, vektor, ust_k)]
