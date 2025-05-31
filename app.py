import os
import pandas as pd
from flask import Flask, request, render_template_string, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'gorkem-bey-ozel-sifre'

dataframe = None

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Kolonlar ve sırası senin verdiğin gibi:
ISTENEN_KOLONLAR = [
    "Sipariş Statüsü",
    "Sipariş Tarihi",
    "Teslim Tarihi",
    "Sipariş Numarası",
    "Barkod",
    "Stok Kodu",
    "Adet",
    "Alıcı",
    "Paket No",
    "Kargo Firması",
    "Kargo Kodu",
    "Ürün Adı",
    "Birim Fiyatı",
    "Satış Tutarı",
    "İndirim Tutarı",
    "Faturalanacak Tutar",
    "Komisyon Oranı",
    "Teslimat Adresi",
    "İl",
    "İlçe"
]

KULLANICI_ADI = "admin"
SIFRE = "bilmiyorum"

def giris_gerekli(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('giris'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/login', methods=['GET', 'POST'])
def login():
    hata = None
    if request.method == 'POST':
        kullanici = request.form.get('kullanici')
        sifre = request.form.get('sifre')
        if kullanici == KULLANICI_ADI and sifre == SIFRE:
            session['giris'] = True
            return redirect(url_for('upload_file'))
        else:
            hata = "Kullanıcı adı veya şifre yanlış!"
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Giriş Yap</title>
            <meta charset="utf-8">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { background-color: #f4f6f8; }
                .container { margin-top: 120px; }
            </style>
        </head>
        <body>
            <div class="container col-md-4 mx-auto text-center">
                <h2 class="text-primary mb-4">Giriş Yap</h2>
                <form method="post" class="border rounded-4 p-5 shadow bg-white">
                    <input type="text" name="kullanici" placeholder="Kullanıcı Adı" class="form-control mb-3" required autofocus>
                    <input type="password" name="sifre" placeholder="Şifre" class="form-control mb-4" required>
                    {% if hata %}
                        <div class="alert alert-danger mb-3">{{ hata }}</div>
                    {% endif %}
                    <button type="submit" class="btn btn-success btn-lg rounded-pill px-5">Giriş</button>
                </form>
            </div>
        </body>
        </html>
    """, hata=hata)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@giris_gerekli
def upload_file():
    global dataframe
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith(('.xls', '.xlsx')):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            df = pd.read_excel(filepath)
            try:
                dataframe = df[ISTENEN_KOLONLAR]
            except KeyError as e:
                eksik_kolonlar = set(ISTENEN_KOLONLAR) - set(df.columns)
                return f"Yüklenen Excel'de şu kolon(lar) eksik: {', '.join(eksik_kolonlar)}", 400
            return redirect(url_for('show_table'))
        else:
            return "Yalnızca Excel dosyası yükleyebilirsin.", 400

    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Excel Yükle</title>
            <meta charset="utf-8">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { background-color: #f4f6f8; }
                .container { margin-top: 80px; }
                h2 { margin-bottom: 30px; }
            </style>
        </head>
        <body>
            <div class="container text-center">
                <div style="position:absolute;top:18px;right:28px;">
                    <a href="/logout" class="btn btn-outline-danger">Çıkış Yap</a>
                </div>
                <h2 class="text-success">Excel Dosyanı Yükle</h2>
                <form method="post" enctype="multipart/form-data" class="border rounded-4 p-5 shadow bg-white">
                    <input type="file" name="file" accept=".xls,.xlsx" class="form-control mb-4" required>
                    <button type="submit" class="btn btn-primary btn-lg rounded-pill px-5">Yükle</button>
                </form>
            </div>
        </body>
        </html>
    '''

@app.route('/table')
@giris_gerekli
def show_table():
    global dataframe
    if dataframe is None:
        return "Henüz bir dosya yüklenmedi.", 404

    html_table = dataframe.to_html(
        classes='table table-hover table-bordered align-middle text-center compact-table',
        index=False,
        table_id='veriTablosu'
    )

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Yüklenen Excel Tablosu</title>
      <meta charset="utf-8">
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
      <style>
        body { background-color: #f4f6f8; }
        .container { margin-top: 25px; max-width: 99vw; }
        h2 { margin-bottom: 16px; font-size: 1.4rem; }
        .compact-table {
          font-size: 0.90rem;
        }
        .compact-table th, .compact-table td {
          padding-top: 3px !important;
          padding-bottom: 3px !important;
          padding-left: 5px !important;
          padding-right: 5px !important;
          white-space: nowrap;
        }
        .table { border-radius: 12px; overflow: hidden; }
        th { background: #007bff; color: #fff; }
        td, th { vertical-align: middle !important; }
        .table-responsive { max-height: 70vh; overflow-x: auto; }
        .arama-kutusu { margin-bottom: 14px; max-width: 350px;}
      </style>
      <script>
        function filtreleTablo() {
          var input = document.getElementById("aramaInput");
          var filtre = input.value.toLowerCase();
          var tablo = document.getElementById("veriTablosu");
          var tr = tablo.getElementsByTagName("tr");
          for (var i = 1; i < tr.length; i++) {
            var tds = tr[i].getElementsByTagName("td");
            var satirGoster = false;
            for (var j = 0; j < tds.length; j++) {
              if (tds[j].textContent.toLowerCase().indexOf(filtre) > -1) {
                satirGoster = true;
                break;
              }
            }
            tr[i].style.display = satirGoster ? "" : "none";
          }
        }
      </script>
    </head>
    <body>
      <div class="container-fluid">
        <div style="position:absolute;top:18px;right:28px;">
            <a href="/logout" class="btn btn-outline-danger">Çıkış Yap</a>
        </div>
        <h2 class="text-primary">Yüklenen Excel Tablosu</h2>
        <input type="text" id="aramaInput" class="form-control arama-kutusu" placeholder="Tabloda ara..." onkeyup="filtreleTablo()">
        <div class="table-responsive shadow rounded-4">
          {{ table|safe }}
        </div>
        <div class="mt-4">
          <a href="/" class="btn btn-success btn-lg rounded-pill px-5">Yeni dosya yükle</a>
        </div>
      </div>
    </body>
    </html>
    """, table=html_table)

if __name__ == '__main__':
    app.run(debug=True)
