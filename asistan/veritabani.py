"""Parçaları ve embedding'lerini SQLite'ta saklar.

Embedding'ler float32 BLOB olarak tutuluyor (1024 x 4 byte). Arama sırasında
hepsi belleğe okunup numpy ile karşılaştırılıyor; birkaç yüz parça için bu
milisaniyeler sürüyor, ayrı bir vektör veritabanına gerek olmadı.
"""
import sqlite3
from pathlib import Path

import numpy as np

from asistan import ayarlar
from asistan.parcalama import Parca

SEMA = """
CREATE TABLE IF NOT EXISTS parcalar (
    id        INTEGER PRIMARY KEY,
    kaynak    TEXT NOT NULL,
    madde     TEXT NOT NULL,
    baslik    TEXT,
    metin     TEXT NOT NULL,
    embedding BLOB NOT NULL
)"""


def baglan(yol: Path = ayarlar.VERITABANI) -> sqlite3.Connection:
    baglanti = sqlite3.connect(yol)
    baglanti.execute(SEMA)
    return baglanti


def sifirla(baglanti: sqlite3.Connection) -> None:
    baglanti.execute("DELETE FROM parcalar")
    baglanti.commit()


def ekle(baglanti: sqlite3.Connection, parcalar: list[Parca], vektorler: np.ndarray) -> None:
    baglanti.executemany(
        "INSERT INTO parcalar (kaynak, madde, baslik, metin, embedding) VALUES (?, ?, ?, ?, ?)",
        [(p.kaynak, p.madde, p.baslik, p.metin, np.asarray(v, dtype=np.float32).tobytes())
         for p, v in zip(parcalar, vektorler)],
    )
    baglanti.commit()


def hepsini_oku(baglanti: sqlite3.Connection) -> tuple[list[Parca], np.ndarray]:
    satirlar = baglanti.execute(
        "SELECT kaynak, madde, baslik, metin, embedding FROM parcalar ORDER BY id").fetchall()
    parcalar = [Parca(k, m, b, t) for k, m, b, t, _ in satirlar]
    if not satirlar:
        return parcalar, np.zeros((0, 1024), dtype=np.float32)
    matris = np.frombuffer(b"".join(s[4] for s in satirlar), dtype=np.float32)
    return parcalar, matris.reshape(len(satirlar), -1)


def sayi(baglanti: sqlite3.Connection) -> int:
    return baglanti.execute("SELECT COUNT(*) FROM parcalar").fetchone()[0]
