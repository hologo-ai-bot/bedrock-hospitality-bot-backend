from flask import Blueprint, jsonify,  request
from main.services.client_service import ClientService

client_blueprint = Blueprint('client', __name__)

client_service = ClientService()

@client_blueprint.route('/')
def index():
    return 'Token Controller Working'

@client_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('fname')
    last_name = data.get('lname')
    tkns_remaining = data.get('tokens')

    if not username or not email or not password or not first_name or not last_name :
        return jsonify({"error": "Invalid data provided"}), 400
    try:
        response = client_service.clientRegister(username,email,password,first_name,last_name,tkns_remaining )
        if response is not None:
            return jsonify("Success ",response.to_json()), 201
        else:
            return jsonify({"error": "Username already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@client_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')    

    if not email or not password :
        return jsonify({"error": "Invalid data provided", }), 400
    try:
        response = client_service.clientLogin(email,password)

        if response is not None:
            if response:
                return jsonify({"success": "login success"}), 200
            else:
                return jsonify({"error": "Invalid email or password"}), 401
        else:
            return jsonify({"error": "User doesn't exist"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500    

@client_blueprint.route('/<username>', methods=['GET'])
def get_user(username):
    try:
        response = client_service.returnClient(username)
        if response is None:
            return jsonify({"error": "User not found"}), 404
        else:
            return jsonify(response.to_json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@client_blueprint.route('/token/<username>', methods=['GET'])
def get_token(username):
    try:
        response = client_service.returnTokenInfo(username )
        if response is None:
            return jsonify({"error": "User not found"}), 404
        else:
            return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@client_blueprint.route('/token/update', methods=['PUT'])
def update_token():
    try:
        data = request.json
        username = data.get('username')
        add_tkn = data.get('add_tkn')
        if not username or add_tkn is None :
            return jsonify({"error": "Invalid input data"}), 400
        response = client_service.updateClientToken(username, add_tkn)
        if response is None:
            return jsonify({"error": "User not found"}), 404                   
        else:
            return jsonify({"success": "Token update success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@client_blueprint.route('/delete', methods=['Delete'])
def delete_client():
    try:
        data = request.json
        clientId = data.get('clientId')
        if clientId is None:
            return jsonify({"error": "Invalid input data"}), 400
        response = client_service.deleteClient(clientId)
        if response is None:
            return jsonify({"error": "User not found"}), 404
        else:
            return jsonify({"success": "client deletion success"}), 200 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

