"""
Veri erişim katmanı: CRUD fonksiyonları (Hafta 4).

Temel kural: Her fonksiyon sirket_id alır ve SQL'de sirket_id ile filtreler.
Böylece bir şirket başka bir şirketin verisini okuyamaz, değiştiremez, silemez.

Tüm sorgular parametrelidir (?). Değerler SQL metnine yapıştırılmaz,
ayrı gönderilir. Bu, SQL injection saldırılarını engeller.
"""
from contextlib import contextmanager

import pyodbc

from app.data.db import get_connection

GECERLI_DURUMLAR = ("basarili", "basarisiz")


@contextmanager
def _oturum():
    """Bağlantı açar. Hata yoksa commit, hata varsa rollback yapar ve kapatır."""
    conn = get_connection()
    try:
        yield conn.cursor()
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _sozluk_listesi(cur):
    """Sorgu sonucunu [{kolon: değer}, ...] biçimine çevirir."""
    kolonlar = [k[0] for k in cur.description]
    return [dict(zip(kolonlar, satir)) for satir in cur.fetchall()]


# ====================== CREATE ======================

def log_ekle(sirket_id, kaynak_id, zaman, ip_adresi, kullanici_adi,
             durum, ham_metin=None):
    """Yeni bir giriş kaydı ekler ve yeni kaydın id'sini döndürür.

    Kaynağın bu şirkete ait olup olmadığı SQL içinde kontrol edilir.
    Başka şirketin kaynağı verilirse hiçbir satır eklenmez ve hata fırlatılır.
    """
    if durum not in GECERLI_DURUMLAR:
        raise ValueError(f"durum şunlardan biri olmalı: {GECERLI_DURUMLAR}")

    sql = """
        INSERT INTO log_kaydi
            (sirket_id, kaynak_id, zaman, ip_adresi, kullanici_adi, durum, ham_metin)
        OUTPUT INSERTED.id
        SELECT k.sirket_id, k.id, ?, ?, ?, ?, ?
        FROM kaynak k
        WHERE k.id = ? AND k.sirket_id = ?
    """
    with _oturum() as cur:
        satir = cur.execute(sql, zaman, ip_adresi, kullanici_adi, durum,
                            ham_metin, kaynak_id, sirket_id).fetchone()
        if satir is None:
            raise ValueError("Bu kaynak bu şirkete ait değil.")
        return satir[0]


def kural_ekle(sirket_id, ad, kural_turu, esik=None, pencere_dk=None):
    """Şirkete yeni bir anomali kuralı ekler ve id'sini döndürür."""
    sql = """
        INSERT INTO kural (sirket_id, ad, kural_turu, esik, pencere_dk)
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?, ?)
    """
    with _oturum() as cur:
        return cur.execute(sql, sirket_id, ad, kural_turu,
                           esik, pencere_dk).fetchone()[0]


# ======================= READ =======================

def son_loglar(sirket_id, adet=20):
    """Şirketin en yeni giriş kayıtlarını döndürür."""
    sql = """
        SELECT TOP (?) l.id, l.sirket_id, l.zaman, l.ip_adresi,
               l.kullanici_adi, l.durum, k.ad AS kaynak
        FROM log_kaydi l
        JOIN kaynak k ON k.id = l.kaynak_id
        WHERE l.sirket_id = ?
        ORDER BY l.zaman DESC
    """
    with _oturum() as cur:
        cur.execute(sql, adet, sirket_id)
        return _sozluk_listesi(cur)


def basarisiz_giris_ozeti(sirket_id, dakika=1440, en_az=1):
    """Son 'dakika' içindeki başarısız girişleri IP'ye göre özetler.

    Her IP için: başarısız sayısı, denenen farklı kullanıcı sayısı, son deneme.
    """
    sql = """
        SELECT ip_adresi,
               COUNT(*)                      AS basarisiz_sayisi,
               COUNT(DISTINCT kullanici_adi) AS farkli_kullanici,
               MAX(zaman)                    AS son_deneme
        FROM log_kaydi
        WHERE sirket_id = ?
          AND durum = 'basarisiz'
          AND zaman >= DATEADD(MINUTE, ?, SYSDATETIME())
        GROUP BY ip_adresi
        HAVING COUNT(*) >= ?
        ORDER BY basarisiz_sayisi DESC
    """
    with _oturum() as cur:
        cur.execute(sql, sirket_id, -dakika, en_az)
        return _sozluk_listesi(cur)


def kurallari_getir(sirket_id):
    """Şirketin tüm kurallarını döndürür."""
    sql = """
        SELECT id, ad, kural_turu, esik, pencere_dk, aktif
        FROM kural
        WHERE sirket_id = ?
        ORDER BY id
    """
    with _oturum() as cur:
        cur.execute(sql, sirket_id)
        return _sozluk_listesi(cur)


# ====================== UPDATE ======================

def kural_guncelle(sirket_id, kural_id, esik, pencere_dk):
    """Bir kuralın eşik ve zaman penceresini günceller.

    Dönen sayı etkilenen satır sayısıdır:
    1 = güncellendi, 0 = kural yok veya başka şirkete ait.
    """
    sql = """
        UPDATE kural
        SET esik = ?, pencere_dk = ?
        WHERE id = ? AND sirket_id = ?
    """
    with _oturum() as cur:
        return cur.execute(sql, esik, pencere_dk, kural_id, sirket_id).rowcount


# ====================== DELETE ======================

def kural_sil(sirket_id, kural_id):
    """Bir kuralı siler. Dönen sayı etkilenen satır sayısıdır (1 veya 0).

    Kurala bağlı anomali kaydı varsa yabancı anahtar kısıtı silmeye izin vermez.
    """
    sql = "DELETE FROM kural WHERE id = ? AND sirket_id = ?"
    try:
        with _oturum() as cur:
            return cur.execute(sql, kural_id, sirket_id).rowcount
    except pyodbc.IntegrityError:
        raise ValueError("Bu kurala bağlı anomali kayıtları var, silinemez.")