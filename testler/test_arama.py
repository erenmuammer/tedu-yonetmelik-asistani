import numpy as np

from asistan.arama import Sonuc, en_yakinlar, yeterli_mi
from asistan.parcalama import Parca


def _birim(v):
    v = np.asarray(v, dtype=np.float32)
    return v / np.linalg.norm(v)


def test_en_yakinlar_benzerlige_gore_siralar():
    matris = np.stack([_birim([1, 0, 0]), _birim([0, 1, 0]), _birim([1, 1, 0])])
    sonuc = en_yakinlar(matris, _birim([1, 0.2, 0]), ust_k=2)
    assert [i for i, _ in sonuc] == [0, 2]
    assert sonuc[0][1] > sonuc[1][1]


def test_esik_kontrolu():
    p = Parca("X", "Madde 1", "", "metin")
    assert yeterli_mi([Sonuc(p, 0.55), Sonuc(p, 0.2)], esik=0.4)
    assert not yeterli_mi([Sonuc(p, 0.3)], esik=0.4)
    assert not yeterli_mi([], esik=0.4)
