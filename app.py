import os
import pandas as pd
from flask import Flask, request, render_template_string, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'gorkem-bey-ozel-sifre'

SIPARIS_UPLOAD = 'uploads_siparis'
MALIYET_UPLOAD = 'uploads_maliyet'
for folder in [SIPARIS_UPLOAD, MALIYET_UPLOAD]:
    if not os.path.exists(folder):
        os.makedirs(folder)

SIPARIS_KOLONLAR = [
    "Sipariş Statüsü", "Sipariş Tarihi", "Teslim Tarihi", "Sipariş Numarası", "Barkod",
    "Stok Kodu", "Adet", "Alıcı", "Paket No", "Kargo Firması", "Kargo Kodu", "Ürün Adı",
    "Birim Fiyatı", "Satış Tutarı", "İndirim Tutarı", "Faturalanacak Tutar", "Komisyon Oranı",
    "Teslimat Adresi", "İl", "İlçe"
]
MALIYET_KOLONLAR = [
    "Barkod", "Model Kodu", "Stok Kodu", "Kategori", "Ürün Adı",
    "Trendyol Satış Fiyatı", "Ürün Maliyeti (KDV Dahil)"
]
KULLANICI_ADI = "admin"
SIFRE = "bilmiyorum"

siparis_df = None
maliyet_df = None

