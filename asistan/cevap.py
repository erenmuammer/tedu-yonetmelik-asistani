"""Bulunan parçaları bağlam olarak verip yerel modelden cevap üretir."""
import re

from asistan import ayarlar, foundry
from asistan.arama import Sonuc, yeterli_mi

RED_CEVABI = ("Bu konuda elimdeki belgelerde bilgi bulamadım. "
              "Öğrenci İşleri Müdürlüğü'ne sormanız daha doğru olur.")

SISTEM_MESAJI = """Sen TED Üniversitesi'nin yönetmelik ve yönergeleri hakkında öğrencilerin sorularını cevaplayan bir asistansın. Sana soruyla ilgili olabilecek madde parçaları verilecek.
Kurallar:
- Sadece verilen parçalardaki bilgiyi kullan; kendi bilgini ekleme, tahmin yürütme.
- Cevabı Türkçe ve en fazla 3-4 cümleyle ver. Sayıları, süreleri ve koşulları parçada geçtiği gibi yaz.
- Parçalar soruyu cevaplamıyorsa sadece şunu yaz: Bu konuda elimdeki belgelerde bilgi bulamadım.
- En sona tek satır ekle: Kaynak: <belge adı>, <madde>"""

KAYNAK_SATIRI = re.compile(r"(?im)^[ \t]*kaynak[^\n]*\n")


def baglam_metni(sonuclar: list[Sonuc]) -> str:
    return "\n\n".join(f"[{i}] {s.parca.etiket()}:\n{s.parca.metin}" for i, s in enumerate(sonuclar, 1))


def mesajlar(soru: str, sonuclar: list[Sonuc]) -> list[dict]:
    return [
        {"role": "system", "content": SISTEM_MESAJI},
        {"role": "user", "content": f"İLGİLİ PARÇALAR:\n\n{baglam_metni(sonuclar)}\n\nSORU: {soru}"},
    ]


def temizle(metin: str) -> str:
    """Model bazen 'Kaynak:' satırından sonra da yazmaya devam ediyor; orada kesiyoruz."""
    m = KAYNAK_SATIRI.search(metin)
    return (metin[: m.end()] if m else metin).strip()


def kaynaktan_sonra_kes(akis):
    """Akış için aynı şey: tamamlanmış bir 'Kaynak:' satırı görünce akışı bitirir."""
    metin = ""
    for parca in akis:
        onceki = len(metin)
        metin += parca
        m = KAYNAK_SATIRI.search(metin)
        if m:
            yield metin[onceki: m.end() - 1]
            return
        yield parca


_model_id = None


def _model() -> str:
    global _model_id
    if _model_id is None:
        _model_id = foundry.modeli_yukle(ayarlar.CHAT_MODELI)
    return _model_id


def cevapla(soru: str, sonuclar: list[Sonuc], akis: bool = False,
            esik: float = ayarlar.BENZERLIK_ESIGI):
    """Cevabı tek parça string olarak, akis=True ise parça parça (generator) döner."""
    if not yeterli_mi(sonuclar, esik):
        # eşiğin altındaysa modele hiç sormuyoruz; küçük modeller alakasız
        # bağlamdan da cevap uydurmaya meyilli
        return iter([RED_CEVABI]) if akis else RED_CEVABI
    yanit = foundry.istemci().chat.completions.create(
        model=_model(), messages=mesajlar(soru, sonuclar),
        temperature=0.0, max_tokens=350, stream=akis)
    if not akis:
        return temizle(yanit.choices[0].message.content)
    return kaynaktan_sonra_kes(
        c.choices[0].delta.content for c in yanit if c.choices and c.choices[0].delta.content)
