from app.business.log_parser import dosya_ayristir
from app.data import crud

sirket_id = crud.kullanici_getir("deneme")["sirket_id"]

kaynaklar = crud.kaynaklari_getir(sirket_id)
if kaynaklar:
    kaynak_id = kaynaklar[0]["id"]
else:
    kaynak_id = crud.kaynak_ekle(sirket_id, "Web sunucusu", "web")

with open("sample_logs/ornek_giris.log", encoding="utf-8") as dosya:
    kayitlar, hatalar = dosya_ayristir(dosya)

eklenen = crud.loglar_toplu_ekle(sirket_id, kaynak_id, kayitlar)
print("Eklenen kayıt:", eklenen)
print("Atlanan hatalı satır:", len(hatalar))