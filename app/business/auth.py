import bcrypt


def parola_hashle(parola):
    """Düz parolayı alır, hash'lenmiş METİN döndürür."""
    
    # bcrypt.hashpw() fonksiyonu bytes tipinde veri bekler, bu yüzden encode ediyoruz.
    parola_bytes = parola.encode('utf-8')
    # Salt oluştur ve parolayı hashle
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(parola_bytes, salt)
    # Hash'i metin olarak döndür
    return hashed.decode('utf-8')


def parola_dogrula(parola, kayitli_hash):
    """Girilen parola kayıtlı hash ile eşleşiyorsa True, yoksa False döndürür."""
    
    # bcrypt.checkpw() fonksiyonu bytes tipinde veri bekler, bu yüzden encode ediyoruz.
    parola_bytes = parola.encode('utf-8')
    kayitli_hash_bytes = kayitli_hash.encode('utf-8')
    # Parolayı doğrula
    return bcrypt.checkpw(parola_bytes, kayitli_hash_bytes)
    