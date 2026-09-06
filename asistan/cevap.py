"""Bulunan parçaları bağlam olarak verip yerel modelden cevap üretir."""
import re

from asistan import ayarlar, foundry
from asistan.arama import Sonuc, yeterli_mi

RED_CEVABI = ("Bu konuda elimdeki belgelerde bilgi bulamadım. "
              "Öğrenci İşleri Müdürlüğü'ne sormanız daha doğru olur.")

SISTEM_MESAJI = """Sen TED Üniversitesi'nin yönetmelik ve yönergeleri hakkında öğrencilerin sorularını cevaplayan bir asistansın.
Sana yönetmeliklerden alınmış parçalar ve bir soru verilecek.
- Sadece parçalardaki bilgiyi kullan; kendi bilgini ekleme, tahmin yürütme.
- Parçalar konuyla ilgili görünse bile sorunun cevabını vermiyorsa cevap uydurma; sadece şunu yaz: Bu konuda elimdeki belgelerde bilgi bulamadım.
- Türkçe ve kısa cevap ver: 2-4 cümle. Başlık, kalın yazı ve liste kullanma.
- Sayıları, süreleri ve koşulları parçada geçtiği gibi yaz."""

# qwen3 cevaba boş bir <think></think> bloğuyla başlıyor (bazen kapanış etiketi olmadan)
DUSUNME_BLOGU = re.compile(r"^\s*<think>(?:.*?</think>)?\s*", re.S)
KAYNAK_ISARETI = re.compile(r"(?i)\bkaynak(lar)?\s*:")
CEVAP_ETIKETI = re.compile(r"(?i)^\s*cevap\s*:\s*")


def baglam_metni(sonuclar: list[Sonuc]) -> str:
    return "\n\n".join(f"--- Parça {i} ({s.parca.etiket()}) ---\n{s.parca.metin}"
                       for i, s in enumerate(sonuclar, 1))


def mesajlar(soru: str, sonuclar: list[Sonuc], model: str = ayarlar.CHAT_MODELI) -> list[dict]:
    kullanici = f"{baglam_metni(sonuclar)}\n\nSoru: {soru}"
    if "qwen3" in model:
        # qwen3 yoksa önce İngilizce uzun uzun "düşünüyor", cevap 15 saniyeyi buluyor
        kullanici += " /no_think"
    return [{"role": "system", "content": SISTEM_MESAJI},
            {"role": "user", "content": kullanici}]


def tekrarlari_sil(metin: str) -> str:
    """Model aynı cümleyi iki kere yazabiliyor; birebir tekrar eden cümleleri atar.

    Satır yapısı (liste maddeleri gibi) korunuyor.
    """
    gorulen: set[str] = set()
    satirlar = []
    for satir in metin.strip().splitlines():
        temiz = []
        for c in re.split(r"(?<=[.!?])\s+", satir.strip()):
            anahtar = c.strip().lower()
            if anahtar and anahtar not in gorulen:
                gorulen.add(anahtar)
                temiz.append(c.strip())
        if temiz:
            satirlar.append(" ".join(temiz))
    return "\n".join(satirlar)


def temizle(metin: str) -> str:
    """Modelin çıktısını toparlar.

    Düşünme bloğunu ve baştaki "Cevap:" etiketini atar, modelin kendi yazdığı
    "Kaynak:" kısmından sonrasını keser (kaynağı biz ekliyoruz), kalın yazıyı
    ve tekrar eden cümleleri temizler, yarım kalan son cümleyi düşürür.
    """
    metin = DUSUNME_BLOGU.sub("", metin, count=1).replace("**", "")
    metin = CEVAP_ETIKETI.sub("", metin)
    m = KAYNAK_ISARETI.search(metin)
    if m:
        metin = metin[: m.start()]
    metin = tekrarlari_sil(metin)
    if metin and metin[-1] not in ".!?" and metin.count(".") >= 1:
        metin = metin[: metin.rfind(".") + 1]  # max_tokens'a takılıp yarım kalan cümle
    return metin.strip()


def kaynak_satiri(sonuclar: list[Sonuc], esik: float, cevap: str = "") -> str:
    """Cevabın dayandığı parçaları tek satırda verir.

    Model hangi parçayı kullandığını söylemiyor; cevaptaki kelimelerle en çok
    örtüşen (ve eşiği geçen) iki parçayı kaynak sayıyoruz.
    """
    kelimeler = {k for k in re.findall(r"\w{4,}", cevap.lower())}
    adaylar = [s for s in sonuclar if s.benzerlik >= esik]
    def ortusme(s: Sonuc) -> int:
        return sum(1 for k in kelimeler if k in s.parca.metin.lower())
    adaylar.sort(key=lambda s: (ortusme(s), s.benzerlik), reverse=True)
    etiketler = []
    for s in adaylar:
        if s.parca.etiket() not in etiketler:
            etiketler.append(s.parca.etiket())
    return "Kaynak: " + " · ".join(etiketler[:2])


_model_idler: dict[str, str] = {}


def _model(alias: str) -> str:
    if alias not in _model_idler:
        _model_idler[alias] = foundry.modeli_yukle(alias)
    return _model_idler[alias]


def cevapla(soru: str, sonuclar: list[Sonuc], esik: float = ayarlar.BENZERLIK_ESIGI,
            model: str = ayarlar.CHAT_MODELI) -> str:
    if not yeterli_mi(sonuclar, esik):
        # eşiğin altındaysa modele hiç sormuyoruz; küçük modeller alakasız
        # bağlamdan da cevap uydurmaya meyilli
        return RED_CEVABI
    yanit = foundry.istemci().chat.completions.create(
        model=_model(model), messages=mesajlar(soru, sonuclar, model),
        temperature=0.1, max_tokens=300)
    cevap = temizle(yanit.choices[0].message.content)
    if "bilgi bulamadım" in cevap.lower():
        return RED_CEVABI
    return f"{cevap}\n{kaynak_satiri(sonuclar, esik, cevap)}"
