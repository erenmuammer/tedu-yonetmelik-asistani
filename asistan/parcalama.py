"""Yönetmelik metnini madde madde parçalara ayırır.

pdftotext çıktısında her sayfanın başında belge başlığı, doküman numarası ve
sayfa numarası tekrar ediyor. Önce bunlar ayıklanıyor, sonra metin
"MADDE 5 –" gibi madde başlıklarından bölünüyor. Bir madde çok uzunsa
fıkra sınırlarından ((1), (2) ...) küçük parçalara ayrılıyor.

Paragraf uzunluğuna göre bölmeyi de denedim ama madde ortasından kesince
retrieval belirgin şekilde kötüleşiyordu; yönetmelik gibi metinlerde doğal
birim madde.
"""
import re
from dataclasses import dataclass
from pathlib import Path

from asistan import ayarlar

MADDE_DESENI = re.compile(r"^(GEÇİCİ\s+)?MADDE\s+(\d+)\s*[–:-]?\s*(.*)$", re.IGNORECASE)
BOLUM_DESENI = re.compile(r"^[A-ZÇĞİÖŞÜ]+\s+BÖLÜM$")
FIKRA_DESENI = re.compile(r"(?=\(\d+\)\s)")
SAYFA_AYRACI = "\f"
GURULTU = ("TASNİF DIŞI", "Doküman No", "KYS-YN-", "Sayfa No")


@dataclass
class Parca:
    kaynak: str   # belge adı
    madde: str    # "Madde 12" ya da "Geçici Madde 1"
    baslik: str   # maddenin hemen üstündeki kısa başlık, yoksa boş
    metin: str

    def etiket(self) -> str:
        return f"{self.kaynak}, {self.madde}" + (f" ({self.baslik})" if self.baslik else "")


def sayfa_basliklarini_temizle(metin: str) -> list[str]:
    """Sayfa başlarında tekrar eden satırları ve doküman bilgilerini atar."""
    sayfalar = metin.split(SAYFA_AYRACI)
    sayac: dict[str, int] = {}
    for sayfa in sayfalar:
        for satir in {s.strip() for s in sayfa.splitlines() if s.strip()}:
            sayac[satir] = sayac.get(satir, 0) + 1
    # üç ve daha fazla sayfada aynen geçen kısa satırlar başlık kabul ediliyor
    tekrar_edenler = {s for s, n in sayac.items() if n >= 3 and len(s) < 120}

    satirlar = []
    for sayfa in sayfalar:
        for satir in sayfa.splitlines():
            s = satir.strip()
            if not s or s in tekrar_edenler:
                continue
            if any(g in s for g in GURULTU):
                continue
            if re.fullmatch(r"\d+\s*/\s*\d+", s):  # tek başına sayfa numarası
                continue
            satirlar.append(s)
    return satirlar


def maddelere_bol(satirlar: list[str], kaynak: str) -> list[Parca]:
    parcalar: list[Parca] = []
    baslik = ""
    madde = ""
    govde: list[str] = []
    onceki = ""

    def kaydet():
        if madde and govde:
            parcalar.append(Parca(kaynak, madde, baslik, " ".join(govde)))

    i = 0
    while i < len(satirlar):
        s = satirlar[i]
        if BOLUM_DESENI.match(s):   # "İKİNCİ BÖLÜM" ve altındaki bölüm adı
            i += 2
            onceki = ""
            continue
        m = MADDE_DESENI.match(s)
        if m:
            kaydet()
            gecici, no, kalan = m.groups()
            madde = f"{'Geçici ' if gecici else ''}Madde {no}"
            # bir önceki kısa satır madde başlığıdır ("Staj süresi" gibi)
            # (tamamı büyük harf olan satırlar belge başlığıdır, madde başlığı değil)
            baslik = onceki if (onceki and len(onceki) < 80 and not onceki.endswith(".") and not onceki.isupper()) else ""
            if baslik and govde and govde[-1] == baslik:
                govde.pop()
                # başlık bir önceki maddeye eklenmişti, onu geri al
                if parcalar and parcalar[-1].metin.endswith(baslik):
                    parcalar[-1].metin = parcalar[-1].metin[: -len(baslik)].rstrip()
            govde = [kalan.strip()] if kalan.strip() else []
        elif madde:
            govde.append(s)
        onceki = s
        i += 1
    kaydet()
    return parcalar


def uzun_maddeleri_bol(parcalar: list[Parca], maks: int = ayarlar.MAKS_PARCA_UZUNLUGU) -> list[Parca]:
    sonuc = []
    for p in parcalar:
        if len(p.metin) <= maks:
            sonuc.append(p)
            continue
        fikralar = [f.strip() for f in FIKRA_DESENI.split(p.metin) if f.strip()]
        grup: list[str] = []
        for f in fikralar:
            if grup and len(" ".join(grup)) + len(f) > maks:
                sonuc.append(Parca(p.kaynak, p.madde, p.baslik, " ".join(grup)))
                grup = []
            grup.append(f)
        if grup:
            sonuc.append(Parca(p.kaynak, p.madde, p.baslik, " ".join(grup)))
    return sonuc


def dosyayi_parcala(yol: Path) -> list[Parca]:
    kaynak = ayarlar.BELGE_ADLARI.get(yol.stem, yol.stem.replace("-", " "))
    satirlar = sayfa_basliklarini_temizle(yol.read_text(encoding="utf-8"))
    return uzun_maddeleri_bol(maddelere_bol(satirlar, kaynak))


def tum_belgeleri_parcala(klasor: Path = ayarlar.BELGE_KLASORU) -> list[Parca]:
    parcalar = []
    for yol in sorted(klasor.glob("*.txt")):
        parcalar.extend(dosyayi_parcala(yol))
    return parcalar
