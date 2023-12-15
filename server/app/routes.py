from flask import request, jsonify, send_file
from functools import wraps
import jwt
from app import app
from app.models import User 
from app.utils import jwt_required, login
from flask import request, jsonify
from app import app, db , mongo
from app.models import User
from app.scan_folder import scan_folder
from bson import json_util
from app.prediction import *
from bson import ObjectId
from pymongo import UpdateOne

@app.route('/protected')
@jwt_required
def protected_resource(current_user_id):
    user = User.query.get(current_user_id)
    if user:
        return jsonify({'message': 'You have access to this protected resource', 'user': user.as_dict()})
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/auth', methods=['POST'])
def auth():
    print("auth")
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = login(data)
    if user:
        token = jwt.encode({'identity': user.id}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'access_token': token.decode('UTF-8')})
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


@app.route('/image_from_server',methods=['POST'])
@jwt_required
def main_image_from_server(current_user_id):
    print('image_from_server')
    filepath = request.get_json()
    print('filepath encore ',filepath['filepath'])
    filepath = os.path.join(os.getcwd(), filepath['filepath'])
    return send_file(filepath, mimetype='image/jpeg')


#verifie si la bdd user est vide / True = vide / False = les compte existe deja
@app.route('/check_db_empty')
def check_db_empty():
    print('check_db_empty')
    user_count = User.query.count() 
    if user_count == 0:
        return jsonify({'message': 'True'})
    else:
        return jsonify({'message': 'False'})


#cree un user "admin" si la bdd est vide
# donnee atendu
# json =  data = {
#             'username': 'user',
#             'password': 'password'
#         }
@app.route('/first_user', methods=['POST'])
def first_user():
    print('first_user')
    user_count = User.query.count()
    if user_count == 0:
        data = request.get_json()
        print("data=",data)
        # Check if the required fields are present in the request
        if 'username' not in data or 'password' not in data :
            return jsonify({'message': 'Incomplete data. Please provide username, password'}), 400

        # Create a new user
        new_user = User(username=data['username'], password=data['password'], role='admin')
        user_name = data['username']
        print("cree luser: ",user_name)
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        print('new uszer: ',new_user.as_dict())
        return jsonify({f'message': 'User created successfully', 'user': list({user_name})}), 201
    else:
        return jsonify({'message': 'bdd non vide'}), 400


#cree un user (only admin) 
# donner atendu en POST
# json =  data = {
#             'username': 'user',
#             'password': 'password',
#             'role': 'utilisateur' # ou 'admin'
#         }
@app.route('/create_user', methods=['POST'])
@jwt_required
def create_user(current_user_id):
    print("create_user")
    user = User.query.get(current_user_id)
    if user.as_dict()['role'] != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 401

    data = request.get_json()
    # Check if the required fields are present in the request
    if 'username' not in data or 'password' not in data or 'role' not in data:
        return jsonify({'message': 'Incomplete data. Please provide username, password, and role'}), 400

    # Check if the username is already taken
    if User.query.filter_by(username=data['username']).first(): 
        return jsonify({'message': 'Username already exists. Please choose a different username'}), 400

    # Create a new user
    new_user = User(username=data['username'], password=data['password'], role=data['role'])
    user_name = data['username']
    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return jsonify({f'message': 'User crated  successfully', 'user': list({user_name})}), 201


# suprime un user avec son user_id (only admin)
# /delete_user/1 pour l'user_id 1
@app.route('/delete_user', methods=['POST'])
@jwt_required
def delete_user(current_user_id):
    print('delete_user')
    current_user = User.query.get(current_user_id)
    if current_user.as_dict()['role'] != "admin":
        return jsonify({'message': 'Unauthorized access'}), 401

    data = request.get_json() 
    user_id = data['id'] 
    # Check if the user to be deleted exists
    user_to_delete = User.query.get(user_id)
    if not user_to_delete:
        return jsonify({'message': 'User not found'}), 404

    # Delete the user from the database
    db.session.delete(user_to_delete)
    db.session.commit()

    return jsonify({'message': f'User deleted successfully user : {user_to_delete.username}'}), 201


# changer le role d'un user avec son user_id (only admin)
# /change_role/1 pour l'user_id 1
# data atnedu en POST
# data = {
#     'role': 'admin'
# }
@app.route('/change_role', methods=['POST'])
@jwt_required
def change_user_role(current_user_id):
    print('change_role')
    current_user = User.query.get(current_user_id)
    if current_user.as_dict()['role'] != "admin":
        print("pas autoriser")
        return jsonify({'message': 'Unauthorized access'}), 401
    
    data = request.get_json() 
    user_id = data['id']
    
    # Check if the use r to be modified exists
    user_to_modify = User.query.get(user_id)
    print("user to modify: ",user_to_modify)
    if not user_to_modify:
        return jsonify({'message': 'User not found'}), 404

    # Parse the new role from the request data
    data = request.get_json()
    new_role = data.get('role')

    # Check if the new role is valid
    if new_role not in ['admin', 'utilisateur']:
        return jsonify({'message': 'Invalid role. Role must be "admin" or "utilisateur"'}), 400

    # Change the user's role and commit the changes to the database
    user_to_modify.role = new_role
    db.session.commit()
    return jsonify({'message': f'User role c hanged to {new_role} successfully'}), 201 


