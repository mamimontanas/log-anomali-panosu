from datetime import timedelta


def cok_basarisiz_giris_bul(loglar, esik, pencere_dk):
    """Aynı IP'den pencere_dk dakika içinde en az esik kadar başarısız giriş varsa yakalar.

    loglar: [{"id", "zaman", "ip_adresi", "kullanici_adi", "durum"}, ...]
    Dönen: [{"ip_adresi": "...", "log_idler": [...]}, ...]
    """
    pencere = timedelta(minutes=pencere_dk)

    # Sadece başarısız girişleri IP'ye göre grupla
    gruplar = {}
    for log in loglar:
        if log["durum"] == "basarisiz":
            gruplar.setdefault(log["ip_adresi"], []).append(log)

    bulgular = []
    for ip, ip_loglari in gruplar.items():
        ip_loglari.sort(key=lambda l: l["zaman"])

        # Kaydırmalı pencere ile kontrol et
        for i in range(len(ip_loglari)):
            pencere_baslangici = ip_loglari[i]["zaman"]
            pencere_sonu = pencere_baslangici + pencere

            # Pencere içindeki logları say
            pencere_icindeki_loglar = [
                log for log in ip_loglari if pencere_baslangici <= log["zaman"] <= pencere_sonu
            ]

            if len(pencere_icindeki_loglar) >= esik:
                bulgular.append({
                    "ip_adresi": ip,
                    "log_idler": [log["id"] for log in pencere_icindeki_loglar]
                })
                break  # Aynı IP için birden fazla bulgu istemiyoruz

    return bulgular


MESAI_BASLANGIC = 8   # 08:00
MESAI_BITIS = 18      # 18:00


def _ip_gruplari(loglar, sadece_durum=None):
    """Logları IP'ye göre gruplar ve her grubu zamana göre sıralar."""
    gruplar = {}
    for log in loglar:
        if sadece_durum is None or log["durum"] == sadece_durum:
            gruplar.setdefault(log["ip_adresi"], []).append(log)
    for liste in gruplar.values():
        liste.sort(key=lambda l: l["zaman"])
    return gruplar


def cok_kullanici_denemesi_bul(loglar, esik, pencere_dk):
    """Aynı IP pencere içinde en az esik kadar FARKLI kullanıcı adını
    başarısız denediyse yakalar (hesap tarama belirtisi)."""
    pencere = timedelta(minutes=pencere_dk)
    bulgular = []
    for ip, ip_loglari in _ip_gruplari(loglar, "basarisiz").items():
        for i, ilk in enumerate(ip_loglari):
            penceredekiler = [l for l in ip_loglari[i:] if l["zaman"] - ilk["zaman"] <= pencere]
            kullanicilar = {l["kullanici_adi"] for l in penceredekiler}
            if len(kullanicilar) >= esik:
                bulgular.append({
                    "ip_adresi": ip,
                    "log_idler": [l["id"] for l in penceredekiler],
                    "aciklama": f"{len(kullanicilar)} farklı kullanıcı adı denendi",
                })
                break
    return bulgular


def basarisizdan_basariya_bul(loglar, esik, pencere_dk):
    """Aynı IP'den pencere içinde en az esik başarısız girişin ardından
    başarılı giriş gelirse yakalar (parola tahmin edilmiş olabilir)."""
    pencere = timedelta(minutes=pencere_dk)
    bulgular = []
    for ip, ip_loglari in _ip_gruplari(loglar).items():
        for log in ip_loglari:
            if log["durum"] != "basarili":
                continue
            onceki_hatalar = [
                l for l in ip_loglari
                if l["durum"] == "basarisiz" and log["zaman"] - pencere <= l["zaman"] < log["zaman"]
            ]
            if len(onceki_hatalar) >= esik:
                bulgular.append({
                    "ip_adresi": ip,
                    "log_idler": [l["id"] for l in onceki_hatalar] + [log["id"]],
                    "aciklama": f"{len(onceki_hatalar)} başarısız denemenin ardından "
                                f"'{log['kullanici_adi']}' ile başarılı giriş",
                })
                break
    return bulgular


def mesai_disi_bul(loglar, baslangic=MESAI_BASLANGIC, bitis=MESAI_BITIS):
    """Mesai saatleri dışındaki BAŞARILI girişleri yakalar.
    Aynı kullanıcı aynı gün için tek bulgu üretilir."""
    gruplar = {}
    for log in loglar:
        saat = log["zaman"].hour
        if log["durum"] == "basarili" and (saat < baslangic or saat >= bitis):
            anahtar = (log["kullanici_adi"], log["zaman"].date())
            gruplar.setdefault(anahtar, []).append(log)
    return [
        {
            "ip_adresi": grup[0]["ip_adresi"],
            "log_idler": [l["id"] for l in grup],
            "aciklama": f"'{kullanici}' mesai dışında giriş yaptı ({grup[0]['zaman']:%H:%M})",
        }
        for (kullanici, _), grup in gruplar.items()
    ]


KURAL_FONKSIYONLARI = {
    "cok_basarisiz_giris": cok_basarisiz_giris_bul,
    "cok_kullanici_denemesi": cok_kullanici_denemesi_bul,
    "basarisizdan_basariya": basarisizdan_basariya_bul,
}


def kurallari_uygula(loglar, kurallar):
    """Şirketin aktif kurallarını loglara uygular, tüm bulguları döndürür.

    İş kuralı: pasif kural ve eşiği/penceresi eksik kural çalıştırılmaz.
    """
    sonuc = []
    for kural in kurallar:
        if not kural["aktif"]:
            continue
        tur = kural["kural_turu"]
        if tur == "mesai_disi":
            bulgular = mesai_disi_bul(loglar)
        elif tur in KURAL_FONKSIYONLARI and kural["esik"] and kural["pencere_dk"]:
            bulgular = KURAL_FONKSIYONLARI[tur](loglar, kural["esik"], kural["pencere_dk"])
        else:
            continue
        for b in bulgular:
            b["kural_id"] = kural["id"]
            b["kural_adi"] = kural["ad"]
            b.setdefault("aciklama", f"{len(b['log_idler'])} başarısız giriş")
            sonuc.append(b)
    return sonuc