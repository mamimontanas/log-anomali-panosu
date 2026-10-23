"""
Log ayrıştırıcı testleri (Hafta 6). Veritabanı gerektirmez.

Çalıştırma: python -m pytest tests -v
"""
from datetime import datetime

import pytest

from app.business.log_parser import dosya_ayristir, satir_ayristir

GECERLI = "2026-10-23 09:42:10 auth basarisiz user=admin ip=203.0.113.45"


def test_gecerli_satir_ayristirilir():
    k = satir_ayristir(GECERLI)
    assert k["zaman"] == datetime(2026, 10, 23, 9, 42, 10)
    assert k["durum"] == "basarisiz"
    assert k["kullanici_adi"] == "admin"
    assert k["ip_adresi"] == "203.0.113.45"
    assert k["ham_metin"] == GECERLI


def test_bastaki_ve_sondaki_bosluklar_temizlenir():
    k = satir_ayristir("   " + GECERLI + "  \n")
    assert k["ham_metin"] == GECERLI


def test_user_ve_ip_sirasi_farkli_olabilir():
    k = satir_ayristir("2026-10-23 09:42:10 auth basarili ip=192.0.2.31 user=ayse.k")
    assert k["kullanici_adi"] == "ayse.k"
    assert k["ip_adresi"] == "192.0.2.31"


@pytest.mark.parametrize("satir", [
    "bu satir bozuk",                                                # eksik alan
    "2026-13-40 09:42:10 auth basarili user=a ip=192.0.2.1",          # geçersiz tarih
    "2026-10-23 09:42:10 ssh basarili user=a ip=192.0.2.1",           # log türü auth değil
    "2026-10-23 09:42:10 auth belki user=a ip=192.0.2.1",             # geçersiz durum
    "2026-10-23 09:42:10 auth basarili user=a ip=999.1.1.1",          # geçersiz IP
    "2026-10-23 09:42:10 auth basarili ip=192.0.2.1 x=y",             # kullanıcı yok
    "",                                                              # boş satır
])
def test_bozuk_satirlar_reddedilir(satir):
    with pytest.raises(ValueError):
        satir_ayristir(satir)


def test_dosya_bozuk_satirda_durmaz_ve_bos_satiri_atlar():
    satirlar = [GECERLI, "", "bozuk satir", GECERLI.replace("admin", "root")]
    kayitlar, hatalar = dosya_ayristir(satirlar)
    assert len(kayitlar) == 2
    assert len(hatalar) == 1
    assert hatalar[0]["satir_no"] == 3


def test_ornek_dosya_beklenen_sonucu_verir():
    with open("sample_logs/ornek_giris.log", encoding="utf-8") as f:
        kayitlar, hatalar = dosya_ayristir(f)
    assert len(kayitlar) == 7
    assert [h["satir_no"] for h in hatalar] == [8, 9, 10]