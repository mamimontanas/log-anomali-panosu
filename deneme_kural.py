from app.business.kural_motoru import kurallari_uygula
from app.business.log_parser import dosya_ayristir

with open("sample_logs/saldiri_senaryosu.log", encoding="utf-8") as dosya:
    kayitlar, _ = dosya_ayristir(dosya)
for no, k in enumerate(kayitlar, start=1):
    k["id"] = no

kurallar = [
    {"id": 1, "ad": "Çok sayıda başarısız giriş", "kural_turu": "cok_basarisiz_giris", "esik": 5, "pencere_dk": 10, "aktif": True},
    {"id": 2, "ad": "Çok sayıda kullanıcı adı denemesi", "kural_turu": "cok_kullanici_denemesi", "esik": 5, "pencere_dk": 15, "aktif": True},
    {"id": 3, "ad": "Başarısızlıktan sonra başarılı giriş", "kural_turu": "basarisizdan_basariya", "esik": 5, "pencere_dk": 30, "aktif": True},
    {"id": 4, "ad": "Mesai dışı giriş", "kural_turu": "mesai_disi", "esik": None, "pencere_dk": None, "aktif": True},
]

for b in kurallari_uygula(kayitlar, kurallar):
    print(f"{b['onem']:<7} {b['kural_adi']:<38} {b['ip_adresi']:<15} {b['aciklama']}")