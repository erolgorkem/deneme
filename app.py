from flask import Flask, request, redirect, url_for, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "gizli_anahtar"

# Dosya yükleme limiti: 100 MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    message = ""
    if request.method == "POST":
        if "file" not in request.files:
            message = "Dosya seçilmedi!"
            return html(message)
        file = request.files["file"]
        if file.filename == "":
            message = "Dosya adı boş!"
            return html(message)
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        try:
            df = pd.read_excel(filepath)
            # Test amaçlı: ilk 5 satırı terminale yaz
            print(df.head())
            message = f"{file.filename} başarıyla yüklendi! Satır sayısı: {len(df)}"
        except Exception as e:
            message = f"HATA: {str(e)}"
        return html(message)
    return html(message)

def html(message=""):
    return f"""
    <!doctype html>
    <title>Excel Dosyası Yükle</title>
    <h1>Excel Dosyası Yükle (.xlsx)</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Yükle>
    </form>
    <p style='color:red'>{message}</p>
    """

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
    
