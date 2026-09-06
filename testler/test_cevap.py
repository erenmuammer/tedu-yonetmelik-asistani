from asistan.cevap import kaynaktan_sonra_kes, temizle


def test_kaynak_satirindan_sonrasi_atiliyor():
    metin = "Staj en az 40 iş günüdür.\nKaynak: Staj Yönergesi, Madde 5\nd) alakasız devam\nbaşka şeyler"
    assert temizle(metin) == "Staj en az 40 iş günüdür.\nKaynak: Staj Yönergesi, Madde 5"
    assert temizle("Sadece cevap, kaynak yok") == "Sadece cevap, kaynak yok"


def test_akista_da_kesiliyor():
    akis = ["Cevap.\nKay", "nak: X, Madde 1\nsaçma", "lık"]
    assert list(kaynaktan_sonra_kes(akis)) == ["Cevap.\nKay", "nak: X, Madde 1"]
    assert list(kaynaktan_sonra_kes(["tam", " cevap"])) == ["tam", " cevap"]
