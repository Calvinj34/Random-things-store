from flask import render_template, request, redirect, url_for, flash, Blueprint
from ..forms import UserCreationForm, loginform, ItemSubmitForm
from ..models import User, Item, Cart
from flask_login import login_user, logout_user, current_user, login_required
from flask_httpauth import HTTPBasicAuth
from flask_httpauth import HTTPTokenAuth

basic_auth= HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verifypassword(username, password):
    user = User.query.filter_by(username = username).first()
    if user: 
        if user.password == password:
            return user

@token_auth.verify_token
def verifyToken(token):
    user = User.query.filter_by(token=token).first()
    if user:
        return user

api = Blueprint('api', __name__)

@api.route('/api/shop', methods=["GET", "POST"])
def shopPageAPI():

    items = Item.query.all()

    new_items = []
    for i in items:
        new_items.append(i.to_dict())
    
    return {
        'status': 'ok',
        'totalResults': len(items),
        'items': [i.to_dict() for i in items]
    }

@api.post('/api/login')
@basic_auth.login_required
def getToken():
    user = basic_auth.current_user()
    return {
        'username': user.username,
        'token' : user.token, 
        'status': 'ok'


    }

@api.route('/api/signup', methods=["POST"])
def signUpPageAPI():
    data = request.json
   
       
    username = data['username']
    email = data['email']
    password = data['password']
    


    user = User(username, email, password)

    user.saveToDB()

    return {
        'status': 'ok',
        'message': "Succesffuly created an account!"
    }

@api.route('/api/shop/<int:item_id>', methods=["GET"])
def singleItem(item_id):

    item = Item.query.get(item_id)

    return item.to_dict()

@api.route('/api/addtocart/<int:item_id>', methods=["GET", "POST"])
@token_auth.login_required
def addToCart(item_id):
    
    transaction = Cart(item_id, token_auth.current_user().id)
    transaction.saveToDB()

    return {
        'status': 'ok',
        'message': 'Item successfully added to cart.'
    } 

@api.route('/api/mycart', methods=["GET", "POST"])
@token_auth.login_required
def myCart():

    my_cart = Cart.query.filter_by(customer_id = token_auth.current_user().id).all()
    my_cart = [Item.query.get(c.item_id).to_dict() for c in my_cart ]

    

    total = 0
    for item in my_cart:
        total += float(item['price'])

    return {
        'status': 'ok',
        'my_cart': my_cart,
        'total': total
    }

@api.route('/api/cart/<int:item_id>/delete', methods=["GET", "POST"])
@login_required
def deleteItem(item_id):
    item = Cart.query.get(item_id)

    item.deleteFromDB()

    return {
        'status': 'ok',
        'message': 'Item successfully deleted from cart'
    }

@api.route('/api/cart/deleteall', methods=["GET", "POST"])
@login_required
def deleteAll():

    cart = Cart.query.all()
    for item in cart:
        item.deleteFromDB()

    return {
        'status': 'ok',
        'message': 'Successfully deleted all items from cart.'
    }