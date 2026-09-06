"""Bulunan parçaları bağlam olarak verip yerel modelden cevap üretir."""
import re

from asistan import ayarlar, foundry
from asistan.arama import Sonuc, yeterli_mi

RED_CEVABI = ("Bu konuda elimdeki belgelerde bilgi bulamadım. "
              "Öğrenci İşleri Müdürlüğü'ne sormanız daha doğru olur.")

SISTEM_MESAJI = """Sen TED Üniversitesi'nin yönetmelik ve yönergeleri hakkında öğrencilerin sorularını cevaplayan bir asistansın. Sana soruyla ilgili olabilecek madde parçaları verilecek.
Kurallar:
- Sadece verilen parçalardaki bilgiyi kullan; kendi bilgini ekleme, tahmin yürütme.
- Türkçe ve kısa cevap ver: 2-4 cümle. Başlık, kalın yazı ve uzun listeler kullanma.
- Sayıları, süreleri ve koşulları parçada geçtiği gibi yaz.
- Parçalar soruyu cevaplamıyorsa sadece şunu yaz: Bu konuda elimdeki belgelerde bilgi bulamadım.
- En sona tek satır ekle, örneğin: Kaynak: Staj Yönergesi, Madde 5"""

KAYNAK_SATIRI = re.compile(r"(?im)^[ \t]*kaynak[^\n]*\n")
# qwen3 cevaba boş bir <think></think> bloğuyla başlıyor (bazen kapanış etiketi olmadan)
DUSUNME_BLOGU = re.compile(r"^\s*<think>(?:.*?</think>)?\s*", re.S)


def baglam_metni(sonuclar: list[Sonuc]) -> str:
    return "\n\n".join(f"[{i}] {s.parca.etiket()}:\n{s.parca.metin}" for i, s in enumerate(sonuclar, 1))


def mesajlar(soru: str, sonuclar: list[Sonuc], model: str = ayarlar.CHAT_MODELI) -> list[dict]:
    soru_metni = f"İLGİLİ PARÇALAR:\n\n{baglam_metni(sonuclar)}\n\nSORU: {soru}"
    if "qwen3" in model:
        # qwen3 yoksa önce İngilizce uzun uzun "düşünüyor", cevap 15 saniyeyi buluyor
        soru_metni += " /no_think"
    return [
        {"role": "system", "content": SISTEM_MESAJI},
        {"role": "user", "content": soru_metni},
    ]


def temizle(metin: str) -> str:
    """Baştaki düşünme bloğunu atar; 'Kaynak:' satırından sonrasını keser.

    Model bazen kaynak satırından sonra da yazmaya devam ediyordu.
    """
    metin = DUSUNME_BLOGU.sub("", metin, count=1)
    m = KAYNAK_SATIRI.search(metin)
    return (metin[: m.end()] if m else metin).strip()


def dusunmeyi_atla(akis):
    """Akışın başındaki <think> etiketini (ve varsa hemen ardındaki kapanışı) göstermeden geçer.

    /no_think ile blok boş geliyor; dolu gelirse metnin içinde kalır, o durumu
    akışta ayırt etmenin bir yolu yok.
    """
    tampon = ""
    gecildi = False
    for parca in akis:
        if gecildi:
            yield parca
            continue
        tampon += parca
        bas = tampon.lstrip()
        if "<think>".startswith(bas):
            continue  # "<th" gibi, henüz belli değil
        if not bas.startswith("<think>"):
            gecildi = True
            yield tampon
            continue
        kalan = bas[len("<think>"):].lstrip()
        if kalan.startswith("</think>"):
            kalan = kalan[len("</think>"):].lstrip()
        elif "</think>".startswith(kalan):
            continue
        if kalan:
            gecildi = True
            yield kalan


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
    return kaynaktan_sonra_kes(dusunmeyi_atla(
        c.choices[0].delta.content for c in yanit if c.choices and c.choices[0].delta.content))