def giris_gerekli(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('giris'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def kolon_eslestir(df, aranan_kolonlar):
    # Küçük harfe, boşluğa, noktalama işaretine duyarsız başlık eşleştirme
    temiz = lambda s: ''.join(str(s).lower().replace(' ', '').replace('\n','').replace('-','').replace('(','').replace(')','').replace('_',''))
    df_cols = {temiz(col):col for col in df.columns}
    sonuclar = []
    for aranan in aranan_kolonlar:
        anahtar = temiz(aranan)
        sonuclar.append(df_cols.get(anahtar, None))
    return sonuclar

@app.route('/login', methods=['GET', 'POST'])
def login():
    hata = None
    if request.method == 'POST':
        kullanici = request.form.get('kullanici')
        sifre = request.form.get('sifre')
        if kullanici == KULLANICI_ADI and sifre == SIFRE:
            session['giris'] = True
            return redirect(url_for('index'))
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

@app.route('/')
@giris_gerekli
def index():
    return redirect(url_for('siparis'))

@app.route('/siparis', methods=['GET', 'POST'])
@giris_gerekli
def siparis():
    global siparis_df
    hata = None
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith(('.xls', '.xlsx')):
            filepath = os.path.join(SIPARIS_UPLOAD, file.filename)
            file.save(filepath)
            try:
                df = pd.read_excel(filepath)
                eslesen_kolonlar = kolon_eslestir(df, SIPARIS_KOLONLAR)
                # Kolon sırası bozulmadan ve eksikler None olacak şekilde DataFrame oluştur
                siparis_df = pd.DataFrame()
                for hedef, kaynak in zip(SIPARIS_KOLONLAR, eslesen_kolonlar):
                    if kaynak:
                        siparis_df[hedef] = df[kaynak]
                    else:
                        siparis_df[hedef] = ""
                # Tarih kolonlarını biçimlendir
                for kol in ["Sipariş Tarihi", "Teslim Tarihi"]:
                    if kol in siparis_df.columns:
                        siparis_df[kol] = pd.to_datetime(siparis_df[kol], errors='coerce').dt.strftime('%Y-%m-%d')
            except Exception as e:
                hata = f"Excel kolonlarında eksik veya hatalı başlık var: {str(e)}"
    return render_sablon(
        aktif_tab="siparis",
        tablo_df=siparis_df,
        kolonlar=SIPARIS_KOLONLAR,
        yukleme_hatasi=hata
    )

@app.route('/maliyet', methods=['GET', 'POST'])
@giris_gerekli
def maliyet():
    global maliyet_df
    hata = None
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith(('.xls', '.xlsx')):
            filepath = os.path.join(MALIYET_UPLOAD, file.filename)
            file.save(filepath)
            try:
                df = pd.read_excel(filepath)
                eslesen_kolonlar = kolon_eslestir(df, MALIYET_KOLONLAR)
                maliyet_df = pd.DataFrame()
                for hedef, kaynak in zip(MALIYET_KOLONLAR, eslesen_kolonlar):
                    if kaynak:
                        maliyet_df[hedef] = df[kaynak]
                    else:
                        maliyet_df[hedef] = ""
            except Exception as e:
                hata = f"Excel kolonlarında eksik veya hatalı başlık var: {str(e)}"
    return render_sablon(
        aktif_tab="maliyet",
        tablo_df=maliyet_df,
        kolonlar=MALIYET_KOLONLAR,
        yukleme_hatasi=hata
    )

def render_sablon(aktif_tab, tablo_df, kolonlar, yukleme_hatasi=None):
    tarih_kolonlari = [k for k in kolonlar if "Tarih" in k]
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Excel Paneli</title>
      <meta charset="utf-8">
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
      <link href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css" rel="stylesheet">
      <style>
        body { background-color: #f4f6f8; }
        .container { margin-top: 30px; max-width: 99vw; }
        .compact-table { font-size: 0.90rem; }
        .compact-table th, .compact-table td {
          padding-top: 3px !important; padding-bottom: 3px !important;
          padding-left: 5px !important; padding-right: 5px !important;
          white-space: nowrap;
        }
        .table { border-radius: 12px; overflow: hidden; }
        th { background: #007bff; color: #fff; cursor: pointer;}
        td, th { vertical-align: middle !important; }
        .table-responsive { max-height: 65vh; overflow-x: auto; }
        .arama-kutusu { margin-bottom: 12px; max-width: 320px;}
        .tabnav { margin-bottom: 14px; }
        .yukle-kart {max-width:450px; margin:auto; margin-bottom:15px;}
        .gizli {display:none;}
      </style>
      <script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
      <script>
        function filtreleTablo() {
          var input = document.getElementById("aramaInput");
          var filtre = input.value.toLowerCase();
          var tablo = document.getElementById("veriTablosu");
          var tr = tablo ? tablo.getElementsByTagName("tr") : [];
          for (var i = 1; i < tr.length; i++) {
            var tds = tr[i].getElementsByTagName("td");
            var satirGoster = false;
            for (var j = 0; j < tds.length; j++) {
              if (tds[j].textContent.toLowerCase().indexOf(filtre) > -1) {
                satirGoster = true; break;
              }
            }
            tr[i].style.display = satirGoster ? "" : "none";
          }
        }
        function tarihAraligiFiltrele(kolonIndex) {
          var tablo = document.getElementById("veriTablosu");
          var baslangic = document.getElementById("tarihBaslangic" + kolonIndex).value;
          var bitis = document.getElementById("tarihBitis" + kolonIndex).value;
          var tr = tablo ? tablo.getElementsByTagName("tr") : [];
          for (var i = 1; i < tr.length; i++) {
            var td = tr[i].getElementsByTagName("td")[kolonIndex];
            if (!td) continue;
            var deger = td.textContent.trim();
            if (baslangic && bitis && deger) {
              if (deger >= baslangic && deger <= bitis) {
                tr[i].style.display = "";
              } else {
                tr[i].style.display = "none";
              }
            } else {
              tr[i].style.display = "";
            }
          }
        }
        function tarihFiltreAc(kolonIndex) {
          document.getElementById("tarihFiltrePanel" + kolonIndex).style.display = "block";
          flatpickr("#tarihBaslangic" + kolonIndex, {dateFormat: "Y-m-d"});
          flatpickr("#tarihBitis" + kolonIndex, {dateFormat: "Y-m-d"});
        }
        function tarihFiltreKapat(kolonIndex) {
          document.getElementById("tarihFiltrePanel" + kolonIndex).style.display = "none";
          document.getElementById("tarihBaslangic" + kolonIndex).value = "";
          document.getElementById("tarihBitis" + kolonIndex).value = "";
          tarihAraligiFiltrele(kolonIndex);
        }
      </script>
    </head>
    <body>
      <div class="container-fluid">
        <div style="position:absolute;top:18px;right:28px;">
            <a href="/logout" class="btn btn-outline-danger">Çıkış Yap</a>
        </div>
        <ul class="nav nav-tabs tabnav">
          <li class="nav-item">
            <a class="nav-link {% if aktif_tab == 'siparis' %}active{% endif %}" href="/siparis">Sipariş Exceli</a>
          </li>
          <li class="nav-item">
            <a class="nav-link {% if aktif_tab == 'maliyet' %}active{% endif %}" href="/maliyet">Maliyet Exceli</a>
          </li>
        </ul>
        <div class="card yukle-kart shadow-sm border-0">
          <div class="card-body p-3">
            <h5 class="card-title text-primary mb-3" style="font-size:1.1rem;">
              {% if aktif_tab == 'siparis' %}Sipariş Exceli Yükle{% else %}Maliyet Exceli Yükle{% endif %}
            </h5>
            <form method="post" enctype="multipart/form-data">
              <input type="file" name="file" accept=".xls,.xlsx" class="form-control form-control-sm mb-2" required>
              <button type="submit" class="btn btn-primary btn-sm rounded-pill px-4">Yükle</button>
            </form>
            {% if yukleme_hatasi %}
              <div class="alert alert-danger mt-2 mb-0 p-2" style="font-size:0.96em;">{{ yukleme_hatasi }}</div>
            {% endif %}
          </div>
        </div>
        <div class="mt-3 mb-2 {% if tablo_df is none %}gizli{% endif %}">
          <input type="text" id="aramaInput" class="form-control arama-kutusu" placeholder="Tabloda ara..." onkeyup="filtreleTablo()">
        </div>
        <div class="table-responsive shadow rounded-4" style="background:white;">
          {% if tablo_df is not none %}
            <table class="table table-hover table-bordered align-middle text-center compact-table" id="veriTablosu">
              <thead>
                <tr>
                  {% for kol in kolonlar %}
                    <th onclick="{% if 'Tarih' in kol %}tarihFiltreAc({{ loop.index0 }}){% else %}void(0);{% endif %}">
                      {{kol}}
                      {% if 'Tarih' in kol %}
                        <span style="font-size:0.85em; color:#ffb100;">&#128197;</span>
                        <div id="tarihFiltrePanel{{loop.index0}}" style="display:none; position:absolute; z-index:20; background:white; border:1px solid #ccc; padding:12px; border-radius:8px;">
                          <label>Başlangıç:</label>
                          <input type="text" id="tarihBaslangic{{loop.index0}}" class="form-control mb-2" placeholder="Başlangıç">
                          <label>Bitiş:</label>
                          <input type="text" id="tarihBitis{{loop.index0}}" class="form-control mb-2" placeholder="Bitiş">
                          <button onclick="tarihAraligiFiltrele({{loop.index0}});" class="btn btn-primary btn-sm mb-1">Filtrele</button>
                          <button onclick="tarihFiltreKapat({{loop.index0}});" class="btn btn-outline-secondary btn-sm">Temizle</button>
                        </div>
                      {% endif %}
                    </th>
                  {% endfor %}
                </tr>
              </thead>
              <tbody>
                {% for row in tablo_df[kolonlar].itertuples(index=False) %}
                  <tr>
                    {% for value in row %}
                      <td>{{ value }}</td>
                    {% endfor %}
                  </tr>
                {% endfor %}
              </tbody>
            </table>
          {% endif %}
        </div>
      </div>
    </body>
    </html>
    """, tablo_df=tablo_df, kolonlar=kolonlar, aktif_tab=aktif_tab, yukleme_hatasi=yukleme_hatasi)

if __name__ == '__main__':
    app.run(debug=True)
