from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "gizli_anahtar"  # Flash mesajlar için

# --- Dosya yükleme limiti (örneğin 100 MB) ---
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("Dosya seçilmedi!")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("Dosya adı boş!")
            return redirect(request.url)
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            try:
                df = pd.read_excel(filepath)
                # --- Örneğin: İlk 5 satırı yazdır (test amaçlı) ---
                print(df.head())
                flash(f"{file.filename} başarıyla yüklendi! Satır sayısı: {len(df)}")
            except Exception as e:
                flash(f"HATA: {str(e)}")
                return redirect(request.url)
            return redirect(url_for('upload_file'))
    return '''
    <!doctype html>
    <title>Excel Dosyası Yükle</title>
    <h1>Excel Dosyası Yükle (.xlsx)</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Yükle>
    </form>
    '''

if __name__ == "__main__":
    # Sunucuyu dışarıya aç, debug aktif
    app.run(debug=True, host="0.0.0.0", port=5000)
