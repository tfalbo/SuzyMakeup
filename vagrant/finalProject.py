from flask import Flask
app = Flask(__name__)


## Routes for Categories

@app.route('/categories')
def showCategories():
    return "This page will show all categories"

@app.route('/categories/new')
def newCategory():
    return "This page creates a new category"

@app.route('/categories/<int:category_id>/edit')
def editCategory(category_id):
    return "This page edits category {}".format(category_id)

@app.route('/categories/<int:category_id>/delete')
def deleteCategory(category_id):
    return "This page deletes category {}".format(category_id)

## Routes for Items

@app.route('/categories/<int:category_id>/items')
def showItems(category_id):
    return "This page will show all items of category {}".format(category_id)

@app.route('/categories/<int:category_id>/items/new')
def newItem(category_id):
    return "This page creates a new item for category {}".format(category_id)

@app.route('/categories/<int:category_id>/items/<int:item_id>/edit')
def editItem(category_id, item_id):
    return "This page edits item {} of category {}".format(item_id,category_id)

@app.route('/categories/<int:category_id>/items/<int:item_id>/delete')
def deleteItem(category_id, item_id):
    return "This page deletes item {} of category {}".format(item_id,category_id)



if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
