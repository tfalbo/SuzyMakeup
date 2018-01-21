from flask import Flask
from flask import render_template
app = Flask(__name__)


#Fake Categories
category = {'name': 'Face', 'id': '1'}

categories = [{'name': 'Face', 'id': '1'}, {'name':'Eyes', 'id':'2'},{'name':'Lips', 'id':'3'}]


#Fake Category Items
items = [ {'name':'Foundation', 'description':'made with fresh cheese', 'price':'$5.99', 'id':'1'},
        {'name':'Blush','description':'made with Dutch Chocolate', 'price':'$3.99', 'id':'2'},
        {'name':'Powder', 'description':'with fresh organic vegetables','price':'$5.99', 'id':'3'},
        {'name':'Primer', 'description':'with lemon','price':'$.99', 'id':'4'},
        {'name':'Bronzer', 'description':'creamy dip with fresh spinach','price':'$1.99','id':'5'} ]

item =  {'name':'Foundation','description':'made with fresh cheese','price':'$5.99'}

## Routes for Categories

@app.route('/')
@app.route('/categories')
def showCategories():
    return render_template('categories.html', categories = categories)

@app.route('/categories/new')
def newCategory():
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
