"""Metinleri embedding vektörüne çevirir (qwen3-embedding-0.6b, 1024 boyut)."""
import numpy as np

from asistan import foundry

_istemci = None


def _istemci_al():
    global _istemci
    if _istemci is None:
        _istemci = foundry.embedding_modeli().get_embedding_client()
    return _istemci


def metinleri_gom(metinler: list[str], grup: int = 16) -> np.ndarray:
    """(n, 1024) boyutlu, satırları normalize edilmiş float32 matris döner."""
    istemci = _istemci_al()
    vektorler = []
    for i in range(0, len(metinler), grup):
        yanit = istemci.generate_embeddings(metinler[i:i + grup])
        vektorler.extend(v.embedding for v in sorted(yanit.data, key=lambda d: d.index))
    matris = np.asarray(vektorler, dtype=np.float32)
    return matris / np.linalg.norm(matris, axis=1, keepdims=True)


def soruyu_gom(soru: str) -> np.ndarray:
    return metinleri_gom([soru])[0]
