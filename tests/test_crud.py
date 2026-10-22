"""
CRUD testleri. Sentetik test verisi üzerinde çalışır (önce seed.py çalıştırılmış olmalı).

Çalıştırma (proje klasöründen):
    python -m pytest tests -v
"""
from datetime import datetime

import pytest

from app.data import crud
from app.data.db import get_connection


def _tek_deger(sql, *params):
    conn = get_connection()
    try:
        return conn.cursor().execute(sql, *params).fetchone()[0]
    finally:
        conn.close()


@pytest.fixture(scope="module")
def mavi():
    return _tek_deger("SELECT id FROM sirket WHERE ad = ?", "Mavi Lojistik A.Ş.")


@pytest.fixture(scope="module")
def yesil():
    return _tek_deger("SELECT id FROM sirket WHERE ad = ?", "Yeşil Gıda Ltd.")


def test_son_loglar_sadece_kendi_sirketinin(mavi):
    loglar = crud.son_loglar(mavi, adet=50)
    assert len(loglar) == 50
    assert all(l["sirket_id"] == mavi for l in loglar)


def test_basarisiz_ozeti_saldirgan_ipleri_bulur(mavi):
    # Pencere 1 yıl: seed verisi ne zaman yüklenmiş olursa olsun içinde kalsın
    ozet = crud.basarisiz_giris_ozeti(mavi, dakika=60 * 24 * 365, en_az=10)
    ipler = {o["ip_adresi"] for o in ozet}
    assert "203.0.113.45" in ipler
    assert "198.51.100.23" in ipler


def test_kural_ekle_guncelle_sil(mavi):
    kural_id = crud.kural_ekle(mavi, "Test kuralı", "mesai_disi")
    try:
        assert crud.kural_guncelle(mavi, kural_id, 3, 5) == 1
        kural = next(k for k in crud.kurallari_getir(mavi) if k["id"] == kural_id)
        assert kural["esik"] == 3 and kural["pencere_dk"] == 5
    finally:
        assert crud.kural_sil(mavi, kural_id) == 1


def test_baska_sirketin_kuralina_dokunulamaz(mavi, yesil):
    kural_id = crud.kural_ekle(mavi, "Gizli kural", "mesai_disi")
    try:
        assert crud.kural_guncelle(yesil, kural_id, 1, 1) == 0
        assert crud.kural_sil(yesil, kural_id) == 0
    finally:
        crud.kural_sil(mavi, kural_id)


def test_baska_sirketin_kaynagiyla_log_eklenemez(mavi, yesil):
    yesil_kaynak = _tek_deger(
        "SELECT TOP 1 id FROM kaynak WHERE sirket_id = ?", yesil)
    with pytest.raises(ValueError):
        crud.log_ekle(mavi, yesil_kaynak, datetime.now(),
                      "192.0.2.200", "test.kullanici", "basarili")


def test_gecersiz_durum_reddedilir(mavi):
    kaynak = _tek_deger("SELECT TOP 1 id FROM kaynak WHERE sirket_id = ?", mavi)
    with pytest.raises(ValueError):
        crud.log_ekle(mavi, kaynak, datetime.now(),
                      "192.0.2.200", "test.kullanici", "belki")