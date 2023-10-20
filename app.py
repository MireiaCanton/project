import sqlite3, os
from flask import Flask, g, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + basedir + "/database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['UPLOAD_FOLDER'] = './static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
VIEW_FOLDER='/static/img/'

db = SQLAlchemy(app)

from flask_sqlalchemy import SQLAlchemy


class Categoria(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True)
    slug = db.Column(db.Text, unique=True)

class Producto(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    photo = db.Column(db.Text)
    price = db.Column(db.DECIMAL(10, 2))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)
    updated = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)
    category = db.relationship('Categoria', backref=db.backref('products', lazy=True))
    
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Add user attributes here

##LIST
@app.route('/products/list')
def index():
    #products = db.session.query(Producto, Categoria.name).join(Categoria, Producto.category_id == Categoria.id).add_columns(Producto.id, Producto.title, Producto.description, Producto.photo, Producto.price, Producto.created, Producto.updated).all()
    #category_names = [product[1] for product in products]

    products = db.session.query(Producto).all()

    return render_template('products/template.html', data=products)

if __name__ == "__main__":
    app.run(debug=True)


##READ
@app.route('/products/read/<int:product_id>')
def view_product(product_id):
    products = db.session.query(Producto, Categoria.name).join(Categoria, Producto.category_id == Categoria.id).filter(Producto.id == product_id).add_columns(Producto.id, Producto.title, Producto.description, Producto.photo, Producto.price, Producto.created, Producto.updated).all()
    category_names = [product[1] for product in products]

    return render_template('products/read.html', data=products)

if __name__ == "__main__":
    app.run(debug=True)

##CREATE
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/products/create', methods=['GET', 'POST'])
def crear_producto():
    if request.method == 'POST':
        nombreP = request.form['nombre']
        precioP = request.form['precio']
        descripcion = request.form['descripcion']
        categoria = request.form['categoria']
        fecha = datetime.now()

        if categoria == 'Electrónica':
            categoria_id = 1
        elif categoria == 'Ropa':
            categoria_id = 2
        elif categoria == 'Juguetes':
            categoria_id = 3

        if 'foto' not in request.files:
            return render_template('products/create.html', error_message="Se requiere una imagen.")

        file = request.files['foto']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ruta = VIEW_FOLDER + filename

            new_product = Producto(title=nombreP, description=descripcion, photo=ruta, price=precioP, category_id=categoria_id)
            db.session.add(new_product)
            db.session.commit()
            return redirect('/products/list')
        else:
            error_message = "El archivo de imagen no es válido. Asegúrate de que sea una imagen válida (ej. PNG, JPG, JPEG, GIF)."
            return render_template('products/create.html', error_message=error_message)
    else:
        return render_template('products/create.html')


##UPDATE
@app.route('/products/update/<int:product_id>', methods=['GET', 'POST'])
def editar_producto(product_id):
    product = Producto.query.get(product_id)
    if not product:
        return "Producto no encontrado"
    if request.method == 'POST':
        nombreP = request.form['nombre']
        precioP = request.form['precio']
        descripcion = request.form['descripcion']
        categoria = request.form['categoria']
        if categoria == 'Electrónica':
            categoria_id = 1
        elif categoria == 'Ropa':
            categoria_id = 2
        elif categoria == 'Juguetes':
            categoria_id = 3


        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if 'foto' in request.files:
            file = request.files['foto']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                ruta = VIEW_FOLDER + filename
            else:
                ruta = None
        else:
            ruta = None

        product.title = nombreP
        product.description = descripcion
        product.price = precioP
        product.category_id = categoria_id
        product.updated = fecha
        if ruta:
            product.photo = ruta

        db.session.commit()
        return redirect('/products/list')

    return render_template('products/update.html', product=product, product_id=product_id)

##DELETE
@app.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = 'ads'
    if product:        
        db.session.delete(product)
        db.session.commit()
        return redirect('/products/list')
    else:
        return "Producto no encontrado"
    



if __name__ == '__main__':
    app.run(debug=True)