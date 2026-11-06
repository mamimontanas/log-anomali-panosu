/* Migration 02: anomali tablosuna açıklama kolonu (Hafta 7)
   Kolon zaten varsa tekrar eklemez, script güvenle tekrar çalıştırılabilir. */
USE LogAnomali;
GO

IF COL_LENGTH('anomali', 'aciklama') IS NULL
    ALTER TABLE anomali ADD aciklama NVARCHAR(400) NULL;
GO