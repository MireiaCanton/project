import sqlite3, os
from flask import Flask, g, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = '/static/img'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/products/create', methods=['POST', 'GET'])
def crear_producto():
    if request.method == 'POST':
        nombreP = request.form['nombre']
        precioP = request.form['precio']
        descripcion = request.form['descripcion']
        categoria = request.form['categoria']
        if categoria == 'Electrònica':
            categoria = 1
        elif categoria == 'Roba':
            categoria = 2
        else:
            categoria = 3
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.file['foto']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute('INSERT INTO products (title, description, photo, price, category_id) VALUES (?, ?, ?, ?, ?)', (nombreP, descripcion, ruta, precioP, categoria ))
        db.commit()
        db.close()
        return render_template('/products/template.html')
    else:
        return render_template('products/create.html')

