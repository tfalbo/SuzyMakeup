from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item

app = Flask(__name__)

engine = create_engine('sqlite:///suzymakeup.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/categories/')
def showCategories():
    categories = session.query(Category)
    return render_template('categories.html', categories = categories)

@app.route('/categories/new/', methods=['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')

@app.route('/categories/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    editedCategory = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        session.add(editedCategory)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html', category = editedCategory)

@app.route('/categories/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html', category = categoryToDelete)


## Routes for Items

@app.route('/categories/<int:category_id>')
@app.route('/categories/<int:category_id>/items/', methods = ['GET', 'POST'])
def showItems(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id)
    return render_template('items.html', category=category, items=items, category_id=category_id)


@app.route('/categories/<int:category_id>/items/new/', methods = ['GET', 'POST'])
def newItem(category_id):
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                        description=request.form['description'],
                        price=request.form['price'],
                        category_id=category_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('showItems', category_id = category_id))
    else:
        return render_template('newItem.html', category_id = category_id)

@app.route('/categories/<int:category_id>/items/<int:item_id>/edit/', methods = ['GET', 'POST'])
def editItem(category_id, item_id):
    editedItem = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['name']
        if request.form['price']:
            editedItem.price = request.form['price']
        session.add(editedItem)
        session.commit()
        return redirect(url_for(showItems),category_id = category_id)
    else:
        return render_template('editItem.html', category_id = category_id, item = editedItem)

@app.route('/categories/<int:category_id>/items/<int:item_id>/delete/', methods = ['GET', 'POST'])
def deleteItem(category_id, item_id):
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('deleteItem.html', item = itemToDelete)



if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
