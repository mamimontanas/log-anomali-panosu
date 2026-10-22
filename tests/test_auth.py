"""
Kimlik doğrulama ve rol testleri (Hafta 5).
Geçici bir test şirketi ve iki kullanıcı oluşturur, testler bitince siler.

Çalıştırma: python -m pytest tests -v
"""
import uuid

import pytest

from app.business.auth import parola_dogrula, parola_hashle
from app.data import crud
from app.data.db import get_connection
from app.presentation.web import app

PAROLA = "testparola123"
HATA_MESAJI = "Kullanıcı adı veya parola hatalı."


def _sql(sql, *params):
    conn = get_connection()
    try:
        conn.cursor().execute(sql, *params)
        conn.commit()
    finally:
        conn.close()


@pytest.fixture(scope="module")
def kullanicilar():
    ek = uuid.uuid4().hex[:8]
    yon, ana, sirket = f"test_yon_{ek}", f"test_ana_{ek}", f"Test Şirketi {ek}"
    crud.sirket_ve_yonetici_ekle(sirket, yon, parola_hashle(PAROLA))
    _sql("INSERT INTO kullanici (sirket_id, kullanici_adi, parola_hash, rol) "
         "SELECT sirket_id, ?, ?, 'analist' FROM kullanici WHERE kullanici_adi = ?",
         ana, parola_hashle(PAROLA), yon)
    yield {"yonetici": yon, "analist": ana}
    _sql("DELETE FROM kullanici WHERE kullanici_adi IN (?, ?)", yon, ana)
    _sql("DELETE FROM sirket WHERE ad = ?", sirket)


@pytest.fixture
def istemci():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def giris_yap(istemci, kadi, parola=PAROLA):
    return istemci.post("/giris", data={"kullanici_adi": kadi, "parola": parola})


def test_parola_duz_saklanmiyor_ve_tuzlu():
    h1, h2 = parola_hashle(PAROLA), parola_hashle(PAROLA)
    assert PAROLA not in h1
    assert h1 != h2  # salt: aynı parola, farklı hash
    assert parola_dogrula(PAROLA, h1)
    assert not parola_dogrula("yanlis", h1)


def test_veritabaninda_hash_saklaniyor(kullanicilar):
    k = crud.kullanici_getir(kullanicilar["yonetici"])
    assert k["parola_hash"].startswith("$2b$")


def test_dogru_giris_panoya_yonlendirir(istemci, kullanicilar):
    r = giris_yap(istemci, kullanicilar["yonetici"])
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/pano")


def test_yanlis_parola_reddedilir(istemci, kullanicilar):
    r = giris_yap(istemci, kullanicilar["yonetici"], "yanlisparola")
    assert r.status_code == 200
    assert HATA_MESAJI in r.get_data(as_text=True)


def test_olmayan_kullanici_ayni_mesaji_alir(istemci):
    r = giris_yap(istemci, "boyle_biri_yok")
    assert HATA_MESAJI in r.get_data(as_text=True)


def test_oturumsuz_pano_engellenir(istemci):
    r = istemci.get("/pano")
    assert r.status_code == 302
    assert "/giris" in r.headers["Location"]


def test_analist_yonetim_sayfasina_giremez(istemci, kullanicilar):
    giris_yap(istemci, kullanicilar["analist"])
    r = istemci.get("/yonetim")
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/pano")


def test_yonetici_yonetim_sayfasina_girer(istemci, kullanicilar):
    giris_yap(istemci, kullanicilar["yonetici"])
    r = istemci.get("/yonetim")
    assert r.status_code == 200
    assert "Kural yönetimi" in r.get_data(as_text=True)