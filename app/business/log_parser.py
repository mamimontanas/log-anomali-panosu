import ipaddress
from datetime import datetime

GECERLI_DURUMLAR = ("basarili", "basarisiz")


def satir_ayristir(satir):
    """Tek bir log satırını parçalarına ayırır.

    Örnek: 2026-10-23 09:42:10 auth basarisiz user=admin ip=203.0.113.45
    Doğruysa sözlük döndürür, bozuksa ValueError fırlatır.
    """
    satir = satir.strip()
    parcalar = satir.split()

    if len(parcalar) < 4:
        raise ValueError("Eksik alanlar")

    try:
        tarih = datetime.strptime(parcalar[0] + " " + parcalar[1], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError("Geçersiz tarih formatı")

    if parcalar[2] != "auth":
        raise ValueError("Geçersiz log türü")

    durum = parcalar[3]
    if durum not in GECERLI_DURUMLAR:
        raise ValueError("Geçersiz durum")

    user = None
    ip = None

    for parca in parcalar[4:]:
        if parca.startswith("user="):
            user = parca.split("=", 1)[1]
        elif parca.startswith("ip="):
            ip = parca.split("=", 1)[1]

    if not user or not ip:
        raise ValueError("Eksik alanlar")

    try:
        ipaddress.ip_address(ip)
    except ValueError:
        raise ValueError("Geçersiz IP adresi")

    return {
        "zaman": tarih,
        "durum": durum,
        "kullanici_adi": user,
        "ip_adresi": ip,
        "ham_metin": satir,
    }


def dosya_ayristir(satirlar):
    """Bir dosyanın tüm satırlarını ayrıştırır.

    Boş satırları atlar. Bozuk satırlar içe aktarmayı durdurmaz,
    satır numarası ve hata mesajıyla ayrı bir listeye yazılır.
    Dönen değer: (gecerli_kayitlar, hatalar)
    """
    kayitlar = []
    hatalar = []
    for no, satir in enumerate(satirlar, start=1):
        if not satir.strip():
            continue
        try:
            kayitlar.append(satir_ayristir(satir))
        except ValueError as hata:
            hatalar.append({"satir_no": no, "satir": satir.strip(), "hata": str(hata)})
    return kayitlar, hatalar
