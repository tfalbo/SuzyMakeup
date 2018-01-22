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
@app.route('/categories')
def showCategories():
    categories = session.query(Category)
    return render_template('categories.html', categories = categories)

@app.route('/categories/new', methods=['GET', 'POST'])
def newCategory():
    if request == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('/'))
    else:
        return render_template('newCategory.html')

@app.route('/categories/<int:category_id>/edit')
def editCategory(category_id):
    return render_template('editCategory.html', category = category)

@app.route('/categories/<int:category_id>/delete')
def deleteCategory(category_id):
    return render_template('deleteCategory.html', category = category)

## Routes for Items

@app.route('/categories/<int:category_id>')
@app.route('/categories/<int:category_id>/items')
def showItems(category_id):
    return render_template('items.html', category = category, items = items)


@app.route('/categories/<int:category_id>/items/new')
def newItem(category_id):
    return render_template('newItem.html', category = category)

@app.route('/categories/<int:category_id>/items/<int:item_id>/edit')
def editItem(category_id, item_id):
    return render_template('editItem.html', category = category, item = item)

@app.route('/categories/<int:category_id>/items/<int:item_id>/delete')
def deleteItem(category_id, item_id):
    return render_template('deleteItem.html', category = category, item = item)



if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
