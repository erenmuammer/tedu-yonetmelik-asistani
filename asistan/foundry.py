"""Foundry Local servisine bağlanan tek yer.

Foundry Local'ın kendi servisi (foundry server) arka planda çalışıyor ve
OpenAI uyumlu bir HTTP API açıyor. Uygulama bu API'ye openai paketiyle
bağlanıyor. Modellerin önce servise yüklenmesi gerekiyor, onu da
`foundry model load` komutuyla yapıyoruz.

Neden SDK değil de HTTP: pip'teki foundry-local-sdk 2.0.1 bu Mac'te
WebGPU desteklemediği için modelleri CPU'da çalıştırıyordu, CLI servisi ise
GPU (Metal) kullanıyor ve cevaplar çok daha hızlı geliyor. Servis Windows ve
Linux'ta da aynı şekilde çalıştığı için bu yol taşınabilir de.
"""
import json
import subprocess

from openai import OpenAI

KURULUM_NOTU = ("foundry komutu bulunamadı. Kurulum için: "
                "brew tap microsoft/foundrylocal && brew install foundrylocal "
                "(Windows: winget install Microsoft.FoundryLocal)")


def _komut(*args: str) -> dict:
    """foundry CLI komutunu çalıştırıp JSON çıktısını döner."""
    try:
        sonuc = subprocess.run(["foundry", *args, "-o", "json"],
                               capture_output=True, text=True, timeout=1800)
    except FileNotFoundError:
        raise SystemExit(KURULUM_NOTU)
    try:
        return json.loads(sonuc.stdout)
    except json.JSONDecodeError:
        raise SystemExit(f"foundry {' '.join(args)} beklenmeyen çıktı verdi:\n{sonuc.stdout}{sonuc.stderr}")


def sunucu_adresi() -> str:
    """Servis çalışmıyorsa başlatır, HTTP adresini döner."""
    durum = _komut("server", "status")
    if not durum.get("running"):
        print("Foundry Local servisi başlatılıyor...")
        subprocess.run(["foundry", "server", "start"], capture_output=True, text=True, timeout=120)
        durum = _komut("server", "status")
    return durum["webUrls"][0]


def modeli_yukle(alias: str) -> str:
    """Modeli servise yükler (ilk seferde indirir) ve tam model id'sini döner."""
    kayitli = {m["alias"]: m for m in _komut("cache", "list")["models"]}
    bilgi = kayitli.get(alias)
    if bilgi and bilgi.get("loaded"):
        return bilgi["id"]
    if not bilgi or not bilgi.get("cached"):
        print(f"{alias} indiriliyor, bu sadece ilk seferde olacak (birkaç dakika sürebilir)...")
        subprocess.run(["foundry", "model", "download", alias], timeout=3600)
    sonuc = _komut("model", "load", alias)
    if not sonuc.get("success"):
        raise SystemExit(f"{alias} yüklenemedi: {sonuc.get('message')}")
    for m in _komut("model", "list", "--loaded")["models"]:
        if m["alias"] == alias:
            return m["id"]
    raise SystemExit(f"{alias} yüklendi ama listede görünmüyor.")


_istemci = None


def istemci() -> OpenAI:
    global _istemci
    if _istemci is None:
        # api_key zorunlu bir alan ama yerel servis kontrol etmiyor
        _istemci = OpenAI(base_url=sunucu_adresi() + "/v1", api_key="yerel")
    return _istemci