@app.route('/all_user', methods=['POST'])
@jwt_required
def all_user(current_user_id):
    print('all_user')
    current_user = User.query.get(current_user_id)
    if current_user.as_dict()['role'] != "admin":
        print("pas autoriser")
        return jsonify({'message': 'Unauthorized access'}), 401
    
    all_users = User.get_all_users() 
    users_list = [user.as_dict() for user in all_users]
    print(users_list)
    return jsonify({'user': users_list}), 201


@app.route('/recharger_la_bdd', methods=['POST'])
@jwt_required
def recharger_la_bdd():
    print('recharger_la_bdd')
    image_files = scan_folder()
    print("image:",image_files)
    image_detecte=len(image_files)
    image_eregistrer=0
    for image in image_files:
        print("image detecter:",image)
        existing_image = mongo.db.images.find_one(image) 
        if existing_image is None:
            image_eregistrer = image_eregistrer + 1
            print("image ajouté:",image)
            mongo.db.images.insert_one(image)
    return f'{image_eregistrer} Images ajoutées à la  base de données MongoDB sur un total de {image_detecte} images' 


#afiches toute les image de la bdd mongodb
@app.route('/find_all_image', methods=['POST']) 
@jwt_required
def find_all_image(current_user_id): 
    print('find_all_image')
    resultat = mongo.db.images.find({})
    images_list = [{**doc, '_id': str(doc['_id'])} for doc in resultat]
    response = {"result": images_list}
    return jsonify(response)


@app.route('/user_name', methods=['POST'])
@jwt_required
def user(current_user_id):
    print("user_name")
    user = User.query.get(current_user_id)
    print('user_name',user.as_dict())  
    return jsonify(user.as_dict()), 201

@app.route('/user', methods=['POST'])
@jwt_required
def user_id(current_user_id):
    print('user')
    
    data = request.get_json() 
    user_id = data['id']
    user = User.query.get(user_id) 
    user_data = {
            'id': user.id,
            'username': user.username,
            'role': user.role,
        }
    return jsonify({ 'user': user_data}), 201


@app.route('/affiche_image',methods=['POST'])
@jwt_required
def affiche_image(current_user_id):
    print('affiche_image')
    image_id = request.get_json()
    print(image_id)
    image_id = ObjectId(image_id)
    # Récupérer l'élément de la base de données par son _id
    resultat = mongo.db.images.find_one({'_id': image_id}) 
    # Vérifier si l'élément a été trouvé
    if resultat:
        # Récupérer les données d'image à partir de l'élément
        resultat['_id'] = str(resultat['_id'])
        response = {"result": resultat}
        # Faites quelque chose avec les données de l'image (par exemple, afficher dans un modèle)
        return jsonify(response)
    else:
        # Gérer le cas où l'élément n'a pas été trouvé
        return "Image not found", 404


@app.route('/load_images',methods=['POST'])
@jwt_required
def load_images(current_user_id):
    print("load_images")
    filepath = request.get_json()
    image_annotation = PredictorLabeler().predict_single_image(filepath['filepath'])
    return jsonify({'images': image_annotation})
 

 #data
 #{id: id ,regions[]}
@app.route('/post_resultat',methods=['POST'])
@jwt_required
def post_resultat(current_user_id):
    print("post_resultat") 
    data = request.get_json()
    image_id = ObjectId(data['id']) 
    print(data['size']) 
    user = User.query.get(current_user_id)
    print('user_name',user.as_dict())  
    print('user_name',user.as_dict()['username'])
    print('id_user',user.as_dict()['id']) 
    # element_to_update = mongo.db.images.find_one({"_id":image_id})
    change_label = {'$set': {'labels': True}} 
    add_region = {'$set': {'regions': data['regions']}}
    add_size = {'$set': {'size': data['size']}}
    add_id_user = {'$set': {'username': user.as_dict()['username']}}
    add_username_user = {'$set': {'user_id':user.as_dict()['id']}}
     
    updates = [
        UpdateOne({'_id': image_id}, add_region),
        UpdateOne({'_id': image_id}, change_label),
        UpdateOne({'_id': image_id}, add_id_user),
        UpdateOne({'_id': image_id}, add_username_user),
        UpdateOne({'_id': image_id}, add_size)
    ]

    result = mongo.db.images.bulk_write(updates)
    print(result) 
    return jsonify({'status': 'success', 'message': 'File uploaded successfully'}) 