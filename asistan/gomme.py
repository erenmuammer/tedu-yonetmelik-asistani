"""Metinleri embedding vektörüne çevirir (qwen3-embedding-0.6b, 1024 boyut)."""
import numpy as np

from asistan import ayarlar, foundry

_model_id = None


def _model() -> str:
    global _model_id
    if _model_id is None:
        _model_id = foundry.modeli_yukle(ayarlar.EMBEDDING_MODELI)
    return _model_id


def metinleri_gom(metinler: list[str], grup: int = 16) -> np.ndarray:
    """(n, 1024) boyutlu, satırları normalize edilmiş float32 matris döner."""
    vektorler = []
    for i in range(0, len(metinler), grup):
        yanit = foundry.istemci().embeddings.create(model=_model(), input=metinler[i:i + grup])
        vektorler.extend(v.embedding for v in sorted(yanit.data, key=lambda d: d.index))
    matris = np.asarray(vektorler, dtype=np.float32)
    return matris / np.linalg.norm(matris, axis=1, keepdims=True)


def soruyu_gom(soru: str) -> np.ndarray:
    return metinleri_gom([soru])[0]
