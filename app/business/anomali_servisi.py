"""Kural motorunu veritabanına bağlayan iş katmanı servisi (Hafta 7)."""
from app.business.kural_motoru import kurallari_uygula
from app.data import crud


def anomali_taramasi(sirket_id):
    """Şirketin loglarını kurallarıyla tarar, yeni anomalileri kaydeder.

    Dönen değer: (bulunan_bulgu_sayisi, yeni_kaydedilen_anomali_sayisi)
    """
    loglar = crud.loglari_getir(sirket_id)
    kurallar = crud.kurallari_getir(sirket_id)
    bulgular = kurallari_uygula(loglar, kurallar)
    yeni = crud.anomalileri_kaydet(sirket_id, bulgular)
    return len(bulgular), yeni