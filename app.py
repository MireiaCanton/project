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
    
    cursor.execute('''
        SELECT products.id, products.title, products.description, products.photo, 
            products.price, categories.name AS category_name, products.seller_id, 
            products.created, products.updated
        FROM products
        JOIN categories ON products.category_id = categories.id;

    ''')
    
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
        fecha=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if categoria == 'Electrònica':
            categoria = 1
        elif categoria == 'Roba':
            categoria = 2
        elif categoria == 'Joguines':
            categoria = 3

        # Verifica si se proporcionó una imagen
        if 'foto' not in request.files:
            error_message = "Se requiere una imagen."
            return render_template('products/create.html', error_message=error_message)

        file = request.files['foto']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ruta = VIEW_FOLDER + filename

            db = sqlite3.connect(DATABASE)
            cursor = db.cursor()
            cursor.execute('INSERT INTO products (title, description, photo, price, category_id, created) VALUES (?, ?, ?, ?, ?,?)', (nombreP, descripcion, ruta, precioP, categoria, fecha))
            db.commit()
            db.close()

            return redirect('/products/list')
        else:
            error_message = "El archivo de imagen no es válido. Asegúrate de que sea una imagen válida (ej. PNG, JPG, JPEG, GIF)."
            return render_template('products/create.html', error_message=error_message)
    else:
        return render_template('products/create.html')


##READ
@app.route('/products/read/<int:product_id>')
def view_product(product_id):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    cursor.execute('''
    SELECT products.id, products.title, products.description, products.photo, 
           products.price, categories.name AS category_name, products.seller_id, 
           products.created, products.updated
    FROM products
    JOIN categories ON products.category_id = categories.id
    WHERE products.id = ?
''', (product_id,))

    data = cursor.fetchone()
    db.close()

    if data:
        return render_template('products/read.html', product=data)
    else:
        return redirect('/products/list')

##DELETE
@app.route('/products/delete/<int:product_id>', methods=['GET', 'POST'])
def delete_confirmation(product_id):
    if request.method == 'POST':
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute(f'DELETE FROM products WHERE id = ?', (product_id,))
        db.commit()
        db.close()
        return redirect('/products/list')
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM products WHERE id = ?', (product_id,))
    data = cursor.fetchone()
    db.close()

    if data:
        return render_template('products/delete.html', product=data)
    else:
        return "El registro no se encontró."


##UPDATE

@app.route('/products/update/<int:product_id>', methods=['POST', 'GET'])
def editar_producto(product_id):
    if request.method == 'POST':
        nombreP = request.form['nombre']
        precioP = request.form['precio']
        descripcion = request.form['descripcion']
        categoria = request.form['categoria']
        fecha=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if categoria == 'Electrónica':
            categoria = 1
        elif categoria == 'Ropa':
            categoria = 2
        elif categoria == 'Joguines':
            categoria = 3
        if 'foto' in request.files:
            file = request.files['foto']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                ruta = VIEW_FOLDER+filename
            else:
                ruta = None  
        else:
            ruta = None

        
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        if ruta == None:
            cursor.execute(
            'UPDATE products SET title=?, description=?, price=?, category_id=?, updated=? WHERE id=?',
            (nombreP, descripcion, precioP, categoria, fecha, product_id)
        )
        else:
            cursor.execute(
            'UPDATE products SET title=?, description=?, price=?, category_id=?, photo=?, updated=? WHERE id=?',
            (nombreP, descripcion, precioP, categoria, ruta, fecha, product_id)
        )
        db.commit()
        db.close()

        return redirect('/products/list')  
    else:
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        db.close()

        if product:
            return render_template('products/update.html', product=product, product_id=product_id)
        else:
            return redirect('/products/list') 

