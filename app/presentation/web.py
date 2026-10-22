import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for

from app.business.auth import parola_dogrula, parola_hashle
from app.data import crud

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


@app.route("/")
def ana_sayfa():
    return render_template("ana.html")


@app.route("/kayit", methods=["GET", "POST"])
def kayit():
    if request.method == "POST":
        sirket = request.form.get("sirket", "").strip()
        kadi = request.form.get("kullanici_adi", "").strip()
        parola = request.form.get("parola", "")

        if not sirket or not kadi:
            flash("Şirket adı ve kullanıcı adı boş olamaz.")
        elif len(parola) < 8:
            flash("Parola en az 8 karakter olmalı.")
        else:
            try:
                crud.sirket_ve_yonetici_ekle(sirket, kadi, parola_hashle(parola))
                flash("Kayıt tamamlandı.")
                return redirect(url_for("ana_sayfa"))
            except ValueError as hata:
                flash(str(hata))
    return render_template("kayit.html")


@app.route("/giris", methods=["GET", "POST"])
def giris():
    if request.method == "POST":
        kadi = request.form.get("kullanici_adi", "").strip()
        parola = request.form.get("parola", "")

        kullanici = crud.kullanici_getir(kadi)
        if kullanici and parola_dogrula(parola, kullanici["parola_hash"]):
            session.clear()
            session["kullanici_id"] = kullanici["id"]
            session["sirket_id"] = kullanici["sirket_id"]
            session["kullanici_adi"] = kullanici["kullanici_adi"]
            session["rol"] = kullanici["rol"]
            flash("Giriş başarılı.")
            return redirect(url_for("pano"))
        else:
            flash("Kullanıcı adı veya parola hatalı.")

    return render_template("giris.html")


@app.route("/pano")
def pano():
    if "kullanici_id" not in session:
        flash("Önce giriş yapın.")
        return redirect(url_for("giris"))
    loglar = crud.son_loglar(session["sirket_id"], adet=10)
    return render_template("pano.html", loglar=loglar)


@app.route("/cikis")
def cikis():
    session.clear()
    flash("Çıkış yapıldı.")
    return redirect(url_for("giris"))


if __name__ == "__main__":
    app.run(debug=True)