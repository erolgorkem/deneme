import os
import pandas as pd
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# Yüklenen veriyi hafızada tutacak global değişken
dataframe = None

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
        <h2>Excel Yükle</h2>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".xls,.xlsx">
            <input type="submit" value="Yükle">
        </form>
    '''

@app.route('/table')
def show_table():
    global dataframe
    if dataframe is None:
        return "Henüz bir dosya yüklenmedi.", 404
    # HTML tabloya dönüştür
    html_table = dataframe.to_html(classes='table table-striped', index=False)
    return f'''
        <h2>Yüklenen Excel Tablosu</h2>
        {html_table}
        <a href="/">Yeni dosya yükle</a>
    '''

if __name__ == '__main__':
    app.run(debug=True)
