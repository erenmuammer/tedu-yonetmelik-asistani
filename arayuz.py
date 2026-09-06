"""Streamlit arayüzü.

    streamlit run arayuz.py
"""
import time

import streamlit as st

from asistan import ayarlar
from asistan.arama import Arama
from asistan.cevap import cevapla

ORNEKLER = [
    "Zorunlu staj en az kaç iş günü sürer?",
    "Başarı bursu almak için ne gerekiyor?",
    "Yaz okulunda en fazla kaç ders alabilirim?",
    "Kampüste yemekhane fiyatları ne kadar?",
]

st.set_page_config(page_title="TEDÜ Yönetmelik Asistanı", page_icon="📘")
st.title("TEDÜ Yönetmelik Asistanı")
st.caption("TED Üniversitesi yönetmelik ve yönergelerinden, tamamen bu bilgisayarda çalışan "
           "bir dil modeliyle cevap verir. Resmî bilgi değildir; kesin bilgi için Öğrenci İşleri'ne sorun.")


@st.cache_resource
def arama_motoru() -> Arama:
    return Arama()


with st.sidebar:
    st.subheader("Ayarlar")
    ust_k = st.slider("Getirilecek parça sayısı", 1, 8, ayarlar.UST_K)
    esik = st.slider("Benzerlik eşiği", 0.20, 0.70, ayarlar.BENZERLIK_ESIGI, 0.01,
                     help="En iyi parça bile bu değerin altındaysa modele sorulmaz, 'bulamadım' denir.")
    st.markdown(f"**Model:** `{ayarlar.CHAT_MODELI}`  \n**Embedding:** `{ayarlar.EMBEDDING_MODELI}`")
    st.markdown("**Belgeler:**  \n" + "  \n".join(f"- {ad}" for ad in ayarlar.BELGE_ADLARI.values()))

if "soru" not in st.session_state:
    st.session_state.soru = ""

st.write("Örnek sorular:")
sutunlar = st.columns(2)
for i, ornek in enumerate(ORNEKLER):
    if sutunlar[i % 2].button(ornek, use_container_width=True):
        st.session_state.soru = ornek

soru = st.text_input("Sorunuz", key="soru", placeholder="Örn. Yatay geçiş başvurusu ne zaman yapılır?")

if soru.strip():
    baslangic = time.time()
    with st.spinner("Belgeler taranıyor..."):
        sonuclar = arama_motoru().ara(soru, ust_k)
    yer = st.empty()
    metin = ""
    for parca in cevapla(soru, sonuclar, akis=True, esik=esik):
        metin += parca
        yer.markdown(metin)
    st.caption(f"{time.time() - baslangic:.1f} saniye")

    with st.expander("Modele verilen parçalar"):
        for s in sonuclar:
            st.markdown(f"**{s.parca.etiket()}** · benzerlik {s.benzerlik:.2f}")
            st.write(s.parca.metin)
