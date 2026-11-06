"""
Kural motoru testleri (Hafta 7).
Son test geçici bir şirket oluşturup veritabanına yazar, sonunda temizler.

Çalıştırma: python -m pytest tests -v
"""
import uuid

import pytest

from app.business.anomali_servisi import anomali_taramasi
from app.business.auth import parola_hashle
from app.business.kural_motoru import cok_basarisiz_giris_bul, kurallari_uygula, onem_belirle
from app.business.log_parser import dosya_ayristir
from app.data import crud
from app.data.db import get_connection

KURALLAR = [
    {"id": 1, "ad": "Çok başarısız", "kural_turu": "cok_basarisiz_giris", "esik": 5, "pencere_dk": 10, "aktif": True},
    {"id": 2, "ad": "Çok kullanıcı", "kural_turu": "cok_kullanici_denemesi", "esik": 5, "pencere_dk": 15, "aktif": True},
    {"id": 3, "ad": "Başarısızdan başarıya", "kural_turu": "basarisizdan_basariya", "esik": 5, "pencere_dk": 30, "aktif": True},
    {"id": 4, "ad": "Mesai dışı", "kural_turu": "mesai_disi", "esik": None, "pencere_dk": None, "aktif": True},
]


@pytest.fixture
def senaryo():
    with open("sample_logs/saldiri_senaryosu.log", encoding="utf-8") as f:
        kayitlar, hatalar = dosya_ayristir(f)
    assert not hatalar
    for no, k in enumerate(kayitlar, start=1):
        k["id"] = no
    return kayitlar


def test_dort_kural_beklenen_bulgulari_verir(senaryo):
    bulgular = {(b["kural_id"], b["ip_adresi"]) for b in kurallari_uygula(senaryo, KURALLAR)}
    assert bulgular == {
        (1, "198.51.100.23"), (1, "198.51.100.9"),
        (2, "198.51.100.9"),
        (3, "198.51.100.23"),
        (4, "192.0.2.31"), (4, "192.0.2.55"),
    }


def test_normal_kullanici_hatasi_alarm_uretmez(senaryo):
    # can.y bir kez yanlış girip düzeltiyor: yanlış alarm olmamalı
    assert all(b["ip_adresi"] != "192.0.2.14" for b in kurallari_uygula(senaryo, KURALLAR))


def test_esik_ve_pencere_sinirlari(senaryo):
    assert cok_basarisiz_giris_bul(senaryo, esik=7, pencere_dk=10) == []   # 6 hata, eşik 7
    assert cok_basarisiz_giris_bul(senaryo, esik=5, pencere_dk=1) == []    # 1 dakikaya sığmıyor


@pytest.mark.parametrize("tur, sayi, beklenen", [
    ("basarisizdan_basariya", 6, "yuksek"),
    ("cok_basarisiz_giris", 10, "yuksek"),
    ("cok_basarisiz_giris", 9, "orta"),
    ("cok_kullanici_denemesi", 6, "orta"),
    ("mesai_disi", 1, "dusuk"),
])
def test_onem_derecesi(tur, sayi, beklenen):
    assert onem_belirle(tur, sayi) == beklenen


def test_pasif_kural_calismaz(senaryo):
    pasif = [dict(k, aktif=False) for k in KURALLAR]
    assert kurallari_uygula(senaryo, pasif) == []


def test_esigi_eksik_kural_calismaz(senaryo):
    eksik = [dict(KURALLAR[0], esik=None)]
    assert kurallari_uygula(senaryo, eksik) == []


def _sirketi_sil(sirket_id):
    """Test şirketini ve ona bağlı tüm kayıtları doğru sırayla siler."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM uyari WHERE anomali_id IN "
                    "(SELECT id FROM anomali WHERE sirket_id = ?)", sirket_id)
        cur.execute("DELETE FROM anomali_log WHERE anomali_id IN "
                    "(SELECT id FROM anomali WHERE sirket_id = ?)", sirket_id)
        for tablo in ("anomali", "log_kaydi", "kural", "kaynak", "kullanici"):
            cur.execute(f"DELETE FROM {tablo} WHERE sirket_id = ?", sirket_id)
        cur.execute("DELETE FROM sirket WHERE id = ?", sirket_id)
        conn.commit()
    finally:
        conn.close()


def test_tarama_kaydeder_ve_tekrar_etmez(senaryo):
    ek = uuid.uuid4().hex[:8]
    sirket_id = crud.sirket_ve_yonetici_ekle(
        f"Kural Test {ek}", f"kural_test_{ek}", parola_hashle("testparola123"))
    try:
        assert len(crud.kurallari_getir(sirket_id)) == 4   # varsayılan kurallar eklendi
        kaynak_id = crud.kaynak_ekle(sirket_id, "VPN")
        crud.loglar_toplu_ekle(sirket_id, kaynak_id, senaryo)
        assert anomali_taramasi(sirket_id) == (6, 6)        # 6 bulgu, 6 yeni anomali
        assert anomali_taramasi(sirket_id) == (6, 0)        # tekrar taramada yeni kayıt yok
        assert len(crud.anomalileri_getir(sirket_id)) == 6
    finally:
        _sirketi_sil(sirket_id)