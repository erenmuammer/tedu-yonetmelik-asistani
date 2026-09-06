from asistan.cevap import dusunmeyi_atla, kaynaktan_sonra_kes, temizle


def test_kaynak_satirindan_sonrasi_atiliyor():
    metin = "Staj en az 40 iş günüdür.\nKaynak: Staj Yönergesi, Madde 5\nd) alakasız devam\nbaşka şeyler"
    assert temizle(metin) == "Staj en az 40 iş günüdür.\nKaynak: Staj Yönergesi, Madde 5"
    assert temizle("Sadece cevap, kaynak yok") == "Sadece cevap, kaynak yok"


def test_akista_da_kesiliyor():
    akis = ["Cevap.\nKay", "nak: X, Madde 1\nsaçma", "lık"]
    assert list(kaynaktan_sonra_kes(akis)) == ["Cevap.\nKay", "nak: X, Madde 1"]
    assert list(kaynaktan_sonra_kes(["tam", " cevap"])) == ["tam", " cevap"]


def test_dusunme_blogu_temizleniyor():
    assert temizle("<think>\n\nCevap.\nKaynak: X, Madde 1") == "Cevap.\nKaynak: X, Madde 1"
    assert temizle("<think>\nuzun uzun düşünce\n</think>\n\nCevap.") == "Cevap."
    assert temizle("Düz cevap.") == "Düz cevap."


def test_akista_dusunme_blogu_atlaniyor():
    assert list(dusunmeyi_atla(["<th", "ink>\n", "\nCev", "ap.\nKaynak: X"])) == ["Cev", "ap.\nKaynak: X"]
    assert list(dusunmeyi_atla(["<think>\n", "</think>\n\nCevap", "."])) == ["Cevap", "."]
    assert list(dusunmeyi_atla(["Düz", " cevap"])) == ["Düz", " cevap"]
