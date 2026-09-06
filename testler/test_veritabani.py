import numpy as np

from asistan import veritabani
from asistan.parcalama import Parca


def test_yaz_oku_dongusu(tmp_path):
    baglanti = veritabani.baglan(tmp_path / "deneme.db")
    parcalar = [Parca("Staj Yönergesi", "Madde 5", "Süre", "yirmi iş günü"),
                Parca("Burs Yönergesi", "Madde 8", "", "GNO 3.00")]
    vektorler = np.random.rand(2, 1024).astype(np.float32)
    veritabani.ekle(baglanti, parcalar, vektorler)
    assert veritabani.sayi(baglanti) == 2

    okunan, matris = veritabani.hepsini_oku(baglanti)
    assert okunan == parcalar
    assert matris.shape == (2, 1024) and matris.dtype == np.float32
    assert np.allclose(matris, vektorler)

    veritabani.sifirla(baglanti)
    assert veritabani.sayi(baglanti) == 0
    _, bos = veritabani.hepsini_oku(baglanti)
    assert bos.shape == (0, 1024)
