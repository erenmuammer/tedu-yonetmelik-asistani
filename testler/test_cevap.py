from asistan.arama import Sonuc
from asistan.cevap import kaynak_satiri, tekrarlari_sil, temizle
from asistan.parcalama import Parca


def test_dusunme_blogu_ve_kaynak_satiri_temizleniyor():
    assert temizle("<think>\n\nCevap budur.\nKaynak: X, Madde 1") == "Cevap budur."
    assert temizle("<think>\nuzun uzun düşünce\n</think>\n\nCevap budur.") == "Cevap budur."
    assert temizle("Düz **kalın** cevap.") == "Düz kalın cevap."
    assert temizle("**Cevap:**  \nDört yarıyıl izin verilir. Kaynak: Yönetmelik Madde 35") == "Dört yarıyıl izin verilir."
    assert temizle("İlk cümle tam. İkinci cümle yarım kal") == "İlk cümle tam."


def test_tekrar_eden_cumleler_atiliyor():
    assert tekrarlari_sil("En fazla dört yarıyıl izin verilir. En fazla dört yarıyıl izin verilir. Bunun için başvuru gerekir.") == \
        "En fazla dört yarıyıl izin verilir. Bunun için başvuru gerekir."


def test_kaynak_satiri_cevapla_ortusen_parcayi_secer():
    p1 = Parca("Staj Yönergesi", "Madde 5", "Süre", "stajların süresi toplam kırk iş günüdür")
    p2 = Parca("Staj Yönergesi", "Madde 9", "", "staj başvuru süreci kariyer merkezi")
    p3 = Parca("Burs Yönergesi", "Madde 8", "", "başarı bursu genel not ortalaması")
    sonuclar = [Sonuc(p2, 0.6), Sonuc(p1, 0.55), Sonuc(p3, 0.3)]
    satir = kaynak_satiri(sonuclar, esik=0.4, cevap="Zorunlu staj toplam kırk iş günüdür.")
    assert satir == "Kaynak: Staj Yönergesi, Madde 5 (Süre) · Staj Yönergesi, Madde 9"
    assert kaynak_satiri(sonuclar, esik=0.4) == "Kaynak: Staj Yönergesi, Madde 9 · Staj Yönergesi, Madde 5 (Süre)"
