from asistan.parcalama import (Parca, maddelere_bol, sayfa_basliklarini_temizle,
                               uzun_maddeleri_bol)

BASLIK = "   TED ÜNİVERSİTESİ STAJ YÖNERGESİ\n   Doküman No  Yayın Tarihi\n   KYS-YN-17  30.04.2014  2/5\n"


def test_tekrar_eden_sayfa_basliklari_atiliyor():
    metin = "\f".join(BASLIK + f"sayfa {i} metni\n" for i in range(4))
    satirlar = sayfa_basliklarini_temizle(metin)
    assert satirlar == ["sayfa 0 metni", "sayfa 1 metni", "sayfa 2 metni", "sayfa 3 metni"]


def test_farkli_madde_bicimleri_bolunuyor():
    satirlar = [
        "Amaç",
        "MADDE 1 – (1) Bu yönergenin amacı stajı düzenlemektir.",
        "Süre",
        "MADDE 2-",
        "Staj en az 20 iş günüdür.",
        "Madde 3: (1) Üçüncü madde.",
        "GEÇİCİ MADDE 1 – Geçiş hükmü.",
    ]
    parcalar = maddelere_bol(satirlar, "Staj Yönergesi")
    assert [p.madde for p in parcalar] == ["Madde 1", "Madde 2", "Madde 3", "Geçici Madde 1"]
    assert parcalar[0].baslik == "Amaç"
    assert parcalar[1].baslik == "Süre"
    assert parcalar[1].metin == "Staj en az 20 iş günüdür."
    assert parcalar[0].metin.endswith("düzenlemektir.")  # sonraki başlık metne karışmıyor


def test_bolum_basliklari_metne_karismiyor():
    satirlar = ["MADDE 1 – Birinci.", "İKİNCİ BÖLÜM", "Esaslar", "MADDE 2 – İkinci."]
    parcalar = maddelere_bol(satirlar, "X")
    assert parcalar[0].metin == "Birinci."
    assert parcalar[1].baslik == ""


def test_uzun_madde_fikralardan_bolunuyor():
    metin = " ".join(f"({i}) " + "kelime " * 40 for i in range(1, 8))
    parcalar = uzun_maddeleri_bol([Parca("X", "Madde 9", "Sınavlar", metin)], maks=600)
    assert len(parcalar) > 1
    assert all(p.madde == "Madde 9" for p in parcalar)
    assert all(len(p.metin) <= 600 for p in parcalar)
    assert "".join(p.metin for p in parcalar).count("(") == 7
