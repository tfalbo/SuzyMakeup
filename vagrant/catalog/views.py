import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import Base, Category, Item
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_basicauth import BasicAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///suzymakeup.db'

db = SQLAlchemy(app)


# Basic Auth
app.config['BASIC_AUTH_USERNAME'] = os.environ['SUZY_ADM']
app.config['BASIC_AUTH_PASSWORD'] = os.environ['SUZY_PASS']

basic_auth = BasicAuth(app)

## Photo Setup

app.config['UPLOADS_DEFAULT_DEST'] = "static/img"
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)


## Routes

@app.route('/')
@app.route('/categories/')
def index():
    categories = db.session.query(Category)
    items = db.session.query(Item)
    return render_template('index.html', categories = categories, items = items)


@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/items')
def indexCategory(category_id):
    categories = db.session.query(Category)
    category = db.session.query(Category).filter_by(id=category_id).one()
    items = db.session.query(Item).filter_by(category_id = category_id)
    return render_template('category.html', categories = categories, category = category, items = items)

@app.route('/categories/<int:category_id>/items/<int:item_id>/')
def indexItem(category_id, item_id):
    categories = db.session.query(Category)
    item = db.session.query(Item).filter_by(id = item_id).one()
    return render_template('item.html', categories = categories, item = item)



## Admin route

@app.route('/admin/')
@app.route('/admin/categories/')
@basic_auth.required
def showCategories():
    categories = db.session.query(Category)
    return render_template('admin/categories.html', categories = categories)

@app.route('/admin/categories/new/', methods=['GET', 'POST'])
@basic_auth.required
def newCategory():
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        db.session.add(newCategory)
        db.session.commit()
        return redirect(url_for('showCategories'))
    else:
        categories = db.session.query(Category)
        return render_template('admin/newCategory.html', categories = categories)

@app.route('/admin/categories/<int:category_id>/edit/', methods=['GET', 'POST'])
@basic_auth.required
def editCategory(category_id):
    editedCategory = db.session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        db.session.add(editedCategory)
        db.session.commit()
        return redirect(url_for('admin/showCategories'))
    else:
        categories = db.session.query(Category)
        return render_template('editCategory.html', category = editedCategory, categories = categories)

@app.route('/admin/categories/<int:category_id>/delete/', methods=['GET', 'POST'])
@basic_auth.required
def deleteCategory(category_id):
    categoryToDelete = db.session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        db.session.delete(categoryToDelete)
        db.session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('admin/deleteCategory.html', category = categoryToDelete)


## Routes for Items

@app.route('/admin/categories/<int:category_id>')
@app.route('/admin/categories/<int:category_id>/items/', methods = ['GET', 'POST'])
@basic_auth.required
def showItems(category_id):
    categories = db.session.query(Category)
    category = db.session.query(Category).filter_by(id=category_id).one()
    items = db.session.query(Item).filter_by(category_id=category_id)
    return render_template('admin/items.html', categories = categories, category=category, items=items, category_id=category_id)


@app.route('/admin/categories/<int:category_id>/items/new/', methods = ['GET', 'POST'])
@basic_auth.required
def newItem(category_id):
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                        description=request.form['description'],
                        price=request.form['price'],
                        photo_filename = photos.save(request.files['photo']),
                        category_id=category_id)
        db.session.add(newItem)
        db.session.commit()
        return redirect(url_for('showItems', category_id = category_id))
    else:
        categories = db.session.query(Category)
        return render_template('admin/newItem.html', category_id = category_id, categories = categories)

@app.route('/admin/categories/<int:category_id>/items/<int:item_id>/edit/', methods = ['GET', 'POST'])
@basic_auth.required
def editItem(category_id, item_id):
    editedItem = db.session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['name']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['photo']:
            editedItem.photo_filename = photos.save(request.files['photo'])
        db.session.add(editedItem)
        db.session.commit()
        return redirect(url_for('showItems',category_id = category_id))
    else:
        categories = db.session.query(Category)
        return render_template('admin/editItem.html', category_id = category_id, item = editedItem, categories = categories)

@app.route('/admin/categories/<int:category_id>/items/<int:item_id>/delete/', methods = ['GET', 'POST'])
@basic_auth.required
def deleteItem(category_id, item_id):
    itemToDelete = db.session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('admin/deleteItem.html', item = itemToDelete)


## API Endpoints

@app.route('/api/')
@app.route('/api/categories/')
def apiShowCategories():
    categories = db.session.query(Category)
    return jsonify(categories=[c.serialize for c in categories])

@app.route('/api/categories/<int:category_id>/')
@app.route('/api/categories/<int:category_id>/items/', methods = ['GET'])
def apiShowItems(category_id):
    category = db.session.query(Category).filter_by(id=category_id).one()
    items = db.session.query(Item).filter_by(category_id=category_id)
    return jsonify(category=category.name,items=[i.serialize for i in items])


if __name__ == '__main__':
    app.debug = True
    app.run()
