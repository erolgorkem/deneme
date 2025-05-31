import os
import pandas as pd
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

dataframe = None  # Global değişken: Yüklenen Excel verisi burada tutulacak

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global dataframe
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith(('.xls', '.xlsx')):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            dataframe = pd.read_excel(filepath)
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
def show_table():
    global dataframe
    if dataframe is None:
        return "Henüz bir dosya yüklenmedi.", 404
    html_table = dataframe.to_html(classes='table table-hover table-bordered align-middle text-center', index=False)
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Yüklenen Excel Tablosu</title>
      <meta charset="utf-8">
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
      <style>
        body { background-color: #f4f6f8; }
        .container { margin-top: 40px; }
        h2 { margin-bottom: 30px; }
        .table { font-size: 1.05rem; border-radius: 15px; overflow: hidden; }
        th { background: #007bff; color: #fff; }
        td, th { vertical-align: middle !important; }
      </style>
    </head>
    <body>
      <div class="container">
        <h2 class="text-primary">Yüklenen Excel Tablosu</h2>
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
