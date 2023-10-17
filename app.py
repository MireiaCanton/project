import sqlite3, os
from flask import Flask, g, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime

UPLOAD_FOLDER = './static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
VIEW_FOLDER='/static/img/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATABASE = 'database.db'
@app.route('/')
def hello():
    return render_template('./hello.html')

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

@app.route('/products/list')
def index():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM products')
    data = cursor.fetchall()
    db.close()
    return render_template('/products/template.html', data=data)


##CREATE
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
        if 'foto' not in request.files:
            return redirect(request.url)
        file = request.files['foto']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ruta = VIEW_FOLDER+filename
            
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute('INSERT INTO products (title, description, photo, price, category_id) VALUES (?, ?, ?, ?, ?)', (nombreP, descripcion, ruta, precioP, categoria ))
        db.commit()
        db.close()
        return render_template('products/template.html')
    else:
        return render_template('products/create.html')



##UPDATE
# ... (your existing code)

@app.route('/products/update/<int:product_id>', methods=['POST', 'GET'])
def editar_producto(product_id):
    if request.method == 'POST':
        nombreP = request.form['nombre']
        precioP = request.form['precio']
        descripcion = request.form['descripcion']
        categoria = request.form['categoria']
        fecha=datetime.now()
        if categoria == 'Electrónica':
            categoria = 1
        elif categoria == 'Ropa':
            categoria = 2
        else:
            categoria = 3
        if 'foto' in request.files:
            file = request.files['foto']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                ruta = VIEW_FOLDER+filename
            else:
                ruta = None  # No new photo was uploaded
        else:
            ruta = None

        # Update the product in the database
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        if ruta == None:
            cursor.execute(
            'UPDATE products SET title=?, description=?, price=?, category_id=?, updated=? WHERE id=?',
            (nombreP, descripcion, precioP, categoria, product_id, fecha)
        )
        else:
            cursor.execute(
            'UPDATE products SET title=?, description=?, price=?, category_id=?, photo=?, updated=? WHERE id=?',
            (nombreP, descripcion, precioP, categoria, ruta, product_id, fecha)
        )
        db.commit()
        db.close()

        return redirect('/products/list')  # Redirect to the product listing page or a success page
    else:
        # Load the current product details from the database based on product_id
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        db.close()

        if product:
            return render_template('products/update.html', product=product, product_id=product_id)
        else:
            # Handle the case where the product with the given ID doesn't exist
            # You can redirect or show an error message
            return redirect('/products/list')  # Redirect to the product listing page

