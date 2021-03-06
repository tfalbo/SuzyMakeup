import os
import random
import string
import httplib2
import json
import requests
from flask import Flask, render_template, request, flash
from flask import redirect, url_for, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item
from flask_uploads import UploadSet, IMAGES, configure_uploads
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('/vagrant/catalog/client_secrets.json', 'r').
    read())['web']['client_id']
APPLICATION_NAME = "Suzy Makeup"

engine = create_engine('sqlite:///suzymakeup.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Photo Setup

app.config['UPLOADS_DEFAULT_DEST'] = "static/img"
app.config['UPLOADS_DEFAULT_URL'] = "http://0.0.0.0:5000/static/img/"
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)


# Routes

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            '/vagrant/catalog/client_secrets.json', scope='')
        print(oauth_flow)
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])

    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += """ "style = "width: 300px; height: 300px;border-radius:
                150px;-webkit-border-radius: 150px;-moz-border-radius:
                150px;"> """
    print("done!")
    return output

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    token_url = 'https://accounts.google.com/o/oauth2/revoke?token='
    url = token_url + login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/categories/')
def index():
    categories = session.query(Category)
    items = session.query(Item)
    return render_template('index.html', categories=categories, items=items)


@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/items')
def indexCategory(category_id):
    categories = session.query(Category)
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id)
    return render_template(
        'category.html',
        categories=categories,
        category=category,
        items=items)


@app.route('/categories/<int:category_id>/items/<int:item_id>/')
def indexItem(category_id, item_id):
    categories = session.query(Category)
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('item.html', categories=categories, item=item)


# Admin route

@app.route('/admin/')
@app.route('/admin/categories/')
def showCategories():
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category)
    return render_template(
        'admin/categories.html',
        categories=categories,
        login_session=login_session)


@app.route('/admin/categories/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        categories = session.query(Category)
        return render_template(
            'admin/newCategory.html',
            categories=categories,
            login_session=login_session)


@app.route(
    '/admin/categories/<int:category_id>/edit/',
    methods=['GET', 'POST'])
def editCategory(category_id):
    editedCategory = session.query(Category).filter_by(id=category_id).one()

    # Check for user authentication
    if 'username' not in login_session:
        return redirect('/login')

    # Check for user authorization
    if editedCategory.user_id != login_session['user_id']:
        flash('You are not the owner of {}'.format(editedCategory.name))
        return redirect(url_for('showItems', category_id=editedCategory.id))

    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        session.add(editedCategory)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        categories = session.query(Category)
        return render_template(
            'admin/editCategory.html',
            category=editedCategory,
            categories=categories,
            login_session=login_session)


@app.route(
    '/admin/categories/<int:category_id>/delete/',
    methods=['GET', 'POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()

    # Check for user authentication
    if 'username' not in login_session:
        return redirect('/login')

    # Check for user authorization
    if categoryToDelete.user_id != login_session['user_id']:
        flash('You are not the owner of {}'.format(categoryToDelete.name))
        return redirect(url_for('showItems', category_id=categoryToDelete.id))

    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template(
            'admin/deleteCategory.html',
            category=categoryToDelete)


# Routes for Items

@app.route('/admin/categories/<int:category_id>')
@app.route(
    '/admin/categories/<int:category_id>/items/',
    methods=['GET', 'POST'])
def showItems(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category)
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id)
    return render_template(
        'admin/items.html',
        categories=categories,
        category=category,
        items=items,
        category_id=category_id,
        login_session=login_session)


@app.route(
    '/admin/categories/<int:category_id>/items/new/',
    methods=['GET', 'POST'])
def newItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            photo_filename=photos.save(request.files['photo']),
            category_id=category_id,
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('showItems', category_id=category_id))
    else:
        categories = session.query(Category)
        return render_template(
            'admin/newItem.html',
            category_id=category_id,
            categories=categories,
            login_session=login_session)


@app.route(
    '/admin/categories/<int:category_id>/items/<int:item_id>/edit/',
    methods=['GET', 'POST'])
def editItem(category_id, item_id):
    editedItem = session.query(Item).filter_by(id=item_id).one()

    # Check for user authentication
    if 'username' not in login_session:
        return redirect('/login')

    # Check for user authorization
    if editedItem.user_id != login_session['user_id']:
        flash('You are not the owner of {}'.format(editedItem.name))
        return redirect(url_for('showItems',
                                category_id=editedItem.category_id))

    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['name']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['photo']:
            editedItem.photo_filename = photos.save(request.files['photo'])
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showItems', category_id=category_id))
    else:
        categories = session.query(Category)
        return render_template(
            'admin/editItem.html',
            category_id=category_id,
            item=editedItem,
            categories=categories,
            login_session=login_session)


@app.route(
    '/admin/categories/<int:category_id>/items/<int:item_id>/delete/',
    methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    itemToDelete = session.query(Item).filter_by(id=item_id).one()

    # Check for user authentication
    if 'username' not in login_session:
        return redirect('/login')

    # Check for user authorization
    if itemToDelete.user_id != login_session['user_id']:
        flash('You are not the owner of {}'.format(itemToDelete.name))
        return redirect(url_for('showItems',
                        category_id=itemToDelete.category_id))

    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('admin/deleteItem.html', item=itemToDelete)


# API Endpoints

@app.route('/api/')
@app.route('/api/categories/')
def apiShowCategories():
    categories = session.query(Category)
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/api/categories/<int:category_id>/')
@app.route('/api/categories/<int:category_id>/items/', methods=['GET'])
def apiShowItems(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id)
    return jsonify(category=category.name, items=[i.serialize for i in items])


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
