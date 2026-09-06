"""Komut satırından soru sorma.

    python sor.py "Zorunlu staj en az kaç iş günü?"
    python sor.py                # soru-cevap döngüsü, çıkmak için boş satır
"""
import sys
import time

from asistan.arama import Arama
from asistan.cevap import cevapla


def sor(arama: Arama, soru: str) -> None:
    baslangic = time.time()
    sonuclar = arama.ara(soru)
    print()
    for parca in cevapla(soru, sonuclar, akis=True):
        print(parca, end="", flush=True)
    kaynaklar = "; ".join(f"{s.parca.etiket()} ({s.benzerlik:.2f})" for s in sonuclar[:3])
    print(f"\n\n[{time.time() - baslangic:.1f} sn] en yakın parçalar: {kaynaklar}")


def main():
    arama = Arama()
    if len(sys.argv) > 1:
        sor(arama, " ".join(sys.argv[1:]))
        return
    print("TEDÜ Yönetmelik Asistanı. Çıkmak için boş satır bırakın.")
    while True:
        try:
            soru = input("\nSoru: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not soru:
            break
        sor(arama, soru)


if __name__ == "__main__":
    main()
