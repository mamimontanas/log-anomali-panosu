/* =====================================================
   P27 - Günlük (Log) Anomali İzleme Panosu
   Veritabanı: LogAnomali (Microsoft SQL Server)
   Dosya: 01_tablolar.sql
   ===================================================== */

USE LogAnomali;
GO

/* 1) ŞİRKET: sistemdeki her müşteri şirket */
CREATE TABLE sirket (
    id                INT IDENTITY(1,1) PRIMARY KEY,
    ad                NVARCHAR(100) NOT NULL UNIQUE,
    olusturma_tarihi  DATETIME2     NOT NULL DEFAULT SYSDATETIME()
);
GO

/* 2) KULLANICI: panele giren kişiler (bir şirkete bağlı) */
CREATE TABLE kullanici (
    id             INT IDENTITY(1,1) PRIMARY KEY,
    sirket_id      INT           NOT NULL,
    kullanici_adi  NVARCHAR(50)  NOT NULL UNIQUE,
    parola_hash    NVARCHAR(255) NOT NULL,
    rol            NVARCHAR(20)  NOT NULL
                   CHECK (rol IN ('yonetici', 'analist')),
    CONSTRAINT fk_kullanici_sirket
        FOREIGN KEY (sirket_id) REFERENCES sirket(id)
);
GO

/* 3) KAYNAK: şirketin log gönderen sistemi (web sunucusu, VPN vb.) */
CREATE TABLE kaynak (
    id         INT IDENTITY(1,1) PRIMARY KEY,
    sirket_id  INT           NOT NULL,
    ad         NVARCHAR(100) NOT NULL,
    tur        NVARCHAR(50)  NULL,
    CONSTRAINT fk_kaynak_sirket
        FOREIGN KEY (sirket_id) REFERENCES sirket(id)
);
GO

/* 4) LOG_KAYDI: tek bir giriş denemesi */
CREATE TABLE log_kaydi (
    id             BIGINT IDENTITY(1,1) PRIMARY KEY,
    sirket_id      INT           NOT NULL,
    kaynak_id      INT           NOT NULL,
    zaman          DATETIME2     NOT NULL,
    ip_adresi      NVARCHAR(45)  NULL,
    kullanici_adi  NVARCHAR(100) NULL,
    durum          NVARCHAR(10)  NOT NULL
                   CHECK (durum IN ('basarili', 'basarisiz')),
    ham_metin      NVARCHAR(MAX) NULL,
    CONSTRAINT fk_log_sirket
        FOREIGN KEY (sirket_id) REFERENCES sirket(id),
    CONSTRAINT fk_log_kaynak
        FOREIGN KEY (kaynak_id) REFERENCES kaynak(id)
);
GO

/* İndeksler: "şirket + zaman" ve "şirket + IP + zaman" sorguları hızlansın */
CREATE INDEX ix_log_sirket_zaman
    ON log_kaydi (sirket_id, zaman);

CREATE INDEX ix_log_sirket_ip_zaman
    ON log_kaydi (sirket_id, ip_adresi, zaman);
GO

/* 5) KURAL: anomali tespit kuralları (şirkete özel eşikler) */
CREATE TABLE kural (
    id          INT IDENTITY(1,1) PRIMARY KEY,
    sirket_id   INT           NOT NULL,
    ad          NVARCHAR(100) NOT NULL,
    kural_turu  NVARCHAR(50)  NOT NULL
                CHECK (kural_turu IN (
                    'cok_basarisiz_giris',
                    'cok_kullanici_denemesi',
                    'basarisizdan_basariya',
                    'mesai_disi')),
    esik        INT NULL CHECK (esik > 0),
    pencere_dk  INT NULL CHECK (pencere_dk > 0),
    aktif       BIT NOT NULL DEFAULT 1,
    CONSTRAINT fk_kural_sirket
        FOREIGN KEY (sirket_id) REFERENCES sirket(id)
);
GO

/* 6) ANOMALİ: bir kuralın yakaladığı şüpheli durum */
CREATE TABLE anomali (
    id             INT IDENTITY(1,1) PRIMARY KEY,
    sirket_id      INT          NOT NULL,
    kural_id       INT          NOT NULL,
    ip_adresi      NVARCHAR(45) NULL,
    tespit_zamani  DATETIME2    NOT NULL DEFAULT SYSDATETIME(),
    onem           NVARCHAR(10) NOT NULL DEFAULT 'orta'
                   CHECK (onem IN ('dusuk', 'orta', 'yuksek')),
    ai_ozeti       NVARCHAR(MAX) NULL,
    CONSTRAINT fk_anomali_sirket
        FOREIGN KEY (sirket_id) REFERENCES sirket(id),
    CONSTRAINT fk_anomali_kural
        FOREIGN KEY (kural_id) REFERENCES kural(id)
);
GO

/* 7) ANOMALİ_LOG: ara tablo (anomali ↔ log_kaydi, çok-çok ilişki) */
CREATE TABLE anomali_log (
    anomali_id  INT    NOT NULL,
    log_id      BIGINT NOT NULL,
    CONSTRAINT pk_anomali_log PRIMARY KEY (anomali_id, log_id),
    CONSTRAINT fk_anomalilog_anomali
        FOREIGN KEY (anomali_id) REFERENCES anomali(id),
    CONSTRAINT fk_anomalilog_log
        FOREIGN KEY (log_id) REFERENCES log_kaydi(id)
);
GO

/* 8) UYARI: panelde gösterilen / gönderilen bildirim */
CREATE TABLE uyari (
    id               INT IDENTITY(1,1) PRIMARY KEY,
    anomali_id       INT          NOT NULL,
    kanal            NVARCHAR(20) NOT NULL DEFAULT 'panel',
    gonderim_zamani  DATETIME2    NOT NULL DEFAULT SYSDATETIME(),
    okundu           BIT          NOT NULL DEFAULT 0,
    CONSTRAINT fk_uyari_anomali
        FOREIGN KEY (anomali_id) REFERENCES anomali(id)
);
GO

/* =====================================================
   KONTROL: 8 tablo da oluştu mu?
   ===================================================== */
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;
GO

/* 9) KISIT: kural zaman penceresi en fazla bir gün (1440 dakika) olabilir.
      NULL değerler (mesai dışı kuralı gibi) bu kısıttan etkilenmez. */
ALTER TABLE kural
ADD CONSTRAINT ck_kural_pencere CHECK (pencere_dk <= 1440);
GO
