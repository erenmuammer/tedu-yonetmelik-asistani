"""Foundry Local modellerini yükleyen tek yer.

Modeller ilk seferde katalogdan indiriliyor (embedding ~500 MB, phi-4-mini ~3.7 GB),
sonrasında ~/.foundry/cache altından çalışıyor ve internet gerekmiyor.
"""
from foundry_local_sdk import Configuration, FoundryLocalManager

from asistan import ayarlar

_yonetici = None


def yonetici():
    global _yonetici
    if _yonetici is None:
        FoundryLocalManager.initialize(Configuration(app_name="tedu-yonetmelik-asistani"))
        _yonetici = FoundryLocalManager.instance
    return _yonetici


def modeli_hazirla(alias: str):
    """Modeli katalogdan bulur, gerekiyorsa indirir ve belleğe yükler."""
    model = yonetici().catalog.get_model(alias)
    if model is None:
        raise SystemExit(f"'{alias}' Foundry Local kataloğunda bulunamadı ('foundry model list' ile bakın).")
    if not model.is_cached:
        print(f"{alias} indiriliyor, bu sadece ilk seferde olacak...")
        model.download(lambda p: print(f"\r  %{p:.0f}", end="", flush=True))
        print()
    if not model.is_loaded:
        model.load()
    return model


def embedding_modeli():
    return modeli_hazirla(ayarlar.EMBEDDING_MODELI)


def chat_modeli(alias: str | None = None):
    return modeli_hazirla(alias or ayarlar.CHAT_MODELI)
