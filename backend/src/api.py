import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# CORS Headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,PATCH,POST,DELETE,OPTIONS')
    return response

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
# @requires_auth('get:drinks')
def get_short_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        short_drinks = [drink.short() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": short_drinks
            })
    except:
        abort(422)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
# @app.route('/drinks-detail', methods=['GET'])
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        drinks_long = [drink.long() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drinks_long
            })
    except:
        abort(422)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    # checking if the method is POST
    if request.method == 'POST':
        # get data
        try:
            body = request.get_json()
            # print('posted drink body:', body)
            if not ('title' in body and 'recipe' in body):
                abort(422)
            title = body.get('title', None)
            # print('new title', title)
            recipe = body.get('recipe', None)
            dumped_recipe = json.dumps(recipe)
            # print('new recipe', dumped_recipe)
            
            drink = Drink(
                title = title,
                recipe = dumped_recipe
                )
            drink.insert()       
            # print('drink succesfully posted',drink)
            return jsonify({
                'success' : True,
                'drinks' :  [drink.long()]
            })
        except:
            abort(422)
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        print('selected drink',drink)
        if not drink:
            abort(404)
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)
        dumped_recipe = json.dumps(recipe)
        # print('title', title)
        # print('recipe', recipe)
        if title:
            drink.title = title
            print('upd title', drink.title)
        if recipe:
            drink.recipe = dumped_recipe
            print('upd recipe', drink.recipe)
        print('patched drink',drink)
        drink.update()
        # formated_drink = Drink.query.all()
        formated_drink = [drink.long() for drink in Drink.query.all()]
        return jsonify({
            "success": True,
            "drinks" : formated_drink
            })
    except:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    if request.method == 'DELETE':
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if not drink:
            abort(404)   
        try:
            drink.delete()
            return jsonify({
                "success": True,
                "deleted_drink": drink.id
            })
        except:
            abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(401)
def Unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "user not Authenticated"
    }), 401

@app.errorhandler(403)
def Forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "resource forbidden"
    }), 403  
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def handling_AuthError(e):
    return jsonify({
       "success": False,
       "error": e.status_code,
       "message": e.error
       }), e.status_code