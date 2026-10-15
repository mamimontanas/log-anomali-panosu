# AI Kullanım Günlüğü

**Proje:** P27 Günlük (Log) Anomali İzleme Panosu (Gözcü)
**Öğrenci:** Muhammed Berkin Tanas
**Kullanılan araç:** Claude (Anthropic), claude.ai sohbet arayüzü

Bu günlükte yapay zekâdan aldığım her anlamlı yardımı; istemi, aldığım çıktıyı ve
kendi yaptığım değişiklik veya doğrulamayı kaydediyorum.

**KVKK notu:** Yapay zekâ araçlarına gerçek kişisel veri girilmemiştir. Projedeki tüm
log verileri sentetik/örnek verilerdir.

> **Taslak notu:** `[ ... ]` ile işaretli yerleri kendi cümlelerinle doldur ya da
> yapmadığın bir şey yazıyorsa sil. Tarihleri gerçek tarihlerle düzelt.

---

## Hafta 3: Kurulum, Mimari ve Veri Modeli

### Kayıt 1: Proje yol haritası
- **Tarih:** 15.10.2026
- **İstem:** P27 projesini seçtim, ders PDF'ine göre adım adım yardım istedim.
- **Çıktı:** PDF'teki P27 bölümünün özeti, 13 haftalık plan ve Hafta 3 için yapılacaklar listesi.
- **Benim yaptığım:** Planı PDF'teki P27 bölümüyle karşılaştırdım. [Neyi kontrol ettiğini yaz.]

### Kayıt 2: Teknoloji seçimi
- **Tarih:** 15.10.2026
- **İstem:** Python ve PostgreSQL ile ilerlemek istedim, sonra veritabanını MSSQL olarak değiştirdim.
- **Çıktı:** Her iki veritabanı için kurulum adımları ve Python bağlantı yöntemi (psycopg2 ve pyodbc).
- **Benim yaptığım:** **Kararı ben verdim:** SQL Server'ı daha tanıdık bulduğum için MSSQL'e geçtim. [Gerekçeni kendi cümlenle yaz.] Python, VS Code, SQL Server Express ve SSMS kurulumlarını kendim yaptım, sanal ortam (`venv`) oluşturup Flask, pyodbc, python-dotenv ve pytest paketlerini kurdum.

### Kayıt 3: Proje fikrinin kapsamı
- **Tarih:** 15.10.2026
- **İstem:** Her şirketin kendi girişini yapıp kendi şirketinin loglarını takip edebildiği, sürekli hatalı veya şüpheli girişte uyarı veren bir panel istediğimi anlattım.
- **Çıktı:** Fikrin "çok şirketli (multi-tenant)" yapı olarak özetlenmesi, `sirket` tablosunun eklenmesi önerisi ve dört başlangıç anomali kuralı.
- **Benim yaptığım:** **Fikir bana ait.** Önerilen kuralları inceledim ve "şirketlerin giriş logları" (A seçeneği) yorumunu onayladım. [Kurallardan değiştirdiğin veya eklediğin bir şey varsa yaz.]

### Kayıt 4: ER diyagramı
- **Tarih:** 15.10.2026
- **İstem:** Proje için ER diyagramı ve varlık/ilişki önerisi istedim.
- **Çıktı:** 8 tablolu bir taslak (sirket, kullanici, kaynak, log_kaydi, kural, anomali, anomali_log, uyari) ve dbdiagram.io kodu.
- **Benim yaptığım:** Kodu dbdiagram.io'ya yapıştırıp diyagramı çizdim ve SVG olarak `docs/er_diyagrami.svg` dosyasına kaydettim. [İlişkileri nasıl doğruladığını yaz: örneğin anomali ile log arasındaki N-N ilişki için neden ara tablo gerektiğini açıkla.]

### Kayıt 5: SQL tablo scripti
- **Tarih:** 15.10.2026
- **İstem:** ER diyagramındaki tabloların SQL Server kodlarını istedim.
- **Çıktı:** `01_tablolar.sql`: 8 tablo, birincil/yabancı anahtarlar, `CHECK` kısıtları ve iki indeks.
- **Benim yaptığım:** Scripti SSMS'te çalıştırdım. Bir ara SSMS kapandı, yeniden açıp tabloları kontrol ettim ve **8 tablonun da oluştuğunu** doğruladım. [Bir kısıtı veya ilişkiyi kendi cümlenle açıkla.]

### Kayıt 6: Mimari şema
- **Tarih:** 15.10.2026
- **İstem:** Dersin istediği mimari şemayı hazırlamak için yardım istedim.
- **Çıktı:** Üç katmanlı (sunum, iş, veri) mimariyi gösteren `mimari_sema.svg`.
- **Benim yaptığım:** Dosyayı `docs` klasörüne koydum. [Katmanları kendi cümlenle açıkla: neden üç katman, her birinin görevi nedir?]

### Kayıt 7: Prototip pano ekranı
- **Tarih:** 15.10.2026
- **İstem:** Gösterilecek bir ekran istedim, ilk sürümü beğenmeyince daha estetik bir tasarım istedim.
- **Çıktı:** `pano_demo.html`: sentetik verili, çalışan bir tasarım prototipi (giriş ekranı, pano, uyarı listesi, giriş kayıtları).
- **Benim yaptığım:** Dosyayı `docs` klasörüne koyup tarayıcıda denedim. Veriler sabit yazılmış sentetik verilerdir, ekran henüz veritabanına bağlı değildir. [Kodu okuyup anladığın bölümleri ve değiştirdiğin bir şey varsa yaz.]

### Kayıt 8: Git ve GitHub
- **Tarih:** 15.10.2026
- **İstem:** Projeyi GitHub'a yüklemek için adım adım yardım istedim.
- **Çıktı:** `.gitignore`, klasör düzeni ve `git init/add/commit/push` komutları.
- **Benim yaptığım:** Git'i kurdum, `mamimontanas/log-anomali-panosu` deposunu açtım, `.gitignore` dosyasını kontrol edip `venv` ve `.env` dosyalarının yüklenmediğini doğruladım. [Hocayı iş birlikçi olarak ekledikten sonra buraya yaz.]

### Kayıt 9: README
- **Tarih:** 15.10.2026
- **İstem:** README dosyasını daha detaylı yazmasını istedim.
- **Çıktı:** Proje amacı, mimari, veritabanı, kurulum ve geliştirme planını içeren `README.md`.
- **Benim yaptığım:** [İçeriği okuyup düzelttiğin yerleri ve gerçek durumla uyuşup uyuşmadığını kontrol ettiğini yaz.]

---

## Genel değerlendirme

- Yapay zekâ **öneri ve taslak** üretti, kararları ben verdim (teknoloji seçimi, proje kapsamı).
- Her çıktıyı çalıştırarak veya inceleyerek doğruladım. Doğrulayamadığım hiçbir şeyi teslim etmedim.
- Açıklayamadığım kodu projeye koymayacağım.