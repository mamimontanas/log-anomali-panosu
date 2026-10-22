import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from app.business.auth import parola_hashle
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


if __name__ == "__main__":
    app.run(debug=True)